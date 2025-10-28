# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import StrictInt
from typing import Any
from openapi_server.models.product_input import ProductInput
from openapi_server.models.products_get200_response import ProductsGet200Response
from openapi_server.models.products_post201_response import ProductsPost201Response


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/products",
    responses={
        200: {"model": ProductsGet200Response, "description": "Products retrieved"},
    },
    tags=["default"],
    summary="List products",
    response_model_by_alias=True,
)
async def products_get(
) -> ProductsGet200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_get()


@router.post(
    "/products",
    responses={
        201: {"model": ProductsPost201Response, "description": "Product created"},
        400: {"description": "Invalid payload"},
    },
    tags=["default"],
    summary="Create product",
    response_model_by_alias=True,
)
async def products_post(
    product_input: ProductInput = Body(None, description=""),
) -> ProductsPost201Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_post(product_input)


@router.get(
    "/products/{productId}",
    responses={
        200: {"model": ProductsPost201Response, "description": "Product retrieved"},
        404: {"description": "Product not found"},
    },
    tags=["default"],
    summary="Get product",
    response_model_by_alias=True,
)
async def products_product_id_get(
    productId: StrictInt = Path(..., description=""),
) -> ProductsPost201Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_product_id_get(productId)


@router.put(
    "/products/{productId}",
    responses={
        200: {"model": ProductsPost201Response, "description": "Product updated"},
        400: {"description": "Invalid payload"},
        404: {"description": "Product not found"},
    },
    tags=["default"],
    summary="Replace product",
    response_model_by_alias=True,
)
async def products_product_id_put(
    productId: StrictInt = Path(..., description=""),
    product_input: ProductInput = Body(None, description=""),
) -> ProductsPost201Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_product_id_put(productId, product_input)


@router.delete(
    "/products/{productId}",
    responses={
        204: {"description": "Product deleted"},
        404: {"description": "Product not found"},
    },
    tags=["default"],
    summary="Delete product",
    response_model_by_alias=True,
)
async def products_product_id_delete(
    productId: StrictInt = Path(..., description=""),
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().products_product_id_delete(productId)
