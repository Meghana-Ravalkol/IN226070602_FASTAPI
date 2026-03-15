from fastapi import FastAPI, Response, status

app = FastAPI()

products = [
    {"id": 1, "name": "Keyboard", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]


def get_product_by_id(pid: int):
    for product in products:
        if product["id"] == pid:
            return product
    return None


@app.get("/products")
def read_products():
    return {
        "data": products,
        "count": len(products)
    }


@app.post("/products")
def create_product(data: dict, response: Response):

    for product in products:
        if product["name"].lower() == data["name"].lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": data["name"],
        "price": data["price"],
        "category": data["category"],
        "in_stock": data.get("in_stock", True)
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": "Product created",
        "product": new_product
    }


@app.get("/products/audit")
def audit_products():

    available = [p for p in products if p["in_stock"]]
    not_available = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 5 for p in available)

    highest = max(products, key=lambda x: x["price"])

    return {
        "total": len(products),
        "available_count": len(available),
        "out_of_stock": [p["name"] for p in not_available],
        "stock_value": total_value,
        "costliest": highest
    }


@app.put("/products/{product_id}")
def edit_product(
        product_id: int,
        price: int | None = None,
        in_stock: bool | None = None,
        response: Response = None
):

    product = get_product_by_id(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


@app.delete("/products/{product_id}")
def remove_product(product_id: int, response: Response):

    product = get_product_by_id(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {
        "message": f"{product['name']} removed"
    }