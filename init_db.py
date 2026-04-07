"""
Script for database seeding with test data.

Usage:
    python init_db.py
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import select, func

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.crud import user as user_crud, category as category_crud, product as product_crud, order as order_crud
from app.crud import profile as profile_crud
from app.schemas.user import UserCreate
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.profile import ProfileCreate
from app.models import User


async def seed_database():
    """Seeds the database with test data (idempotent)."""
    print("🌱 Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            users_count = await session.scalar(select(func.count(User.id)))
            if users_count and users_count > 0:
                print("ℹ️ Database already has data. Seed skipped.")
                return

            # ==================== USERS ====================
            print("\n👤 Creating users...")
            users_data = [
                UserCreate(
                    username="john_doe",
                    email="john@example.com",
                    full_name="John Doe",
                    password="securepass123"
                ),
                UserCreate(
                    username="jane_smith",
                    email="jane@example.com",
                    full_name="Jane Smith",
                    password="securepass456"
                ),
                UserCreate(
                    username="bob_johnson",
                    email="bob@example.com",
                    full_name="Bob Johnson",
                    password="securepass789"
                ),
            ]
            
            created_users = []
            for user_data in users_data:
                user = await user_crud.create_user(session, user_data)
                created_users.append(user)
                print(f"  ✓ User created: {user.username} (ID: {user.id})")

            # ==================== PROFILES ====================
            print("\n🪪 Creating profiles...")
            profiles_data = [
                ProfileCreate(
                    bio="Backend developer and tech enthusiast",
                    phone="+380501112233",
                    address="Shevchenka 1",
                    city="Kyiv",
                    country="Ukraine",
                    zip_code="01001",
                ),
                ProfileCreate(
                    bio="QA engineer, loves clean test cases",
                    phone="+380502223344",
                    address="Naukova 18",
                    city="Lviv",
                    country="Ukraine",
                    zip_code="79000",
                ),
                ProfileCreate(
                    bio="Product manager and sports fan",
                    phone="+380503334455",
                    address="Soborna 7",
                    city="Dnipro",
                    country="Ukraine",
                    zip_code="49000",
                ),
            ]

            for user, profile_data in zip(created_users, profiles_data):
                profile = await profile_crud.create_profile(session, user.id, profile_data)
                print(f"  ✓ Profile created for {user.username} (Profile ID: {profile.id})")
            
            # ==================== CATEGORIES ====================
            print("\n📁 Creating categories...")
            categories_data = [
                CategoryCreate(
                    name="Electronics",
                    description="Electronic devices and gadgets",
                    slug="elektronika"
                ),
                CategoryCreate(
                    name="Clothing",
                    description="Men's and women's clothing",
                    slug="odyag"
                ),
                CategoryCreate(
                    name="Books",
                    description="Books of various genres",
                    slug="knyhy"
                ),
                CategoryCreate(
                    name="Sports",
                    description="Sports equipment",
                    slug="sport"
                ),
            ]
            
            created_categories = []
            for cat_data in categories_data:
                category = await category_crud.create_category(session, cat_data)
                created_categories.append(category)
                print(f"  ✓ Category created: {category.name} (ID: {category.id})")
            
            # ==================== PRODUCTS ====================
            print("\n📦 Creating products...")
            products_data = [
                ProductCreate(
                    name="Dell XPS 13 Laptop",
                    description="Powerful laptop for work",
                    price=1299.99,
                    stock=10,
                    sku="DELL-XPS-13",
                    category_id=created_categories[0].id
                ),
                ProductCreate(
                    name="iPhone 15 Pro",
                    description="Apple smartphone with exceptional quality",
                    price=999.99,
                    stock=15,
                    sku="APPLE-IP15PRO",
                    category_id=created_categories[0].id
                ),
                ProductCreate(
                    name="Classic T-shirt",
                    description="Classic cotton t-shirt",
                    price=29.99,
                    stock=50,
                    sku="TSHIRT-001",
                    category_id=created_categories[1].id
                ),
                ProductCreate(
                    name="Levis 501 Jeans",
                    description="Classic Levis jeans",
                    price=79.99,
                    stock=30,
                    sku="LEVIS-501",
                    category_id=created_categories[1].id
                ),
                ProductCreate(
                    name="Clean Code Programming",
                    description="Book about programming fundamentals",
                    price=59.99,
                    stock=20,
                    sku="BOOK-CP001",
                    category_id=created_categories[2].id
                ),
                ProductCreate(
                    name="Yoga Mat",
                    description="Professional yoga mat",
                    price=39.99,
                    stock=25,
                    sku="YOGA-MAT-001",
                    category_id=created_categories[3].id
                ),
            ]
            
            created_products = []
            for prod_data in products_data:
                product = await product_crud.create_product(session, prod_data)
                created_products.append(product)
                print(f"  ✓ Product created: {product.name} (ID: {product.id})")
            
            # ==================== ORDERS ====================
            print("\n📋 Creating orders...")
            
            # Order for user 1
            order1_data = OrderCreate(
                user_id=created_users[0].id,
                notes="Urgent delivery",
                items=[
                    OrderItemCreate(
                        product_id=created_products[0].id,
                        quantity=1,
                        unit_price=1299.99
                    ),
                    OrderItemCreate(
                        product_id=created_products[2].id,
                        quantity=2,
                        unit_price=29.99
                    ),
                ]
            )
            order1 = await order_crud.create_order(session, order1_data)
            print(f"  ✓ Order #{order1.id} created for user {created_users[0].username}")
            print(f"    - Total amount: ${order1.total_amount:.2f}")
            
            # Order for user 2
            order2_data = OrderCreate(
                user_id=created_users[1].id,
                notes="Standard delivery",
                items=[
                    OrderItemCreate(
                        product_id=created_products[1].id,
                        quantity=1,
                        unit_price=999.99
                    ),
                    OrderItemCreate(
                        product_id=created_products[4].id,
                        quantity=3,
                        unit_price=59.99
                    ),
                ]
            )
            order2 = await order_crud.create_order(session, order2_data)
            print(f"  ✓ Order #{order2.id} created for user {created_users[1].username}")
            print(f"    - Total amount: ${order2.total_amount:.2f}")
            
            # Order for user 3
            order3_data = OrderCreate(
                user_id=created_users[2].id,
                notes="No notes",
                items=[
                    OrderItemCreate(
                        product_id=created_products[3].id,
                        quantity=2,
                        unit_price=79.99
                    ),
                    OrderItemCreate(
                        product_id=created_products[5].id,
                        quantity=1,
                        unit_price=39.99
                    ),
                ]
            )
            order3 = await order_crud.create_order(session, order3_data)
            print(f"  ✓ Order #{order3.id} created for user {created_users[2].username}")
            print(f"    - Total amount: ${order3.total_amount:.2f}")
            
            print("\n✅ Database successfully seeded with test data!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise


async def main():
    """Main function."""
    try:
        print("=" * 50)
        print("  FastAPI Lab 4 - Database Initialization")
        print("=" * 50)
        
        # Seed database with data
        await seed_database()
        
        print("\n" + "=" * 50)
        print("  🎉 Initialization completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
