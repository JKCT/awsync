"Module main."
from asyncio import run
from httpx import AsyncClient

from awsync.client import Client
from awsync.models.aws import Region, Credentials


async def main() -> int:
    "Main function."
    async with AsyncClient() as httpx_client:
        client = Client(
            credentials=Credentials.from_environment(),
            httpx_client=httpx_client,
        )
        response = await client.list_stack_resources(
            region=Region.us_east_1, stack_name="Example-Stack-Name"
        )
        print(response)
    return 0


if __name__ == "__main__":
    run(main())
