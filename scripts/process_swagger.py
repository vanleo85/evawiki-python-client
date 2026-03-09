import json
import sys
import re

JSONRPC_RESPONSE = {
    "type": "object",
    "description": "Универсальный контейнер для любого ответа JSON-RPC",
    "required": ["jsonrpc", "id"],
    "properties": {
        "jsonrpc": {
            "type": "string",
            "default": "2.2"
        },
        "callid": {
            "type": "string",
            "nullable": True,
            "format": "uuid"
        },
        "result": {
            "description": "Универсальное поле: может быть int, dict, list или null"
        },
        "error": {
            "type": "object",
            "nullable": True,
            "properties": {
                "code": {"type": "integer"},
                "message": {"type": "string"},
                "data": {"type": "object", "nullable": True}
            }
        }
    }
}

FULLSEARCH_PATH = {
    "post": {
        "summary": "CmfFullSearch.fulltext_search",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "jsonrpc": {
                                "type": "string",
                                "example": "2.2",
                                "default": "2.2"
                            },
                            "method": {
                                "type": "string",
                                "enum": [
                                    "CmfFullSearch.fulltext_search"
                                ],
                                "default": "CmfFullSearch.fulltext_search"
                            },
                            "callid": {
                                "type": "string",
                                "format": "uuid",
                                "example": "9e43d679-6e6a-4b81-b04e-ab5a415e3696",
                                "x-generate-uuid": True
                            },
                            "args": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "example": [
                                    "CmfTask:b0a83d78-154e-11f0-bd3a-0242ac110002"
                                ]
                            },
                            "kwargs": {
                                "type": "object",
                                "properties": {
                                    "archived": {
                                        "type": "boolean",
                                        "default": False
                                    },
                                    "deleted": {
                                        "type": "boolean",
                                        "default": False
                                    },
                                    "fields": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "example": [
                                            "code"
                                        ]
                                    },
                                    "no_analitycs": {
                                        "type": "boolean",
                                        "default": True
                                    },
                                    "parent_id": {
                                        "type": "string"
                                    },
                                    "slice": {
                                        "type": "array",
                                        "items": {
                                            "type": "integer"
                                        },
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "example": [
                                            0,
                                            50
                                        ]
                                    },
                                    "titles_only": {
                                        "type": "boolean",
                                        "default": False
                                    },
                                    "top": {
                                        "type": "boolean",
                                        "default": False
                                    }
                                },
                                "additionalProperties": False
                            }
                        },
                        "required": [
                            "callid",
                            "args",
                            "kwargs"
                        ]
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "OK"
            },
            "401": {
                "description": "Unauthorized"
            },
            "500": {
                "description": "Internal Server Error"
            }
        }
    }
}


def capitalize(s: str) -> str:
    if not s:
        return ""
    return s[0].upper() + s[1:]


def process_swagger(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Удаляем description из info
    if "info" in data:
        data["info"].pop("description", None)

    data.setdefault("components", {}).setdefault("schemas", {})["JsonRpcResponse"] = JSONRPC_RESPONSE

    # Заменяем operationId на сгенерированные значения
    if "paths" in data:

        # Добавляем полнотекстовый поиск, так как он отсутствует
        data["paths"]["/api/?m=CmfFullSearch.fulltext_search"] = FULLSEARCH_PATH

        for path_key, methods in data["paths"].items():
            for method_key, operation in methods.items():
                # Убираем префикс /api для расчета ID
                clean_path = path_key[8:] if path_key.startswith("/api/?m=") else path_key

                # Разделяем по символам /, {, }, -, _
                parts = re.split(r"[.=/{}_\-]", clean_path)
                # Капитализируем каждую часть (аналог Kotlin capitalize)
                parts = [capitalize(p) for p in parts if p]

                # Формируем ID: части пути + метод (например, Get)
                # generated_id = "".join(parts) + capitalize(method_key.lower())
                generated_id = "".join(parts)

                operation["operationId"] = generated_id

                #
                request_body_properties = operation.get("requestBody", {}).get("content", {}).get("application/json",
                                                                                                  {}).get("schema",
                                                                                                          {}).get(
                    "properties", {})
                request_body_required = operation.get("requestBody", {}).get("content", {}).get("application/json",
                                                                                                {}).get("schema",
                                                                                                        {}).get(
                    "required", {})
                if request_body_properties:
                    if request_body_properties.get("jsonrpc") and "default" not in request_body_properties.get(
                            "jsonrpc"):
                        request_body_properties["jsonrpc"]["default"] = "2.2"
                        if isinstance(request_body_required, list) and "jsonrpc" in request_body_required:
                            request_body_required.remove("jsonrpc")

                    if request_body_properties.get("method") and request_body_properties.get("method", {}).get("enum",
                                                                                                               {}):
                        if isinstance(request_body_properties["method"]["enum"], list) and len(
                                request_body_properties["method"]["enum"]) == 1:
                            request_body_properties["method"]["default"] = request_body_properties["method"]["enum"][0]
                            if isinstance(request_body_required, list) and "method" in request_body_required:
                                request_body_required.remove("method")
                    if request_body_properties.get("callid"):
                        request_body_properties.get("callid")["x-generate-uuid"] = True

                responses_node = operation.get("responses", {}).get("200", {})
                if responses_node and "content" not in responses_node:
                    responses_node["content"] = {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/JsonRpcResponse"
                            }
                        }
                    }

    # Добавляем компонент securitySchemes
    security_schemes = {
        "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    components = data.get("components", {})
    components["securitySchemes"] = security_schemes
    data["components"] = components

    # Добавляем глобальную секцию security
    data["security"] = [{"bearerAuth": []}]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_swagger(sys.argv[1])
    else:
        print("Usage: python3 process_swagger.py <path_to_swagger_json>")
