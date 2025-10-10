from typing import Any, Dict, List


def build_openapi_spec() -> Dict[str, Any]:
    tags: List[Dict[str, Any]] = [
        {"name": "Books", "description": "Operations related to library books"}
    ]
    schemas = {
        "Book": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "publisher": {"type": "string"},
                "publication_year": {"type": "integer"},
                "quantity": {"type": "integer"}
            },
            "required": ["id", "title", "author", "publisher", "publication_year", "quantity"]
        },
        "BookInput": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "publisher": {"type": "string"},
                "publication_year": {"type": "integer"},
                "quantity": {"type": "integer"}
            },
            "required": ["title", "author", "publisher", "publication_year", "quantity"]
        },
        "BookUpdate": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "publisher": {"type": "string"},
                "publication_year": {"type": "integer"},
                "quantity": {"type": "integer"}
            }
        },
        "Message": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    }
    paths = {
        "/api/books": {
            "get": {
                "tags": ["Books"],
                "summary": "List books",
                "responses": {
                    "200": {
                        "description": "A list of books",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Book"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Books"],
                "summary": "Create book",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BookInput"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "The created book",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Book"}
                            }
                        }
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            }
        },
        "/api/books/{book_id}": {
            "parameters": [
                {
                    "name": "book_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"}
                }
            ],
            "get": {
                "tags": ["Books"],
                "summary": "Retrieve book",
                "responses": {
                    "200": {
                        "description": "The requested book",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Book"}
                            }
                        }
                    },
                    "404": {
                        "description": "Not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            },
            "put": {
                "tags": ["Books"],
                "summary": "Update book",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BookUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "The updated book",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Book"}
                            }
                        }
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    },
                    "404": {
                        "description": "Not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            },
            "delete": {
                "tags": ["Books"],
                "summary": "Delete book",
                "responses": {
                    "200": {
                        "description": "Deletion confirmation",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    },
                    "404": {
                        "description": "Not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            }
        }
    }
    spec: Dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {
            "title": "Library API",
            "version": "1.0.0",
            "description": "API for managing library books"
        },
        "servers": [{"url": "http://localhost:5000"}],
        "tags": tags,
        "paths": paths,
        "components": {"schemas": schemas}
    }
    return spec
