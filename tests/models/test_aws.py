"Test AWS models."
import os
from unittest import mock
import pytest

from awsync.models.aws import Credentials, Region


class TestCredentials:
    "Test Credentials class."

    @mock.patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "TESTACCESSKEY",
            "AWS_SECRET_ACCESS_KEY": "TESTSECRETACCESSKEY",
            "AWS_SESSION_TOKEN": "TESTSESSIONTOKEN",
        },
        clear=True,
    )
    def test_credentials_from_environment(self) -> None:
        "Test Credentials.from_environment() static constructor reads values from env vars."
        assert Credentials.from_environment() == Credentials(
            access_key_id="TESTACCESSKEY",
            secret_access_key="TESTSECRETACCESSKEY",
            session_token="TESTSESSIONTOKEN",
        )

    @mock.patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_credentials_from_environment_unset(self) -> None:
        "Test Credentials.from_environment() raises exception when env vars not set."
        with pytest.raises(KeyError):
            Credentials.from_environment()

    def test_credentials_secret_values(self) -> None:
        "Test that secret_access_key is not leaked in string representation."
        assert (
            str(
                Credentials(
                    access_key_id="TESTACCESSKEY",
                    secret_access_key="TESTSECRETACCESSKEY",
                    session_token="TESTSESSIONTOKEN",
                )
            )
            == "Credentials(access_key_id='TESTACCESSKEY', session_token='TESTSESSIONTOKEN')"
        )


class TestRegion:
    "Test Region StrEnum."

    def test_regions(self) -> None:
        "Test that region enum contains all expected regions."
        assert [str(region) for region in Region] == [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "af-south-1",
            "ap-east-1",
            "ap-south-2",
            "ap-southeast-3",
            "ap-southeast-4",
            "ap-south-1",
            "ap-northeast-3",
            "ap-northeast-2",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ca-central-1",
            "ca-west-1",
            "eu-central-1",
            "eu-west-1",
            "eu-west-2",
            "eu-south-1",
            "eu-west-3",
            "eu-south-2",
            "eu-north-1",
            "eu-central-2",
            "il-central-1",
            "me-south-1",
            "me-central-1",
            "sa-east-1",
        ]
