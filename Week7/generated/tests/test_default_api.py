# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any  # noqa: F401
from openapi_server.models.product_input import ProductInput  # noqa: F401
from openapi_server.models.products_get200_response import ProductsGet200Response  # noqa: F401
from openapi_server.models.products_post201_response import ProductsPost201Response  # noqa: F401


def test_products_get(client: TestClient):
    """Test case for products_get

    List products
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/products",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_post(client: TestClient):
    """Test case for products_post

    Create product
    """
    product_input = {"price":0.8008282,"name":"name","description":"description"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/products",
    #    headers=headers,
    #    json=product_input,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_product_id_get(client: TestClient):
    """Test case for products_product_id_get

    Get product
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/products/{productId}".format(productId=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_product_id_put(client: TestClient):
    """Test case for products_product_id_put

    Replace product
    """
    product_input = {"price":0.8008282,"name":"name","description":"description"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/products/{productId}".format(productId=56),
    #    headers=headers,
    #    json=product_input,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_products_product_id_delete(client: TestClient):
    """Test case for products_product_id_delete

    Delete product
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/products/{productId}".format(productId=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

