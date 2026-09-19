from .models import User
from app.inventory.models import StockHistory  # <-- missing import is the usual culprit
from app.orders.models import Order, OrderHistory