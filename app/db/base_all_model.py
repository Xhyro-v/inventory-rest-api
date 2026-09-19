# app/db/base_all_models.py  (atau app/models/__init__.py)
# Import SEMUA model di sini, urutan tidak masalah
from app.auth.models import User
from app.customers.models import Customer
from app.products.models import Product
from app.inventory.models import StockHistory
from app.orders.models import Order, OrderItem, OrderHistory

# Ini penting agar semua class ter-daftar di Base.registry