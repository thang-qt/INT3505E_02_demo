# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any
from openapi_server.models.product_input import ProductInput
from openapi_server.models.products_get200_response import ProductsGet200Response
from openapi_server.models.products_post201_response import ProductsPost201Response


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def products_get(
        self,
    ) -> ProductsGet200Response:
        ...


    async def products_post(
        self,
        product_input: ProductInput,
    ) -> ProductsPost201Response:
        ...


    async def products_product_id_get(
        self,
        productId: StrictInt,
    ) -> ProductsPost201Response:
        ...


    async def products_product_id_put(
        self,
        productId: StrictInt,
        product_input: ProductInput,
    ) -> ProductsPost201Response:
        ...


    async def products_product_id_delete(
        self,
        productId: StrictInt,
    ) -> None:
        ...
