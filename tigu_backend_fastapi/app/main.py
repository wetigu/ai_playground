from fastapi import FastAPI
from app.core.config import settings
# from app.api.v1.api import api_router # Assuming you create this aggregator

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Placeholder for root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Include your API routers here
# app.include_router(api_router, prefix=settings.API_V1_STR)

# Example: Add a simple health check endpoint
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
