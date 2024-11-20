import errno

import middlewared.sqlalchemy as sa

from middlewared.api import api_method
from middlewared.api.current import (
    DockerEntry, DockerStatusArgs, DockerStatusResult, DockerUpdateArgs, DockerUpdateResult,
    NvidiaStatusArgs, NvidiaStatusResult,
)
from middlewared.schema import ValidationErrors
from middlewared.service import CallError, ConfigService, job, private
from middlewared.utils.zfs import query_imported_fast_impl

from .state_utils import Status
from .utils import applications_ds_name
from .validation_utils import validate_address_pools


class DockerModel(sa.Model):
    __tablename__ = 'services_docker'

    id = sa.Column(sa.Integer(), primary_key=True)
    pool = sa.Column(sa.String(255), default=None, nullable=True)
    enable_image_updates = sa.Column(sa.Boolean(), default=True)
    nvidia = sa.Column(sa.Boolean(), default=False)
    cidr_v6 = sa.Column(sa.String(), default='fdd0::/64', nullable=False)
    address_pools = sa.Column(sa.JSON(list), default=[
        {'base': '172.17.0.0/12', 'size': 24},
        {'base': 'fdd0::/48', 'size': 64},
    ])


class DockerService(ConfigService):

    class Config:
        datastore = 'services.docker'
        datastore_extend = 'docker.config_extend'
        cli_namespace = 'app.docker'
        role_prefix = 'DOCKER'
        entry = DockerEntry

    @private
    async def config_extend(self, data):
        data['dataset'] = applications_ds_name(data['pool']) if data.get('pool') else None
        return data

    @api_method(DockerUpdateArgs, DockerUpdateResult)
    @job(lock='docker_update')
    async def do_update(self, job, data):
        """
        Update Docker service configuration.
        """
        old_config = await self.config()
        old_config.pop('dataset')
        config = old_config.copy()
        config.update(data)
        config['cidr_v6'] = str(config['cidr_v6'])

        verrors = ValidationErrors()
        if config['pool'] and not await self.middleware.run_in_thread(query_imported_fast_impl, [config['pool']]):
            verrors.add('docker_update.pool', 'Pool not found.')

        verrors.check()

        if config['address_pools'] != old_config['address_pools']:
            validate_address_pools(
                await self.middleware.call('interface.ip_in_use', {'static': True}), config['address_pools']
            )

        if old_config != config:
            address_pools_changed = any(config[k] != old_config[k] for k in ('address_pools', 'cidr_v6'))
            pool_changed = config['pool'] != old_config['pool']
            if pool_changed:
                # We want to clear upgrade alerts for apps at this point
                await self.middleware.call('app.clear_upgrade_alerts_for_all')

            if pool_changed or address_pools_changed:
                job.set_progress(20, 'Stopping Docker service')
                try:
                    await self.middleware.call('service.stop', 'docker')
                except Exception as e:
                    raise CallError(f'Failed to stop docker service: {e}')

                catalog_sync_job = None
                try:
                    catalog_sync_job = await self.middleware.call('docker.fs_manage.umount')
                except CallError as e:
                    # We handle this specially, if for whatever reason ix-apps dataset is not there,
                    # we don't make it fatal to change pools etc - however if some dataset other then
                    # boot pool is mounted at ix-apps dir, then we will error out as it's a problem
                    # and needs to be fixed before we can proceed
                    if e.errno != errno.ENOENT or await self.middleware.call('docker.fs_manage.ix_apps_is_mounted'):
                        raise
                finally:
                    if catalog_sync_job:
                        await catalog_sync_job.wait()

                await self.middleware.call('docker.state.set_status', Status.UNCONFIGURED.value)

            await self.middleware.call('datastore.update', self._config.datastore, old_config['id'], config)

            if pool_changed:
                job.set_progress(60, 'Applying requested configuration')
                await self.middleware.call('docker.setup.status_change')
            elif config['pool'] and address_pools_changed:
                job.set_progress(60, 'Starting docker')
                catalog_sync_job = await self.middleware.call('docker.fs_manage.mount')
                if catalog_sync_job:
                    await catalog_sync_job.wait()

                await self.middleware.call('service.start', 'docker')

            if not old_config['nvidia'] and config['nvidia']:
                await (
                    await self.middleware.call(
                        'nvidia.install',
                        job_on_progress_cb=lambda encoded: job.set_progress(
                            70 + int(encoded['progress']['percent'] * 0.2),
                            encoded['progress']['description'],
                        )
                    )
                ).wait(raise_error=True)

            if config['pool'] and address_pools_changed:
                job.set_progress(95, 'Initiating redeployment of applications to apply new address pools changes')
                await self.middleware.call(
                    'core.bulk', 'app.redeploy', [
                        [app['name']] for app in await self.middleware.call('app.query', [['state', '!=', 'STOPPED']])
                    ]
                )

        job.set_progress(100, 'Requested configuration applied')
        return await self.config()

    @api_method(DockerStatusArgs, DockerStatusResult, roles=['DOCKER_READ'])
    async def status(self):
        """
        Returns the status of the docker service.
        """
        return await self.middleware.call('docker.state.get_status_dict')

    @api_method(NvidiaStatusArgs, NvidiaStatusResult, roles=['DOCKER_READ'])
    async def nvidia_status(self):
        """
        Returns Nvidia hardware and drivers installation status.
        """
        return await self.nvidia_status_for_job()

    @private
    async def nvidia_status_for_job(self, job=None):
        if not await self.middleware.call('nvidia.present'):
            return {'status': 'ABSENT'}

        if job is None:
            jobs = await self.middleware.call('core.get_jobs', [['method', '=', 'nvidia.install']])
            if not jobs:
                return {'status': 'NOT_INSTALLED'}

            job = jobs[-1]

        match job['state']:
            case 'WAITING':
                return {'status': 'INSTALLING', 'progress': 0, 'description': 'Waiting for installation to begin...'}
            case 'RUNNING':
                return {
                    'status': 'INSTALLING',
                    'progress': job['progress']['percent'],
                    'description': job['progress']['description'],
                }
            case 'FAILED':
                return {'status': 'INSTALL_ERROR', 'error': job['error']}

        if await self.middleware.call('nvidia.installed'):
            return {'status': 'INSTALLED'}

        return {'status': 'NOT_INSTALLED'}


async def update_nvidia_status(middleware, event_type, args):
    if event_type == 'CHANGED' and args['fields']['method'] == 'nvidia.install':
        middleware.send_event(
            'docker.nvidia_status',
            'CHANGED',
            fields=await middleware.call('docker.nvidia_status_for_job', args['fields']),
        )


async def setup(middleware):
    middleware.event_register(
        'docker.nvidia_status',
        'Sent on Nvidia hardware and drivers installation status change.',
        roles=['DOCKER_READ'],
    )
    middleware.event_subscribe('core.get_jobs', update_nvidia_status)
