from fastapi import FastAPI
from .endpoints import leaderboard

# Create FastAPI app instance with metadata
app = FastAPI(
    title="Snap Trust & Growth Dashboard API",
    description=(
        "Backend API for Hackathon 2025: Snap Trust & Growth Dashboard. "
        "Provides endpoints to calculate trust scores, loyalty tiers, "
        "and generate leaderboards for merchants and customers. "
        "Uses AI-based scoring algorithms to assess reliability, engagement, "
        "and overall trustworthiness of both customers and merchants."
    ),
    version="0.1",
    contact={
        "names": "Tarun Bhartiya, Harneet Chugga, Neel Khalade, Jyoti Parkash"
    }
)

# Include only the leaderboard router
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
