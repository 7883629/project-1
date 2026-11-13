import sqlite3
from collections.abc import Iterator
from db import get_db
from fastapi import APIRouter, Query, Depends
from api.service.order import OrderService
from api.schemas.order import OrderOut, ProductStats

router = APIRouter(prefix="/order", tags=["order"])
order_service = OrderService()


@router.get("/", response_model=list[OrderOut])
def get_orders(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0), min_rate: float = 0,conn: sqlite3.Connection = Depends(get_db)) -> list[OrderOut]:
    rows = order_service.get_orders_by_defect(conn,limit, offset, min_rate)
    print("查询成功了", rows)
    return rows


@router.get("/stats", response_model=list[ProductStats])
def get_orders_stats(conn: sqlite3.Connection = Depends(get_db)) -> list[ProductStats]:
    rows = order_service.get_orders_by_product(conn)
    print("查询成功了", rows)
    return rows
