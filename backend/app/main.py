from fastapi import FastAPI
from .endpoints import customers_router, merchants_router, ai_query_router   # import your routers
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import customers_router, merchants_router  # import your routers
# from .endpoints import leaderboard
from .endpoints import dashboard, ai_router
from .db import init_db_from_csv

# Create FastAPI app instance with metadata
app = FastAPI(
    title="Snap Trust & Growth Dashboard API",
    description=(
        "Backend API for Hackathon 2025: Snap Trust & Growth Dashboard. "
        "Provides endpoints to calculate trust scores, loyalty tiers, "
        "and generate metrics for merchants and customers. "
        "Uses AI-based scoring algorithms to assess reliability, engagement, "
        "and overall trustworthiness of both customers and merchants."
    ),
    version="0.1",
    contact={
        "names": "Tarun Bhartiya, Harneet Chugga, Neel Khalade, Jyoti Parkash"
    }
)

# CORS for local dev (Vite)
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

@app.get("/")
def root():
    return {"message": "Backend is running"}

# Include all routers
app.include_router(customers_router.router, prefix="/customers", tags=["Customers"])
app.include_router(merchants_router.router, prefix="/merchants", tags=["Merchants"])

# Include AI query router
app.include_router(ai_query_router.router, prefix="", tags=["AI Query"])
# app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI Chat"])


@app.on_event("startup")
def startup_event() -> None:
    # Initialize SQLite DB from CSVs if needed
    init_db_from_csv()
