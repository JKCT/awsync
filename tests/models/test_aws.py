import os
from unittest import mock
from awsync.models.aws import Credentials, Region


class TestCredentials:
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
        assert Credentials.from_environment() == Credentials(
            access_key_id="TESTACCESSKEY",
            secret_access_key="TESTSECRETACCESSKEY",
            session_token="TESTSESSIONTOKEN",
        )


class TestRegion:
    def test_regions(self) -> None:
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
