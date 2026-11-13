from pydantic import BaseModel


class OrderOut(BaseModel):
    id: int
    product: str
    total_qty: int
    defect_qty: int
    defect_rate_pct: float


class ProductStats(BaseModel):
    product: str
    order_count: int
    defect_rate_pct: float