from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

@app.get("/products/{sku}")
async def get_sku(sku: Annotated[str, Path(min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")]):
    return {"skuID": sku}