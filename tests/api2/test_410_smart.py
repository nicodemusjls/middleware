from time import sleep

import pytest

from functions import POST, PUT, GET
from auto_config import interface, dev_test
# comment pytestmark for development testing with --dev-test
pytestmark = pytest.mark.skipif(dev_test, reason='Skipping for test development testing')

not_real = any((interface == "vtnet0"), (interface == "em0"), ('enp0s' in interface))


def test_05_enable_smartd_service_at_boot():
    results = GET('/service/?service=smartd')
    smartid = results.json()[0]['id']

    results = PUT(f'/service/id/{smartid}/', {"enable": True})
    assert results.status_code == 200, results.text


def test_06_look_smartd_service_at_boot():
    results = GET('/service/?service=smartd')
    assert results.status_code == 200, results.text
    assert results.json()[0]["enable"] is True, results.text


# Read test below only on real hardware
if not_real is False:
    def test_07_starting_smartd_service():
        payload = {"service": "smartd"}
        results = POST("/service/start/", payload)
        assert results.status_code == 200, results.text
        sleep(1)

    def test_08_checking_to_see_if_smartd_service_is_running():
        results = GET('/service/?service=smartd')
        assert results.json()[0]["state"] == "RUNNING", results.text
