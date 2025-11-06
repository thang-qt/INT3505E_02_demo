import os
from datetime import datetime, timezone
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
app = FastAPI()
load_dotenv()
class ProductInput(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
class Product(ProductInput):
    id: int
    createdAt: datetime
    updatedAt: datetime
class ProductEnvelope(BaseModel):
    data: Product
class ProductListEnvelope(BaseModel):
    data: List[Product]
def get_settings():
    uri = os.getenv("MONGODB_URI")
    database = os.getenv("MONGODB_DATABASE", "products")
    if not uri:
        raise RuntimeError("MONGODB_URI is required")
    return uri, database
class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database_name: Optional[str] = None
    async def connect(self):
        if self.client is None:
            uri, database = get_settings()
            self.client = AsyncIOMotorClient(uri)
            self.database_name = database
    async def get_db(self):
        if self.client is None:
            await self.connect()
        return self.client[self.database_name]
database = Database()
async def get_collection():
    db = await database.get_db()
    return db.get_collection("products")
async def next_product_id(db):
    counters = db.get_collection("counters")
    doc = await counters.find_one_and_update(
        {"_id": "products"},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["value"]
def normalize_product(doc):
    if doc is None:
        return None
    doc.pop("_id", None)
    return Product(**doc)
@app.on_event("startup")
async def startup():
    await database.connect()
@app.get("/products", response_model=ProductListEnvelope)
async def list_products(response: Response, collection=Depends(get_collection)):
    cursor = collection.find({}, sort=[("id", 1)])
    items = [normalize_product(doc) async for doc in cursor]
    response.headers["Cache-Control"] = "no-store"
    return {"data": items}
@app.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductEnvelope)
async def create_product(payload: ProductInput, response: Response, collection=Depends(get_collection)):
    now = datetime.now(timezone.utc)
    new_id = await next_product_id(collection.database)
    document = {
        "id": new_id,
        "name": payload.name,
        "price": payload.price,
        "description": payload.description,
        "createdAt": now,
        "updatedAt": now,
    }
    await collection.insert_one(document)
    response.headers["Cache-Control"] = "no-store"
    return {"data": Product(**document)}
@app.get("/products/{productId}", response_model=ProductEnvelope)
async def get_product(productId: int, response: Response, collection=Depends(get_collection)):
    document = await collection.find_one({"id": productId})
    product = normalize_product(document)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response.headers["Cache-Control"] = "no-store"
    return {"data": product}
@app.put("/products/{productId}", response_model=ProductEnvelope)
async def update_product(productId: int, payload: ProductInput, response: Response, collection=Depends(get_collection)):
    now = datetime.now(timezone.utc)
    document = await collection.find_one({"id": productId})
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    updated = {
        "id": productId,
        "name": payload.name,
        "price": payload.price,
        "description": payload.description,
        "createdAt": document["createdAt"],
        "updatedAt": now,
    }
    await collection.replace_one({"id": productId}, updated)
    response.headers["Cache-Control"] = "no-store"
    return {"data": Product(**updated)}
@app.delete("/products/{productId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(productId: int, response: Response, collection=Depends(get_collection)):
    result = await collection.delete_one({"id": productId})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    response.headers["Cache-Control"] = "no-store"
