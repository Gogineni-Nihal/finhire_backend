from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import admin, auth, bookings, cas, expenses, financial_tools, users
from .seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="FinHire API",
    description="REST API for hiring Chartered Accountants and managing basic finances.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):(5173|8081|19006)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(cas.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(financial_tools.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": "FinHire API",
        "status": "running",
        "docs": "/docs",
        "demo_accounts": {
            "user": "user@finhire.demo / password123",
            "ca": "ca@finhire.demo / password123",
            "admin": "admin@finhire.demo / admin123",
        },
    }
