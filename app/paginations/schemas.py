from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

        
class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta


# class ORMSchema(BaseModel):
#     """Base schema agar bisa dibuat dari objek ORM."""

#     model_config = ConfigDict(from_attributes=True)


# # ======================= PER RESOURCE =======================
# class ProductResponse(ORMSchema):
#     id: int
#     sku: str
#     name: str
#     category: str
#     price: int
#     stock: int
#     is_active: bool


# class CustomerResponse(ORMSchema):  # contoh resource ke-2, hapus jika tidak perlu
#     id: int
#     name: str
#     email: str
#     phone: str | None = None