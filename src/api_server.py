"""
Simple API server for handling RFE creation requests

This provides a simple HTTP API that the React frontend can call to create Jira issues.
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from .jira_service import create_rfe_in_jira

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RFE API", description="API for creating RFE issues in Jira")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateRFERequest(BaseModel):
    """Request model for creating RFE"""

    rfe_content: str
    refinement_content: str
    project_key: Optional[str] = None
    issue_type: Optional[str] = "Story"
    priority: Optional[str] = "Medium"
    assignee: Optional[str] = None


class CreateRFEResponse(BaseModel):
    """Response model for RFE creation"""

    success: bool
    message: str
    issue_key: Optional[str] = None
    issue_url: Optional[str] = None
    error: Optional[str] = None


@app.post("/api/create-rfe", response_model=CreateRFEResponse)
async def create_rfe_endpoint(request: CreateRFERequest):
    """
    Create an RFE issue in Jira

    This endpoint accepts RFE content and creates a Jira issue using the direct API integration.
    """
    try:
        logger.info(f"Creating RFE for project: {request.project_key or 'default'}")

        # Call the Jira service to create the issue
        result = await create_rfe_in_jira(
            rfe_content=request.rfe_content,
            refinement_content=request.refinement_content,
            project_key=request.project_key,
            issue_type=request.issue_type,
            priority=request.priority,
            assignee=request.assignee,
        )

        return CreateRFEResponse(**result)

    except Exception as e:
        logger.error(f"Error in create_rfe_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RFE API"}


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "RFE API",
        "version": "1.0.0",
        "endpoints": {"create_rfe": "/api/create-rfe", "health": "/api/health"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api_server:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
