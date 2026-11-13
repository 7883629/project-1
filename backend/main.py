from fastapi import FastAPI
from api.router.chat import router as chat_router
from api.router.order import router as order_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI product Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)

app.include_router(order_router)