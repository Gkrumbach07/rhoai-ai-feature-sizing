#!/usr/bin/env python3
"""
Start the RFE API server

This script starts the FastAPI server for handling RFE creation requests from the React frontend.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Start the API server"""
    port = int(os.getenv("API_PORT", 8001))
    host = os.getenv("API_HOST", "0.0.0.0")

    print(f"🚀 Starting RFE API server on {host}:{port}")
    print(f"📋 Jira URL: {os.getenv('JIRA_BASE_URL', 'Not configured')}")
    print(f"🎯 Project: {os.getenv('JIRA_PROJECT_KEY', 'Not configured')}")

    # Check if Jira credentials are configured
    if not os.getenv("JIRA_USERNAME") or not os.getenv("JIRA_API_TOKEN"):
        print("⚠️  WARNING: Jira credentials not configured!")
        print("   Set JIRA_USERNAME and JIRA_API_TOKEN in your .env file")

    uvicorn.run(
        "src.api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
