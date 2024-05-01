"Module main."
from asyncio import run
import os
from datetime import datetime, UTC
from httpx import AsyncClient

from awsync.client import Client
from awsync.models.aws import Region, Credentials


async def main() -> int:
    "Main function."
    async with AsyncClient() as httpx_client:
        client = Client(
            credentials=Credentials(
                access_key=os.environ["AWS_ACCESS_KEY_ID"],
                secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                session_token=os.environ.get("AWS_SESSION_TOKEN"),
            ),
            httpx_client=httpx_client,
            utcnow=lambda: datetime.now(UTC),
        )

        response = await client.list_stack_resources(
            region=Region.us_east_1, stack_name="AWSRails-S3"
        )
        print(response)
        response_2 = await client.get_resource(
            region=Region.us_east_1,
            resource_type="AWS::S3::Bucket",
            identifier="awsrails-785590537371-us-east-1",
        )
        print(response_2)
        response_3 = await client.invoke(
            region=Region.us_east_1,
            function_name="AWSRails",
            payload={"test": "value"},
        )
        print(response_3)
        return 0


if __name__ == "__main__":
    run(main())
