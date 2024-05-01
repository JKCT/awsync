"Middle level abstraction async AWS client for API requests."
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any, Callable, Dict, List, Optional

from httpx import AsyncClient

from awsync.models.aws import Credentials, Region
from awsync.models.http import Method
from awsync.request import Request


@dataclass(frozen=True)
class Response:
    "An API response."
    status: int
    "Status code."
    text: str
    "Response context as text."


class MaxRetriesException(Exception):
    "Maximum number of retries exceeded."


class StatusError(Exception):
    "API responded with a non-2XX status code."


async def request_with_retry(
    client: AsyncClient,
    request: Request,
    retries: int = 3,
) -> Response:
    """
    Make an async HTTP request with retries and exponential backoff.
    Will only retry if request fails due to throttling or a server error.
    """
    attempt = 0
    client_response = await client.request(
        method=request.method,
        url=request.get_url(),
        headers=request.headers,
        params=request.query,
        json=request.body,
    )
    while client_response.status_code >= 500 or (
        client_response.status_code == 400 and "Throttling" in client_response.text
    ):
        # Base case
        if attempt > retries:
            raise MaxRetriesException(
                f"Maximum number of retries '{retries}' exceeded.\n"
                f"Response: {client_response}"
            )
        # Retry if remote error or throttling - exponential backoff
        await asyncio.sleep(2**attempt)
        client_response = await client.request(
            method=request.method,
            url=request.get_url(),
            headers=request.headers,
            params=request.query,
            json=request.body,
        )
        attempt += 1
    response = Response(status=client_response.status_code, text=client_response.text)
    if response.status < 200 or response.status >= 300:
        raise StatusError(f"Recieved non-2XX response code.\n" f"Response: {response}")
    return response


@dataclass(frozen=True)
class Client:
    "An AWS API client."
    credentials: Credentials
    "AWS credentials."
    httpx_client: AsyncClient
    "The httpx AsyncClient to use for async reqeusts."
    utcnow: Callable[[], datetime]
    "A zero argument callable function that returns the current datetime in UTC."

    async def assume_role(
        self,
        role_arn: str,
    ) -> Dict[str, Any]:
        "Get AWS Role credentials with STS AssumeRole."
        service = "sts"
        region = Region.us_east_1
        request = Request(
            credentials=self.credentials,
            method=Method.POST,
            host=f"{service}.amazonaws.com",
            body={
                "Action": "AssumeRole",
                "RoleArn": role_arn,
                "RoleSessionName": "AsyncSession",
                "Version": "2011-06-15",
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
        )
        signed_request = request.sign(
            utc_now=self.utcnow(), service=service, region=region
        )
        response = await request_with_retry(
            self.httpx_client,
            request=signed_request,
        )
        json_response: Dict[str, Any] = json.loads(response.text)
        return json_response

    async def list_stack_resources(
        self,
        region: Region,
        stack_name: str,
        next_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        "List all resources in a CloudFormation stack asynchronously."
        query_params = {
            "Action": "ListStackResources",
            "Version": "2010-05-15",
            "StackName": stack_name,
        }
        if next_token:
            query_params.update({"NextToken": next_token})

        service = "cloudformation"
        request = Request(
            credentials=self.credentials,
            method=Method.GET,
            host=f"{service}.{region}.amazonaws.com",
            query=query_params,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
        )

        signed_request = request.sign(
            utc_now=self.utcnow(), service=service, region=region
        )
        response = await request_with_retry(
            self.httpx_client,
            request=signed_request,
        )

        json_response = json.loads(response.text)
        result = json_response["ListStackResourcesResponse"]["ListStackResourcesResult"]
        resources: List[Dict[str, Any]] = result["StackResourceSummaries"]

        # Handle pagination
        next_token = result.get("NextToken")
        if next_token:
            resources.extend(
                await self.list_stack_resources(region, stack_name, next_token)
            )
        return resources

    async def get_resource(
        self,
        region: Region,
        resource_type: str,
        identifier: str,
    ) -> Dict[str, Any]:
        """
        Returns information about the current state of the specified resource
        in CloudFormation schema.
        """
        service = "cloudcontrolapi"
        request = Request(
            credentials=self.credentials,
            method=Method.POST,
            host=f"{service}.{region}.amazonaws.com",
            body={
                "Action": "GetResource",
                "Version": "2021-09-30",
                "TypeName": resource_type,
                "Identifier": identifier,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-amz-json-1.0",
                "X-Amz-Target": "CloudApiService.GetResource",
            },
        )
        signed_request = request.sign(
            utc_now=self.utcnow(), service=service, region=region
        )
        response = await request_with_retry(
            self.httpx_client,
            request=signed_request,
        )
        json_response = json.loads(response.text)
        properties = json_response["ResourceDescription"]["Properties"]
        resource: Dict[str, Any] = json.loads(properties)
        return resource

    async def invoke(
        self,
        region: Region,
        function_name: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Invokes a Lambda function.
        """
        service = "lambda"
        request = Request(
            credentials=self.credentials,
            method=Method.POST,
            host=f"{service}.{region}.amazonaws.com",
            path=f"/2015-03-31/functions/{function_name}/invocations",
            body=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        signed_request = request.sign(
            utc_now=self.utcnow(), service=service, region=region
        )
        response = await request_with_retry(
            self.httpx_client,
            request=signed_request,
        )
        return response.text
