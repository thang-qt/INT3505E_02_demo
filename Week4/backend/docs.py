from typing import Any, Dict, List


def build_openapi_spec() -> Dict[str, Any]:
    tags: List[Dict[str, Any]] = [
        {"name": "Auth", "description": "Operations related to authentication"},
        {"name": "Books", "description": "Operations related to library books"},
        {"name": "Loans", "description": "Operations related to book loans"},
    ]
    schemas = {
        "LoginInput": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["username", "password"]
        },
        "TokenResponse": {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "expires_at": {"type": "string", "format": "date-time"}
            },
            "required": ["token", "expires_at"]
        },
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
        "Loan": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "book_id": {"type": "integer"},
                "borrower": {"type": "string"},
                "loaned_at": {"type": "string", "format": "date-time"},
                "returned_at": {"type": "string", "format": "date-time", "nullable": True},
                "returned": {"type": "boolean"}
            },
            "required": ["id", "book_id", "borrower", "loaned_at", "returned"]
        },
        "LoanInput": {
            "type": "object",
            "properties": {
                "book_id": {"type": "integer"},
                "borrower": {"type": "string"}
            },
            "required": ["book_id", "borrower"]
        },
        "LoanReturn": {
            "type": "object",
            "properties": {
                "returned": {"type": "boolean"}
            },
            "required": ["returned"]
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
        "/api/tokens": {
            "post": {
                "tags": ["Auth"],
                "summary": "Create access token",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoginInput"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Issued token",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TokenResponse"}
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
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            }
        },
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
                "security": [{"BearerAuth": []}],
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
                "security": [{"BearerAuth": []}],
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
                "security": [{"BearerAuth": []}],
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
        },
        "/api/loans": {
            "get": {
                "tags": ["Loans"],
                "summary": "List loans",
                "parameters": [
                    {
                        "name": "include_history",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "boolean"},
                        "description": "Include returned loans when true"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "A list of loans",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Loan"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Loans"],
                "summary": "Create loan",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoanInput"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "The created loan",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Loan"}
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
                        "description": "Book not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    },
                    "409": {
                        "description": "Book unavailable",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Message"}
                            }
                        }
                    }
                }
            }
        },
        "/api/loans/{loan_id}": {
            "parameters": [
                {
                    "name": "loan_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"}
                }
            ],
            "get": {
                "tags": ["Loans"],
                "summary": "Retrieve loan",
                "responses": {
                    "200": {
                        "description": "The requested loan",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Loan"}
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
            "patch": {
                "tags": ["Loans"],
                "summary": "Return loan",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoanReturn"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "The updated loan",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Loan"}
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
                    },
                    "409": {
                        "description": "Already returned",
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
        "components": {
            "schemas": schemas,
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer"
                }
            }
        }
    }
    return spec
