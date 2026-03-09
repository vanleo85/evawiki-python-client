# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an SDK generator project for EvaWiki (Evateam) API. It fetches an OpenAPI/Swagger specification from the EvaWiki documentation, processes it, and generates a Python client library using OpenAPI Generator with custom templates.

The generated Python client (`evawiki-python-client`) is published to PyPI using Poetry.

## Common Commands

### Building the Project

```bash
# Fetch the latest OpenAPI spec from EvaWiki docs
./gradlew fetchSwagger

# Process the swagger spec (adds missing endpoints, normalizes operationIds)
./gradlew processSwagger

# Generate the Python client from OpenAPI spec (includes fetch + process)
./gradlew openApiGenerate

# Build the generated Python client package (includes generation)
./gradlew buildClient

# Publish to PyPI (requires PYPI_TOKEN or pypi.token property)
./gradlew publishToPyPI
```

### Full Build and Publish Workflow

```bash
# Complete workflow to generate and publish
./gradlew publishToPyPI
```

## Architecture

### Build Pipeline

1. **fetchSwagger** - Downloads OpenAPI spec from `https://docs.evateam.ru/files/.../oas_evateam_v1_9_22.json` to `api-docs/`

2. **processSwagger** - Python script (`scripts/process_swagger.py`) that:
   - Removes descriptions from info section
   - Adds `JsonRpcResponse` schema for universal JSON-RPC response handling
   - Adds missing `CmfFullSearch.fulltext_search` endpoint
   - Generates operationIds from path/method (splits by `/`, `{`, `}`, `-`, `_` and capitalizes)
   - Sets default values for `jsonrpc`, `method`, and `callid` fields
   - Adds Bearer JWT security scheme globally
   - Wraps all 200 responses in JsonRpcResponse schema

3. **openApiGenerate** - OpenAPI Generator plugin:
   - Uses Python generator with custom templates from `src/main/resources/openapi-templates/`
   - Outputs to `evawiki-client/` directory (configurable via `CLIENT_FOLDER_PATH`)
   - Package name: `evawiki_client`
   - Project name: `evawiki-python-client`

### Configuration

Properties in `gradle.properties`:
- `OPENAPI_SPEC_FILE_NAME` - Name of the downloaded spec file (default: `evawiki.swagger.json`)
- `CLIENT_FOLDER_PATH` - Output directory for generated client (default: `evawiki-client`)

PyPI authentication (one of):
- `pypi.token` Gradle property
- `POETRY_PYPI_TOKEN_PYPI` environment variable
- `PYPI_PASSWORD` environment variable

### Custom Templates

Located in `src/main/resources/openapi-templates/`:

- **model_generic.mustache** - Custom Pydantic model template with:
  - UUID generation support via `x-generate-uuid` extension
  - Pydantic v2 configuration
  - Custom `to_dict()`, `from_dict()`, `to_json()`, `from_json()` methods

- **pyproject.mustache** - Poetry/PEP 621 pyproject.toml template with:
  - Poetry dependency management
  - Type checking configuration (mypy)
  - Development dependencies (pytest, tox, flake8)

- **common_README.mustache** - README with usage example

### JSON-RPC Protocol

The API uses JSON-RPC 2.2 protocol. All requests follow this structure:
```json
{
  "jsonrpc": "2.2",
  "method": "Api.method.name",
  "callid": "<uuid>",
  "args": [],
  "kwargs": {}
}
```

All responses follow the `JsonRpcResponse` schema:
```json
{
  "jsonrpc": "2.2",
  "callid": "<uuid>",
  "result": <any>,
  "error": <nullable>
}
```

## Project Structure

```
.
├── build.gradle.kts          # Gradle build configuration
├── gradle.properties         # Build properties
├── scripts/
│   └── process_swagger.py   # OpenAPI spec processing script
├── src/main/resources/
│   └── openapi-templates/   # Custom mustache templates
├── api-docs/                # Downloaded OpenAPI specs
├── evawiki-client/          # Generated Python client (not in git)
└── .build/                  # Build artifacts and notes
```
