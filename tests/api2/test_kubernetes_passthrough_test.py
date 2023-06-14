import pytest
from pytest_dependency import depends

from middlewared.test.integration.utils import call
from middlewared.service_exception import CallError
from middlewared.client.client import ClientException
from auto_config import ha, pool_name

APP_NAME = 'syncthing'
IS_HA = pytest.mark.skipif(not ha, reason='Only applicable on HA systems')


@pytest.mark.dependency(name='default_kubernetes_cluster')
def test_01_default_kubernetes_cluster(request):
    config = call('kubernetes.update', {'passthrough_mode': False, 'pool': pool_name}, job=True)
    assert config['passthrough_mode'] is False


@pytest.mark.dependency(name='install_chart_release')
def test_02_install_chart_release(request):
    depends(request, ['default_kubernetes_cluster'])
    payload = {'catalog': 'TRUENAS', 'item': 'syncthing', 'release_name': APP_NAME, 'train': 'charts'}
    call('chart.release.create', payload, job=True)
    assert call('chart.release.get_instance', APP_NAME)['name'] == APP_NAME


def test_03_ip_rules_in_default_mode(request):
    depends(request, ['default_kubernetes_cluster'])
    assert len(call('kubernetes.iptable_rules')) > 0


@IS_HA
@pytest.mark.dependency(name='setup_kubernetes_passthrough_mode')
def test_04_kubernetes_passthrough_mode(request):
    depends(request, ['default_kubernetes_cluster'])
    config = call('kubernetes.update', {'passthrough_mode': True}, job=True)
    assert config['passthrough_mode'] is True


@IS_HA
def test_05_validate_kubernetes_passthrough_mode(request):
    depends(request, ['setup_kubernetes_passthrough_mode'])
    with pytest.raises(CallError) as e:
        call('kubernetes.validate_k8s_setup')
        assert e == 'Kubernetes operations are not allowed with passthrough mode enabled'


@IS_HA
def test_06_query_chart_release(request):
    depends(request, ['install_chart_release', 'setup_kubernetes_passthrough_mode'])
    assert call('chart.release.query') == []


@IS_HA
def test_07_install_chart_release_app(request):
    depends(request, ['setup_kubernetes_passthrough_mode'])
    payload = {'catalog': 'TRUENAS', 'item': 'test-syncthing', 'release_name': 'syncthing', 'train': 'charts'}
    with pytest.raises(ClientException) as e:
        call('chart.release.create', payload, job=True)
        assert e == 'Kubernetes operations are not allowed with passthrough mode enabled'


@IS_HA
def test_08_create_kubernetes_backup_restore(request):
    depends(request, ['setup_kubernetes_passthrough_mode'])
    with pytest.raises(ClientException) as e:
        call('kubernetes.backup_chart_releases', 'test_backup', job=True)
        assert e == 'Kubernetes operations are not allowed with passthrough mode enabled'


@IS_HA
def test_09_ip_rules_in_passthrough_mode(request):
    depends(request, ['setup_kubernetes_passthrough_mode'])
    assert len(call('kubernetes.iptable_rules')) == 0


@IS_HA
@pytest.mark.dependency(name='remove_kubernetes_passthrough_mode')
def test_10_remove_kubernetes_passthrough_mode(request):
    depends(request, ['setup_kubernetes_passthrough_mode'])
    call('kubernetes.update', {'passthrough_mode': False}, job=True)


@IS_HA
def test_11_validate_cluster(request):
    depends(request, ['remove_kubernetes_passthrough_mode'])
    assert call('kubernetes.validate_k8s_setup') is True
