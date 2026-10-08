from pydantic import BaseModel, Field, ConfigDict

class ProductCreate(BaseModel):
        sku : str = Field(
                description="The SKU must be filled out in the format: name-series (using a hyphen)"
        )
        name : str = Field(
                min_length=3,
                max_length=30,
                description="User name"
        )
        description : str | None = None
        price : int = Field(
                gt=0,
                description="Price must be greater than 0"
        )
        stock : int = Field(
                ge=0,
                default=1,
                description="Stock can't be zero or negatif"
        )
        status : bool = Field(
                default=False,
                description="Product status active/inactive as True/False"
        )




class ORMSchema(BaseModel):
        """Base schema agar bisa dibuat dari objek ORM."""

        model_config = ConfigDict(from_attributes=True)


class ProductResponse(ORMSchema):
        id: int
        sku: str
        name: str
        description: str
        price: int
        stock: int
        status: bool

class ProductStockUpdate(BaseModel):
        stock : int 

class ProductUpdate(BaseModel):
        name : str | None = None
        description : str | None = None
        price : int | None = None
        status : bool | None = None

