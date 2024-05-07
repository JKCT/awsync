"Test module main function."
from datetime import UTC, datetime
from unittest.mock import patch

from awsync.models.aws import Credentials, Region
from awsync.models.http import Method, Scheme
from awsync import request

TEST_HOST = "www.test.com"
TEST_DATETIME = datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=UTC)
TEST_DATE = request.Date("20000101")
TEST_TIMESTAMP = request.Timestamp("20000101T000000Z")
TEST_CREDENTIALS = Credentials(
    access_key_id="TESTACCESSKEY",
    secret_access_key="TESTSECRETACCESSKEY",
    session_token="TESTSESSIONTOKEN",
)


class TestRequestHelpers:
    "Test the Request helper functions."

    def test_sha_hash(self) -> None:
        "Test _sha_hash (Hex(SHA256Hash(<VALUE>))."
        assert (
            request._sha_hash("")
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_empty_get_query_string(self) -> None:
        "Test _get_query_string with None value."
        assert request._get_query_string(None) == ""

    def test_get_query_string_sorting(self) -> None:
        "Test _get_query_string with multiple items and alphabetical key sorting."
        assert (
            request._get_query_string(
                {
                    "z": "two",
                    "a": "one",
                }
            )
            == "a=one&z=two"
        )

    def test_get_query_string_encoding(self) -> None:
        "Test _get_query_string with all printable ASCII characters."
        assert (
            request._get_query_string(
                {
                    "test": " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
                }
            )
            == "test=%20%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F0123456789%3A%3B%3C%3D%3E%3F%40ABCDEFGHIJKLMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmnopqrstuvwxyz%7B%7C%7D~"
        )

    def test_get_canonical_headers_without_token(self) -> None:
        "Test _get_canonical_headers with a Credentials.session_token."
        canonical_headers = request._get_canonical_headers(
            host=TEST_HOST,
            headers={
                "X-Amz-Content-Sha256": "1234",
            },
            iso_8601_timestamp=TEST_TIMESTAMP,
            credentials=Credentials(
                access_key_id="TESTACCESSKEY",
                secret_access_key="TESTSECRETACCESSKEY",
            ),
        )
        assert canonical_headers == {
            "Host": TEST_HOST,
            "X-Amz-Content-Sha256": "1234",
            "X-Amz-Date": "20000101T000000Z",
        }

    def test_get_canonical_headers_with_token(self) -> None:
        "Test _get_canonical_headers with a Credentials.session_token."
        canonical_headers = request._get_canonical_headers(
            host=TEST_HOST,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Amz-Content-Sha256": "1234",
            },
            iso_8601_timestamp=TEST_TIMESTAMP,
            credentials=TEST_CREDENTIALS,
        )

        assert canonical_headers == {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": TEST_HOST,
            "X-Amz-Content-Sha256": "1234",
            "X-Amz-Date": "20000101T000000Z",
            "X-Amz-Security-Token": "TESTSESSIONTOKEN",
        }

    def test_get_payload_hash_empty(self) -> None:
        "Test _get_payload_hash with None value."
        assert (
            request._get_payload_hash(None)
            == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_get_payload_hash_non_empty(self) -> None:
        "Test _get_payload_hash with dictionary."
        assert (
            request._get_payload_hash({"key": "value"})
            == "9724c1e20e6e3e4d7f57ed25f9d4efb006e508590d528c90da597f6a775c13e5"
        )

    def test_get_canonical_request(self) -> None:
        "Test _get_canonical_request."
        assert (
            request._get_canonical_request(
                method=Method.GET,
                path="/",
                query_string="QKey=QValue",
                payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                canonical_headers={
                    "Host": "www.test.com",
                    "X-Amz-Date": "20000101T000000Z",
                    "X-Amz-Security-Token": "TESTSESSIONTOKEN",
                },
            )
            == "GET\n/\nQKey=QValue\nhost:www.test.com\nx-amz-date:20000101T000000Z\nx-amz-security-token:TESTSESSIONTOKEN\n\nhost;x-amz-date;x-amz-security-token\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_get_string_to_sign(self) -> None:
        "Test _get_string_to_sign."
        assert (
            request._get_string_to_sign(
                scope="20000101/us-east-1/iam/aws4_request",
                iso_8601_timestamp=TEST_TIMESTAMP,
                canonical_request="GET\n/\nQKey=QValue\nhost:www.test.com\nx-amz-date:20000101T000000Z\nx-amz-security-token:TESTSESSIONTOKEN\n\nhost;x-amz-date;x-amz-security-token\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )
            == "AWS4-HMAC-SHA256\n20000101T000000Z\n20000101/us-east-1/iam/aws4_request\na9bd6d78c12b6a275b4259e2d46ece072e2051884c0b63a664a29d93c70408af"
        )

    def test_get_signing_key(self) -> None:
        "Test _get_signing_key."
        assert (
            request._get_signing_key(
                credentials=TEST_CREDENTIALS,
                date=TEST_DATE,
                region=Region.us_east_1,
                service="iam",
            )
            == b"\x07\xfdj@\x9e)\\TS\xbb\xf11;\xe0a+'\xb7\x06\xbd@y\x19\xf5\xad\xaahw\tm`\xff"
        )

    def test_get_authorization_header(self) -> None:
        "Test _get_authorization_header."
        assert request._get_authorization_header(
            signing_key=b"\x07\xfdj@\x9e)\\TS\xbb\xf11;\xe0a+'\xb7\x06\xbd@y\x19\xf5\xad\xaahw\tm`\xff",
            string_to_sign="AWS4-HMAC-SHA256\n20000101T000000Z\n20000101/us-east-1/iam/aws4_request\na9bd6d78c12b6a275b4259e2d46ece072e2051884c0b63a664a29d93c70408af",
            scope="20000101/us-east-1/iam/aws4_request",
            credentials=TEST_CREDENTIALS,
            canonical_headers={
                "Host": TEST_HOST,
                "X-Amz-Date": "20000101T000000Z",
                "X-Amz-Security-Token": "TESTSESSIONTOKEN",
            },
        ) == {
            "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d"
        }

    def test_get_signed_request(self) -> None:
        "Test _get_signed_request."
        test_request = request.Request(
            credentials=TEST_CREDENTIALS,
            method=Method.GET,
            host=TEST_HOST,
            query={"QKey": "QValue"},
            headers={"HKey": "HValue"},
        )
        signed_request = request._get_signed_request(
            request=test_request,
            authorization_header={
                "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d"
            },
            canonical_headers={
                "Host": TEST_HOST,
                "X-Amz-Date": "20000101T000000Z",
                "X-Amz-Security-Token": "TESTSESSIONTOKEN",
            },
        )
        assert signed_request.headers == {
            "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d",
            "Host": TEST_HOST,
            "HKey": "HValue",
            "X-Amz-Date": "20000101T000000Z",
            "X-Amz-Security-Token": "TESTSESSIONTOKEN",
        }
        # Assert requsts are identical except for headers
        assert (
            request.Request(
                credentials=signed_request.credentials,
                method=signed_request.method,
                host=signed_request.host,
                scheme=signed_request.scheme,
                body=signed_request.body,
                path=signed_request.path,
                query=signed_request.query,
                headers=test_request.headers,  # Use original headers for equality.
            )
            == test_request
        )


class TestRequest:
    """
    Test the Request class.
    Tests the individual sign function steps and compares the results to the sign function.
    Results should be identical.
    """

    def test_defaults(self) -> None:
        "Test the default vaules for the Request class."
        test_request = request.Request(
            credentials=TEST_CREDENTIALS, method=Method.GET, host=TEST_HOST
        )
        assert test_request.scheme == Scheme.https
        assert test_request.body is None
        assert test_request.query is None
        assert test_request.path == "/"
        assert test_request.headers == {}

    def test_get_url(self) -> None:
        "Test get_url."
        test_request = request.Request(
            credentials=TEST_CREDENTIALS,
            method=Method.GET,
            host=TEST_HOST,
            scheme=Scheme.http,
            query={"key1": "value1", "key2": "value2"},
            path="/test/path",
        )
        assert test_request.get_url() == "http://www.test.com/test/path"

    def test_sign_with_mocks(self) -> None:
        """
        Test main method get_sign with all helper methods mocked.
        """
        test_request = request.Request(
            credentials=TEST_CREDENTIALS,
            method=Method.GET,
            host=TEST_HOST,
            query={"QKey": "QValue"},
            headers={"HKey": "HValue"},
        )
        # Setup mocks
        with patch("awsync.request._get_payload_hash") as _get_payload_hash_mock, patch(
            "awsync.request._get_query_string"
        ) as _get_query_string_mock, patch(
            "awsync.request._get_canonical_headers"
        ) as _get_canonical_headers_mock, patch(
            "awsync.request._get_canonical_request"
        ) as _get_canonical_request_mock, patch(
            "awsync.request._get_string_to_sign"
        ) as _get_string_to_sign_mock, patch(
            "awsync.request._get_signing_key"
        ) as _get_signing_key_mock, patch(
            "awsync.request._get_authorization_header"
        ) as _get_authorization_header_mock, patch(
            "awsync.request._get_signed_request"
        ) as _get_signed_request_mock:
            _get_query_string_mock.return_value = "QKey=QValue"
            _get_payload_hash_mock.return_value = (
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            )
            _get_canonical_headers_mock.return_value = {
                "Host": TEST_HOST,
                "X-Amz-Date": "20000101T000000Z",
                "X-Amz-Security-Token": "TESTSESSIONTOKEN",
            }
            _get_canonical_request_mock.return_value = "GET\n/\nQKey=QValue\nhost:www.test.com\nx-amz-date:20000101T000000Z\nx-amz-security-token:TESTSESSIONTOKEN\n\nhost;x-amz-date;x-amz-security-token\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            _get_string_to_sign_mock.return_value = "AWS4-HMAC-SHA256\n20000101T000000Z\n20000101/us-east-1/iam/aws4_request\na9bd6d78c12b6a275b4259e2d46ece072e2051884c0b63a664a29d93c70408af"
            _get_signing_key_mock.return_value = b"\x07\xfdj@\x9e)\\TS\xbb\xf11;\xe0a+'\xb7\x06\xbd@y\x19\xf5\xad\xaahw\tm`\xff"
            _get_authorization_header_mock.return_value = {
                "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d"
            }
            _get_signed_request_mock.return_value = request.Request(
                credentials=TEST_CREDENTIALS,
                method=Method.GET,
                host=TEST_HOST,
                query={"QKey": "QValue"},
                headers={
                    "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d",
                    "Host": TEST_HOST,
                    "HKey": "HValue",
                    "X-Amz-Date": "20000101T000000Z",
                    "X-Amz-Security-Token": "TESTSESSIONTOKEN",
                },
            )

            # Call sign method
            signed_request = test_request.sign(
                utc_now=TEST_DATETIME,
                service="iam",
                region=Region.us_east_1,
            )
            assert signed_request.headers == {
                "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d",
                "Host": TEST_HOST,
                "HKey": "HValue",
                "X-Amz-Date": "20000101T000000Z",
                "X-Amz-Security-Token": "TESTSESSIONTOKEN",
            }
            # Assert requsts are identical except for headers
            assert (
                request.Request(
                    credentials=signed_request.credentials,
                    method=signed_request.method,
                    host=signed_request.host,
                    scheme=signed_request.scheme,
                    body=signed_request.body,
                    path=signed_request.path,
                    query=signed_request.query,
                    headers=test_request.headers,  # Use original headers for equality.
                )
                == test_request
            )

            # Assert mocks called
            _get_query_string_mock.assert_called_once_with(query={"QKey": "QValue"})
            _get_payload_hash_mock.assert_called_once_with(body=None)
            _get_canonical_headers_mock.assert_called_once_with(
                credentials=TEST_CREDENTIALS,
                host=TEST_HOST,
                headers={
                    "HKey": "HValue",
                },
                iso_8601_timestamp="20000101T000000Z",
            )
            _get_canonical_request_mock.assert_called_once_with(
                method=Method.GET,
                path="/",
                query_string="QKey=QValue",
                payload_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                canonical_headers={
                    "Host": "www.test.com",
                    "X-Amz-Date": "20000101T000000Z",
                    "X-Amz-Security-Token": "TESTSESSIONTOKEN",
                },
            )
            _get_string_to_sign_mock.assert_called_once_with(
                scope="20000101/us-east-1/iam/aws4_request",
                iso_8601_timestamp="20000101T000000Z",
                canonical_request="GET\n/\nQKey=QValue\nhost:www.test.com\nx-amz-date:20000101T000000Z\nx-amz-security-token:TESTSESSIONTOKEN\n\nhost;x-amz-date;x-amz-security-token\ne3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            )
            _get_signing_key_mock.assert_called_once_with(
                credentials=TEST_CREDENTIALS,
                date=TEST_DATE,
                region=Region.us_east_1,
                service="iam",
            )
            _get_authorization_header_mock.assert_called_once_with(
                signing_key=b"\x07\xfdj@\x9e)\\TS\xbb\xf11;\xe0a+'\xb7\x06\xbd@y\x19\xf5\xad\xaahw\tm`\xff",
                string_to_sign="AWS4-HMAC-SHA256\n20000101T000000Z\n20000101/us-east-1/iam/aws4_request\na9bd6d78c12b6a275b4259e2d46ece072e2051884c0b63a664a29d93c70408af",
                scope="20000101/us-east-1/iam/aws4_request",
                credentials=TEST_CREDENTIALS,
                canonical_headers={
                    "Host": TEST_HOST,
                    "X-Amz-Date": "20000101T000000Z",
                    "X-Amz-Security-Token": "TESTSESSIONTOKEN",
                },
            )
            _get_signed_request_mock.assert_called_once_with(
                request=test_request,
                authorization_header={
                    "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d"
                },
                canonical_headers={
                    "Host": "www.test.com",
                    "X-Amz-Date": "20000101T000000Z",
                    "X-Amz-Security-Token": "TESTSESSIONTOKEN",
                },
            )

    def test_sign_without_mocks(self) -> None:
        """
        Test entire pipeline with main method, get_sign.
        """
        test_request = request.Request(
            credentials=TEST_CREDENTIALS,
            method=Method.GET,
            host=TEST_HOST,
            query={"QKey": "QValue"},
            headers={"HKey": "HValue"},
        )
        signed_request = test_request.sign(
            utc_now=TEST_DATETIME,
            service="iam",
            region=Region.us_east_1,
        )
        assert signed_request.headers == {
            "Authorization": "AWS4-HMAC-SHA256 Credential=TESTACCESSKEY/20000101/us-east-1/iam/aws4_request,SignedHeaders=host;x-amz-date;x-amz-security-token,Signature=f58d9ccaeff88d327464547c29d268d4fba1c6decd669c31f55453096f72631d",
            "Host": TEST_HOST,
            "HKey": "HValue",
            "X-Amz-Date": "20000101T000000Z",
            "X-Amz-Security-Token": "TESTSESSIONTOKEN",
        }
        # Assert requsts are identical except for headers
        assert (
            request.Request(
                credentials=signed_request.credentials,
                method=signed_request.method,
                host=signed_request.host,
                scheme=signed_request.scheme,
                body=signed_request.body,
                path=signed_request.path,
                query=signed_request.query,
                headers=test_request.headers,  # Use original headers for equality.
            )
            == test_request
        )
