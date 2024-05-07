# awsync

![CICD](https://github.com/JKCT/awsync/actions/workflows/cicd.yaml/badge.svg)

An asynchronous, fully-typed AWS API library with a focus on being understandable, reliable, and maintainable.

**NOTE: Currently a work in progress!**
Only a few API methods currently implemented for testing and development.

## Usage

```python
"Module main."
from asyncio import run
from datetime import datetime, UTC
from httpx import AsyncClient

from awsync.client import Client
from awsync.models.aws import Region, Credentials


async def main() -> int:
    "Main function."
    async with AsyncClient() as httpx_client:
        client = Client(
            credentials=Credentials.from_environment(),
            httpx_client=httpx_client,
            utcnow=lambda: datetime.now(UTC),
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

- [make](https://www.gnu.org/software/make/)
- [python3](https://www.python.org/)
- [poetry](https://python-poetry.org/)

### Package Management

- `make init` install/update dependencies, alias for `poetry install --sync`.
- `poetry add` add a dependency ie. `poetry add pydantic`.
- `poetry add -D` add a development dependency ie. `poetry add -D black`.
- `poetry remove` remove a dependency ie. `poetry remove pydantic`.
- `poetry shell` activate the python virtual environment.
- `exit` exit the python virtual environment.

### Repository Mangement

- `make run` runs the main module.
- `make pr` runs all pull request pre-checks below.
- `make format` runs code formatter.
- `make lint` checks code linting.
- `make test` runs tests.

## Repository TODO:

- Logging
- Test Coverage
- Automatic Publish CICD
- Documentation with [mkDocs](https://squidfunk.github.io/mkdocs-material/)
- Issue template
- Repository Template variables?
- Test Makefile replacements
  - [Poetry run](https://python-poetry.org/docs/cli/#run)
  - [doit](https://pydoit.org/)
