from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

# Model diimport dari project Anda (sesuaikan path-nya)
from app.products.models import Product
from app.orders.models import OrderHistory
from app.inventory.models import StockHistory

# ======================= GENERIK =======================
ModelT = TypeVar("ModelT")  # model ORM apa pun yang punya kolom `id`


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]  # wajib diisi oleh subclass

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_paginated(
        self,
        offset: int,
        limit: int,
        filters: Sequence[ColumnElement[bool]] = (),
    ) -> tuple[list[ModelT], int]:
        """Return (items, total). `filters` opsional, contoh: [Product.is_active.is_(True)]"""
        total = (
            self.db.scalar(
                select(func.count()).select_from(self.model).where(*filters)
            )
            or 0
        )
        items = self.db.scalars(
            select(self.model)
            .where(*filters)
            .order_by(self.model.id)  # urutan stabil wajib untuk pagination
            .offset(offset)
            .limit(limit)
        ).all()
        return list(items), total


# ======================= PER RESOURCE =======================
class ProductRepository(BaseRepository[Product]):
    model = Product


class OrderRepository(BaseRepository[OrderHistory]):  # contoh resource ke-2
    model = OrderHistory