"""
Signs Requests with AWS Signature V4 for Authorizing AWS API calls.
See: https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html
"""

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import hmac
import json
from typing import Any, Dict, NewType, Optional
from urllib.parse import quote
from hashlib import sha256

from awsync.models.http import Method, Scheme
from awsync.models.aws import Credentials, Region

Date = NewType("Date", str)
Timestamp = NewType("Timestamp", str)


def _uri_encode(string: str, is_path: bool = False) -> str:
    """
    URI encode every byte.
    If is_path=True, '/' is not encoded, see last rule below.

    UriEncode() must enforce the following rules:
    - URI encode every byte except the unreserved characters: 'A'-'Z', 'a'-'z', '0'-'9', '-', '.', '_', and '~'.
    - The space character is a reserved character and must be encoded as "%20" (and not as "+").
    - Each URI encoded byte is formed by a '%' and the two-digit hexadecimal value of the byte.
    - Letters in the hexadecimal value must be uppercase, for example "%1A".
    - Encode the forward slash character, '/', everywhere except in the object key name (request path). For example, if the object key name is photos/Jan/sample.jpg, the forward slash in the key name is not encoded.
    """
    unreserved_characters = "-_.~"
    if is_path:
        unreserved_characters += "/"
    return quote(string, safe=unreserved_characters)


def _sha_hash(string: str) -> str:
    "Secure Hash Algorithm (SHA) 256 cryptographic hash function then encoded with Lowercase base 16 encoding (Hex)."
    return sha256(string.encode()).hexdigest()


def _get_query_string(query: Optional[Dict[str, str]]) -> str:
    """
    The URI-encoded query string parameters.
    You URI-encode each name and values individually.
    You must also sort the parameters in the canonical query string alphabetically by key name.
    The sorting occurs after encoding.
    NOTE: Does not include '?' at the start.
    """
    if not query:
        return ""
    return "&".join(
        sorted([f"{_uri_encode(k)}={_uri_encode(v)}" for k, v in query.items()])
    )


def _get_canonical_headers(
    host: str,
    credentials: Credentials,
    headers: Dict[str, str],
    iso_8601_timestamp: Timestamp,
) -> Dict[str, str]:
    """
    CanonicalHeaders list must include the following:
        - HTTP host header.
        - If the Content-Type header is present in the request, you must add it to the CanonicalHeaders list.
        - Any x-amz-* headers that you plan to include in your request must also be added. For example, if you are using temporary security credentials, you need to include x-amz-security-token in your request. You must add this header in the list of CanonicalHeaders.
    """
    # Add mandatory headers
    mandatory_headers: Dict[str, str] = {
        "Host": host,
        "X-Amz-Date": iso_8601_timestamp,
    }
    if credentials.session_token:
        mandatory_headers["X-Amz-Security-Token"] = credentials.session_token

    # Add Content-Type and any X-Amz-* headers present in request
    canonical_headers = {
        k: v
        for k, v in headers.items()
        if k.lower() == "content-type" or k.lower().startswith("x-amz-")
    }
    # Overwrite any mandatory headers
    canonical_headers.update(mandatory_headers)
    return canonical_headers


def _get_payload_hash(body: Optional[Dict[str, Any]]) -> str:
    "A string created using the payload in the body of the HTTP request as input to a hash function. This string uses lowercase hexadecimal characters. If there is no payload in the request, you compute a hash of the empty string ('')."
    payload = json.dumps(body) if body else ""
    return _sha_hash(payload)


def _get_canonical_request(
    method: Method,
    path: str,
    query_string: str,
    payload_hash: str,
    canonical_headers: Dict[str, str],
) -> str:
    "Step 1: Create a canonical request."
    canonical_headers_string = (
        "\n".join(
            sorted([f"{k.lower()}:{v.strip()}" for k, v in canonical_headers.items()])
        )
        + "\n"
    )
    signed_headers_string = ";".join(
        sorted([k.lower() for k in canonical_headers.keys()])
    )
    return "\n".join(
        [
            method,
            _uri_encode(path, is_path=True),
            query_string,
            canonical_headers_string,
            signed_headers_string,
            payload_hash,
        ]
    )


def _get_string_to_sign(
    scope: str,
    iso_8601_timestamp: Timestamp,
    canonical_request: str,
) -> str:
    """
    Step 2: Create a hash of the canonical request.
    Step 3: Create a string to sign.
    """
    return "\n".join(
        [
            "AWS4-HMAC-SHA256",
            iso_8601_timestamp,
            scope,
            _sha_hash(canonical_request),
        ]
    )


def _get_signing_key(
    credentials: Credentials, date: Date, region: Region, service: str
) -> bytes:
    "Step 4: Calculate the signature."

    def hmac_sha256(key: bytes, message: str) -> bytes:
        "Computes message HMAC by using the SHA256 algorithm with the signing key provided."
        return hmac.new(key, message.encode(), hashlib.sha256).digest()

    k_date = hmac_sha256(("AWS4" + credentials.secret_access_key).encode(), date)
    k_region = hmac_sha256(k_date, region)
    k_service = hmac_sha256(k_region, service)
    k_signing = hmac_sha256(k_service, "aws4_request")
    return k_signing


def _get_authorization_header(
    signing_key: bytes,
    string_to_sign: str,
    scope: str,
    credentials: Credentials,
    canonical_headers: Dict[str, str],
) -> Dict[str, str]:
    "Step 4 part 2: Create Authorization header from signature."
    signature = hmac.new(
        signing_key, string_to_sign.encode(), hashlib.sha256
    ).hexdigest()
    authorization_header_value = ",".join(
        [
            f"AWS4-HMAC-SHA256 Credential={credentials.access_key_id}/{scope}",
            f"SignedHeaders={';'.join(sorted([k.lower() for k in canonical_headers.keys()]))}",
            f"Signature={signature}",
        ]
    )
    return {"Authorization": authorization_header_value}


def _get_signed_request(
    request: "Request",
    authorization_header: Dict[str, str],
    canonical_headers: Dict[str, str],
) -> "Request":
    "Step 5: Add the signature to the request."
    # Add all mandatory headers.
    authorization_header.update(canonical_headers)
    # Combine with original headers.
    headers = request.headers if request.headers else {}
    headers.update(authorization_header)
    # Return new, signed Request.
    return Request(  # All attributes are the same except for headers.
        credentials=request.credentials,
        method=request.method,
        host=request.host,
        scheme=request.scheme,
        body=request.body,
        path=request.path,
        query=request.query,
        headers=headers,  # Updated headers with additional auth_headers.
    )


@dataclass(frozen=True)
class Request:
    "A complete HTTP Request."
    credentials: Credentials
    "AWS Credentials."
    method: Method
    "The HTTP method."
    host: str
    "The fully qualified domain name (FQDN)."
    scheme: Scheme = Scheme.https
    "The HTTP scheme."
    body: Optional[Dict[str, Any]] = None
    "(Optional) Body (payload) as key/value pairs, values must be serializable by json.dumps()."
    path: str = "/"
    "The URI-encoded version of the absolute path component URI, starting with the '/' that follows the domain name and up to the end of the string or to the question mark character ('?') if you have query string parameters. If the absolute path is empty, use a forward slash character (/)."
    query: Optional[Dict[str, str]] = None
    "(Optional) The query string parameters as key/value pairs."
    headers: Dict[str, str] = field(default_factory=dict)
    """
    The request headers as key/value pairs.

    NOTE: The following headers will be provided automatically when calling sign():
    - Authorization
    - Host
    - X-Amz-Date
    - X-Amz-Security-Token (If a session_token is present in Credentials)
    """

    def get_url(self) -> str:
        "Returns constructed URL as a string."
        return f"{self.scheme}://{self.host}{self.path}"

    def sign(self, utc_now: datetime, service: str, region: Region) -> "Request":
        "Main public method - returns a new, signed version of the original Request."
        # Prepare common variables
        date = Date(utc_now.strftime("%Y%m%d"))  # YYYYMMDD
        iso_8601_timestamp = Timestamp(
            utc_now.strftime("%Y%m%dT%H%M%SZ")  # YYYYMMDDTHHMMSSZ
        )
        query_string = _get_query_string(query=self.query)
        payload_hash = _get_payload_hash(body=self.body)
        canonical_headers = _get_canonical_headers(
            credentials=self.credentials,
            host=self.host,
            headers=self.headers,
            iso_8601_timestamp=iso_8601_timestamp,
        )
        scope = f"""{date}/{region}/{service}/aws4_request"""

        # Sign request
        canonical_request = _get_canonical_request(
            method=self.method,
            path=self.path,
            query_string=query_string,
            payload_hash=payload_hash,
            canonical_headers=canonical_headers,
        )
        string_to_sign = _get_string_to_sign(
            scope=scope,
            iso_8601_timestamp=iso_8601_timestamp,
            canonical_request=canonical_request,
        )
        signing_key = _get_signing_key(
            credentials=self.credentials,
            date=date,
            region=region,
            service=service,
        )
        authorization_header = _get_authorization_header(
            signing_key=signing_key,
            string_to_sign=string_to_sign,
            scope=scope,
            credentials=self.credentials,
            canonical_headers=canonical_headers,
        )
        request = _get_signed_request(
            request=self,
            authorization_header=authorization_header,
            canonical_headers=canonical_headers,
        )
        return request
