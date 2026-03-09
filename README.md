# evawiki_sdk

[![PyPI Version](https://img.shields.io/pypi/v/evawiki-python-client)](https://pypi.org/project/evawiki-python-client/)
[![Python Version](https://img.shields.io/pypi/pyversions/evawiki-python-client)](https://pypi.org/project/evawiki-python-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Gradle-based SDK generator for EvaTeam API. Fetches OpenAPI spec, processes it with custom enhancements, and generates a production-ready Python client published to PyPI.

## Installation

```bash
pip install evawiki-python-client
```

## Quick Start

```python
from evawiki_client import ApiClient, Configuration
from evawiki_client.api.cmf_task_api import CmfTaskApi

config = Configuration(
    host="https://your-evateam-instance.com",
    api_key={"api_key": "your-api-key"}
)

api = CmfTaskApi(ApiClient(config))
response = api.cmf_task_create(kwargs={"title": "New Task"})
print(response.result)
```

## Features

- Full EvaTeam API v1.9.22 coverage (Tasks, Projects, Documents, Persons, Companies, etc.)
- Automatic OAuth2 authentication (API key → Bearer token)
- JSON-RPC 2.2 protocol with Pydantic v2 models
- Full-text search capabilities

## Development

```bash
# Generate and build client
./gradlew openApiGenerate    # Fetch + process + generate
./gradlew buildClient        # Build package
./gradlew publishToPyPI      # Publish to PyPI

# Individual steps
./gradlew fetchSwagger       # Fetch OpenAPI spec
./gradlew processSwagger     # Process spec
```

### Configuration

Edit `gradle.properties`:

```properties
OPENAPI_SPEC_FILE_NAME=evawiki.swagger.json
CLIENT_FOLDER_PATH=evawiki-client
```

### PyPI Token

```bash
./gradlew publishToPyPI -Ppypi.token=your-token
# or
export POETRY_PYPI_TOKEN_PYPI=your-token
./gradlew publishToPyPI
```

## Project Structure

```
.
├── build.gradle.kts          # Build configuration
├── scripts/process_swagger.py  # OpenAPI spec processor
├── src/main/resources/openapi-templates/  # Custom templates
└── evawiki-client/           # Generated client (not in git)
```

## License

MIT – see [LICENSE](LICENSE)

## Links

- [PyPI Package](https://pypi.org/project/evawiki-python-client/)
- [EvaTeam Docs](https://docs.evateam.ru/)
