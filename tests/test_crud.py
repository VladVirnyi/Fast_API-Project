import pytest

from app.crud import category as category_crud
from app.crud import order as order_crud
from app.crud import product as product_crud
from app.crud import profile as profile_crud
from app.crud import user as user_crud
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_user_crud(db_session):
    created = await user_crud.create_user(
        db_session,
        UserCreate(
            username="alice",
            email="alice@example.com",
            full_name="Alice QA",
            password="strongpass123",
        ),
    )

    fetched = await user_crud.get_user_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.username == "alice"

    updated = await user_crud.update_user(
        db_session,
        created.id,
        UserUpdate(full_name="Alice Updated", is_active=False),
    )
    assert updated is not None
    assert updated.full_name == "Alice Updated"
    assert updated.is_active is False

    deleted = await user_crud.delete_user(db_session, created.id)
    assert deleted is True
    assert await user_crud.get_user_by_id(db_session, created.id) is None


@pytest.mark.asyncio
async def test_category_crud(db_session):
    created = await category_crud.create_category(
        db_session,
        CategoryCreate(name="Electronics", description="Devices", slug="electronics"),
    )

    fetched = await category_crud.get_category_by_slug(db_session, "electronics")
    assert fetched is not None
    assert fetched.id == created.id

    updated = await category_crud.update_category(
        db_session,
        created.id,
        CategoryUpdate(name="Electronics Updated"),
    )
    assert updated is not None
    assert updated.name == "Electronics Updated"

    deleted = await category_crud.delete_category(db_session, created.id)
    assert deleted is True
    assert await category_crud.get_category_by_id(db_session, created.id) is None


@pytest.mark.asyncio
async def test_product_crud(db_session):
    category = await category_crud.create_category(
        db_session,
        CategoryCreate(name="Food", description="Food category", slug="food"),
    )

    created = await product_crud.create_product(
        db_session,
        ProductCreate(
            name="Apple",
            description="Fresh apple",
            price=12.5,
            stock=20,
            sku="APPLE-001",
            category_id=category.id,
        ),
    )

    fetched = await product_crud.get_product_by_sku(db_session, "APPLE-001")
    assert fetched is not None
    assert fetched.id == created.id

    updated = await product_crud.update_product(
        db_session,
        created.id,
        ProductUpdate(price=15.0, stock=10),
    )
    assert updated is not None
    assert updated.price == 15.0
    assert updated.stock == 10

    deleted = await product_crud.delete_product(db_session, created.id)
    assert deleted is True
    assert await product_crud.get_product_by_id(db_session, created.id) is None


@pytest.mark.asyncio
async def test_profile_crud(db_session):
    user = await user_crud.create_user(
        db_session,
        UserCreate(
            username="bob",
            email="bob@example.com",
            full_name="Bob",
            password="strongpass123",
        ),
    )

    created = await profile_crud.create_profile(
        db_session,
        user.id,
        ProfileCreate(city="Kyiv", country="Ukraine", bio="QA profile"),
    )

    fetched = await profile_crud.get_profile_by_user_id(db_session, user.id)
    assert fetched is not None
    assert fetched.id == created.id

    updated = await profile_crud.update_profile(
        db_session,
        created.id,
        ProfileUpdate(city="Lviv"),
    )
    assert updated is not None
    assert updated.city == "Lviv"

    deleted = await profile_crud.delete_profile(db_session, created.id)
    assert deleted is True
    assert await profile_crud.get_profile_by_id(db_session, created.id) is None


@pytest.mark.asyncio
async def test_order_crud(db_session):
    user = await user_crud.create_user(
        db_session,
        UserCreate(
            username="orderuser",
            email="orderuser@example.com",
            full_name="Order User",
            password="strongpass123",
        ),
    )
    category = await category_crud.create_category(
        db_session,
        CategoryCreate(name="Books", description="Books", slug="books"),
    )
    product = await product_crud.create_product(
        db_session,
        ProductCreate(
            name="Book",
            description="Interesting book",
            price=100.0,
            stock=5,
            sku="BOOK-001",
            category_id=category.id,
        ),
    )

    created_order = await order_crud.create_order(
        db_session,
        OrderCreate(
            user_id=user.id,
            notes="Initial order",
            items=[OrderItemCreate(product_id=product.id, quantity=2, unit_price=100.0)],
        ),
    )
    assert created_order.total_amount == 200.0
    assert created_order.status == "pending"

    fetched = await order_crud.get_order_by_id(db_session, created_order.id)
    assert fetched is not None
    assert len(fetched.items) == 1

    added_item = await order_crud.add_order_item(
        db_session,
        created_order.id,
        product.id,
        1,
        100.0,
    )
    assert added_item is not None

    updated = await order_crud.update_order_status(db_session, created_order.id, "completed")
    assert updated is not None
    assert updated.status == "completed"

    removed = await order_crud.remove_order_item(db_session, added_item.id)
    assert removed is True

    deleted = await order_crud.delete_order(db_session, created_order.id)
    assert deleted is True
    assert await order_crud.get_order_by_id(db_session, created_order.id) is None