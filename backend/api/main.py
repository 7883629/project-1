from fastapi import FastAPI
from api.router.chat import router as chat_router
from api.router.order import router as order_router

app = FastAPI(title="AI product Assistant")

app.include_router(chat_router)
app.include_router(order_router)