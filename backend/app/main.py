from fastapi import FastAPI
from .endpoints import customers_router, merchants_router, ai_query_router   # import your routers
from fastapi.middleware.cors import CORSMiddleware


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


# Allow all origins (development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

# Include customers router
app.include_router(customers_router.router, prefix="/customers", tags=["Customers"])

# Include merchants router
app.include_router(merchants_router.router, prefix="/merchants", tags=["Merchants"])

# Include AI query router
app.include_router(ai_query_router.router, prefix="", tags=["AI Query"])
