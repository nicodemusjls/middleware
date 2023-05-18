from middlewared.schema import accepts, Bool, Dict, List, Ref, returns, Str
from middlewared.service import filterable, filterable_returns, Service
from middlewared.utils import filter_list


class AppService(Service):

    class Config:
        cli_namespace = 'app'

    @filterable
    @filterable_returns(Ref('available_apps'))
    async def latest(self, filters, options):
        """
        Retrieve latest updated apps.
        """
        return filter_list(
            await self.middleware.call(
                'app.available', [
                    ['last_update', '!=', None], ['name', '!=', 'ix-chart'],
                ], {'order_by': ['-last_update']}
            ), filters, options
        )

    @filterable
    @filterable_returns(Dict(
        'available_apps',
        Bool('healthy', required=True),
        Bool('installed', required=True),
        List('categories', required=True),
        List('maintainers', required=True),
        List('tags', required=True),
        List('screenshots', required=True, items=[Str('screenshot')]),
        List('sources', required=True, items=[Str('source')]),
        Str('name', required=True),
        Str('title', required=True),
        Str('description', required=True),
        Str('app_readme', required=True),
        Str('location', required=True),
        Str('healthy_error', required=True, null=True),
        Str('home', required=True),
        Str('last_update', required=True),
        Str('latest_version', required=True),
        Str('latest_app_version', required=True),
        Str('icon_url', required=True),
        Str('train', required=True),
        Str('catalog', required=True),
        register=True
    ))
    def available(self, filters, options):
        """
        Retrieve all available applications from all configured catalogs.
        """
        if not self.middleware.call_sync('catalog.synced'):
            self.middleware.call_sync('catalog.initiate_first_time_sync')

        results = []
        installed_apps = [
            (app['chart_metadata']['name'], app['catalog'], app['catalog_train'])
            for app in self.middleware.call_sync('chart.release.query')
        ]

        for catalog in self.middleware.call_sync('catalog.query'):
            for train, train_data in self.middleware.call_sync('catalog.items', catalog['label']).items():
                if train not in catalog['preferred_trains']:
                    continue

                for app_data in train_data.values():
                    results.append({
                        'catalog': catalog['label'],
                        'installed': (app_data['name'], catalog['label'], train) in installed_apps,
                        'train': train,
                        **app_data,
                    })

        return filter_list(results, filters, options)

    @accepts()
    @returns(List(items=[Str('category')]))
    async def categories(self):
        """
        Retrieve list of valid categories which have associated applications.
        """
        return sorted(list(await self.middleware.call('catalog.retrieve_mapped_categories')))

    @accepts(Str('app_name'), Str('catalog'), Str('train'))
    @returns(List(items=[Ref('available_apps')]))
    def similar(self, app_name, catalog, train):
        """
        Retrieve applications which are similar to `app_name`.
        """
        available_apps = self.available()
        app = filter_list(
            available_apps, [['name', '=', app_name], ['catalog', '=', catalog], ['train', '=', train]], {'get': True}
        )
        similar_apps = []
        for to_check_app in available_apps:
            if all(to_check_app[k] == app[k] for k in ('name', 'catalog', 'train')):
                continue

            for key in ('categories', 'tags'):
                if set(app[key]).intersection(to_check_app[key]):
                    similar_apps.append(to_check_app)
                    break

        return similar_apps