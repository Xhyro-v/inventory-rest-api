from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.products.models import Product  # sesuaikan path model project Anda
from app.paginations.repositories import (
    BaseRepository,
    OrderRepository,
    ModelT,
    ProductRepository,
)
from app.paginations.schemas import (
    PaginatedResponse,
    PaginationMeta,
)

from app.products.schemas import ProductResponse

SchemaT = TypeVar("SchemaT", bound=BaseModel)


# ======================= GENERIK =======================
class BaseService(Generic[ModelT, SchemaT]):
    schema: type[SchemaT]  # wajib diisi oleh subclass

    def __init__(self, repository: BaseRepository[ModelT]) -> None:
        self.repository = repository

    def paginate(self, page: int, limit: int, filters=()) -> PaginatedResponse[SchemaT]:
        offset = (page - 1) * limit
        items, total = self.repository.get_paginated(offset, limit, filters)

        return PaginatedResponse(
            data=[self.schema.model_validate(item) for item in items],
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=ceil(total / limit) if total else 0,
            ),
        )


# ======================= PER RESOURCE =======================
class ProductService(BaseService[Product, ProductResponse]):
    schema = ProductResponse

    def __init__(self, repository: ProductRepository) -> None:
        super().__init__(repository)


# class CustomerService(BaseService[Customer, CustomerResponse]):
#     schema = CustomerResponse

#     def __init__(self, repository: CustomerRepository) -> None:
#         super().__init__(repository)