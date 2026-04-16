import pytest


@pytest.mark.asyncio
async def test_users_api_crud(client):
    create_response = await client.post(
        "/users/",
        json={
            "username": "api_user",
            "email": "api_user@example.com",
            "full_name": "API User",
            "password": "strongpass123",
        },
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "api_user"

    update_response = await client.put(
        f"/users/{user_id}",
        json={"full_name": "Updated API User", "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated API User"

    delete_response = await client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    not_found_response = await client.get(f"/users/{user_id}")
    assert not_found_response.status_code == 404


@pytest.mark.asyncio
async def test_categories_and_products_api_crud(client):
    category_response = await client.post(
        "/categories/",
        json={"name": "API Category", "description": "Desc", "slug": "api-category"},
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    category_update = await client.put(
        f"/categories/{category_id}",
        json={"name": "API Category Updated"},
    )
    assert category_update.status_code == 200
    assert category_update.json()["name"] == "API Category Updated"

    product_response = await client.post(
        "/products/",
        json={
            "name": "API Product",
            "description": "Prod desc",
            "price": 199.99,
            "stock": 7,
            "sku": "API-PROD-001",
            "category_id": category_id,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    product_list = await client.get("/products/", params={"category_id": category_id})
    assert product_list.status_code == 200
    assert len(product_list.json()) == 1

    product_update = await client.put(
        f"/products/{product_id}",
        json={"stock": 3, "price": 149.99},
    )
    assert product_update.status_code == 200
    assert product_update.json()["stock"] == 3

    product_delete = await client.delete(f"/products/{product_id}")
    assert product_delete.status_code == 204

    category_delete = await client.delete(f"/categories/{category_id}")
    assert category_delete.status_code == 204


@pytest.mark.asyncio
async def test_profiles_and_orders_api_crud(client):
    user_response = await client.post(
        "/users/",
        json={
            "username": "order_api_user",
            "email": "order_api_user@example.com",
            "full_name": "Order API User",
            "password": "strongpass123",
        },
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    category_response = await client.post(
        "/categories/",
        json={"name": "Orders Cat", "description": "Orders", "slug": "orders-cat"},
    )
    category_id = category_response.json()["id"]

    product_response = await client.post(
        "/products/",
        json={
            "name": "Order Product",
            "description": "Order product",
            "price": 50.0,
            "stock": 20,
            "sku": "ORDER-PROD-001",
            "category_id": category_id,
        },
    )
    product_id = product_response.json()["id"]

    profile_response = await client.post(
        f"/profiles/users/{user_id}",
        json={"bio": "Bio", "city": "Kyiv", "country": "Ukraine"},
    )
    assert profile_response.status_code == 201
    profile_id = profile_response.json()["id"]

    profile_update = await client.put(
        f"/profiles/{profile_id}",
        json={"city": "Lviv"},
    )
    assert profile_update.status_code == 200
    assert profile_update.json()["city"] == "Lviv"

    order_response = await client.post(
        "/orders/",
        json={
            "user_id": user_id,
            "notes": "API order",
            "items": [{"product_id": product_id, "quantity": 2, "unit_price": 50.0}],
        },
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    assert order_response.json()["total_amount"] == 100.0

    add_item_response = await client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 1, "unit_price": 50.0},
    )
    assert add_item_response.status_code == 201
    item_id = add_item_response.json()["id"]

    status_update_response = await client.put(
        f"/orders/{order_id}",
        json={"status": "completed"},
    )
    assert status_update_response.status_code == 200
    assert status_update_response.json()["status"] == "completed"

    remove_item_response = await client.delete(f"/orders/{order_id}/items/{item_id}")
    assert remove_item_response.status_code == 204

    delete_order_response = await client.delete(f"/orders/{order_id}")
    assert delete_order_response.status_code == 204

    delete_profile_response = await client.delete(f"/profiles/{profile_id}")
    assert delete_profile_response.status_code == 204