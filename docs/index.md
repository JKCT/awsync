# awsync

![CICD](https://github.com/JKCT/awsync/actions/workflows/cicd.yaml/badge.svg)

An asynchronous, fully-typed AWS API library with a focus on being understandable, reliable, and maintainable.

## Getting Started

📖 Read [the documentation](https://jkct.github.io/awsync/)!

**NOTE: Currently a work in progress!**
Only a few API methods currently implemented for testing and development.

## Usage

```python
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
```

## Local Developer Setup

Requirements:

- [mise](https://mise.jdx.dev/)
- [python](https://www.python.org/) 3.8 or greater
- [poetry](https://python-poetry.org/)

[Install mise](https://mise.jdx.dev/getting-started.html) then run `mise run init` to setup python, poetry, and install dependencies.

### Repository Mangement

This repository uses [mise](https://mise.jdx.dev/) for tool and task management.

List all available commands with `mise tasks`.

Run all pull request checks locally with `mise run pr`

### Package Management

This repository uses [poetry](https://python-poetry.org/) for python package management.

- `poetry install --sync` install/update dependencies.
- `poetry add` add a dependency ie. `poetry add black`.
- `poetry add -D` add a development dependency ie. `poetry add -D black`.
- `poetry remove` remove a dependency ie. `poetry remove black`.
- `poetry shell` activate the python virtual environment for access to installed packages.
- `exit` exit the python virtual environment.
