import pytest

from middlewared.service_exception import CallError
from middlewared.test.integration.assets.account import user
from middlewared.test.integration.utils import call


def test_remote_ssh_semiautomatic_setup_invalid_homedir():
    with user({
        "username": "admin",
        "full_name": "admin",
        "group_create": True,
        "home_create": False,
        "password": "test1234",
    }):
        credential = call("keychaincredential.create", {
            "name": "key",
            "type": "SSH_KEY_PAIR",
            "attributes": call("keychaincredential.generate_ssh_key_pair"),
        })
        try:
            token = call("auth.generate_token")
            with pytest.raises(CallError) as ve:
                call("keychaincredential.remote_ssh_semiautomatic_setup", {
                    "name": "localhost",
                    "url": "http://localhost",
                    "token": token,
                    "username": "admin",
                    "private_key": credential["id"],
                })

            assert "make sure that home directory for admin user on the remote system exists" in ve.value.errmsg
        finally:
            call("keychaincredential.delete", credential["id"])
