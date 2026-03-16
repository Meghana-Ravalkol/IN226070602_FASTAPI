from fastapi import FastAPI, Response, status

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []

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

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int, response: Response):

    product = get_product_by_id(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if not product["in_stock"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Product out of stock"}

    # update existing cart item
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int, response: Response):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "Item not in cart"}


@app.post("/cart/checkout")
def checkout(data: dict):

    if not cart:
        return {"message": "Cart is empty"}

    customer = data["customer_name"]
    address = data["delivery_address"]

    grand_total = 0
    placed_orders = []

    for item in cart:

        order = {
            "customer_name": customer,
            "delivery_address": address,
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"]
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]

    cart.clear()

    return {
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }

@app.get("/orders")
def view_orders():

    return {
        "orders": orders,
        "count": len(orders)
    }