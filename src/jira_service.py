"""
Jira Service for creating RFE issues

This module provides functionality to create RFE issues in Jira using direct API calls.
"""

import os
import json
import logging
import aiohttp
import base64
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class JiraRFERequest:
    """Data structure for RFE creation request"""

    rfe_content: str
    refinement_content: str
    project_key: Optional[str] = None
    issue_type: str = "Story"
    priority: str = "Medium"


class JiraRFEService:
    """Service for creating RFE issues in Jira using direct API calls"""

    def __init__(self):
        self.jira_url = os.getenv("JIRA_BASE_URL", "https://issues.redhat.com")
        self.project_key = os.getenv("JIRA_PROJECT_KEY", "RHOAI")
        self.username = os.getenv("JIRA_USERNAME")
        self.api_token = os.getenv("JIRA_API_TOKEN")

        if not self.username or not self.api_token:
            logger.warning(
                "Jira credentials not configured. Set JIRA_USERNAME and JIRA_API_TOKEN environment variables."
            )

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Jira API"""
        if not self.username or not self.api_token:
            return {}

        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _extract_title_from_rfe(self, rfe_content: str) -> str:
        """Extract a title from the RFE content"""
        # Look for first heading or first line
        lines = rfe_content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            elif line.startswith("## "):
                return line[3:].strip()
            elif line and not line.startswith("#"):
                # Use first non-empty, non-comment line as title
                return line[:100] + "..." if len(line) > 100 else line

        return "RFE - Feature Enhancement Request"

    def _prepare_description(self, rfe_content: str, refinement_content: str) -> str:
        """Prepare the Jira issue description from RFE content"""
        description = "h1. Request for Enhancement (RFE)\n\n"

        if rfe_content:
            description += "h2. RFE Description\n\n"
            description += rfe_content + "\n\n"

        if refinement_content:
            description += "h2. Feature Refinement\n\n"
            description += refinement_content + "\n\n"

        description += (
            "----\n_This RFE was generated using the AI Feature Sizing tool._"
        )

        return description

    async def create_rfe_issue(self, rfe_request: JiraRFERequest) -> Dict[str, Any]:
        """
        Create an RFE issue in Jira using direct API calls

        Args:
            rfe_request: The RFE creation request data

        Returns:
            Dict containing the created issue information or error details
        """
        if not self.username or not self.api_token:
            return {
                "success": False,
                "error": "Jira credentials not configured",
                "message": "Please configure JIRA_USERNAME and JIRA_API_TOKEN environment variables",
            }

        try:
            # Extract title and prepare description
            title = self._extract_title_from_rfe(rfe_request.rfe_content)
            description = self._prepare_description(
                rfe_request.rfe_content, rfe_request.refinement_content
            )

            # Prepare Jira issue data
            project_key = rfe_request.project_key or self.project_key

            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": title,
                    "description": description,
                    "issuetype": {"name": rfe_request.issue_type},
                    "priority": {"name": rfe_request.priority},
                    "labels": ["rfe", "ai-generated", "feature-request"],
                }
            }

            # Add if specified

            # Make API call to create issue
            async with aiohttp.ClientSession() as session:
                url = f"{self.jira_url}/rest/api/2/issue"
                headers = self._get_auth_headers()

                async with session.post(
                    url, json=issue_data, headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        issue_key = result.get("key")

                        logger.info(f"Successfully created Jira RFE: {issue_key}")

                        return {
                            "success": True,
                            "issue_key": issue_key,
                            "issue_url": f"{self.jira_url}/browse/{issue_key}",
                            "message": f"RFE created successfully: {issue_key}",
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Failed to create Jira issue: HTTP {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "message": f"Failed to create RFE in Jira: {error_text}",
                        }

        except Exception as e:
            logger.error(f"Error creating Jira RFE: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create RFE due to unexpected error",
            }


# Convenience function for direct usage
async def create_rfe_in_jira(
    rfe_content: str,
    refinement_content: str,
    project_key: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to create an RFE in Jira

    Args:
        rfe_content: The main RFE content
        refinement_content: The feature refinement content
        project_key: Jira project key (optional)
        **kwargs: Additional options (issue_type, priority)

    Returns:
        Dict with creation result
    """
    service = JiraRFEService()
    request = JiraRFERequest(
        rfe_content=rfe_content,
        refinement_content=refinement_content,
        project_key=project_key,
        **kwargs,
    )

    return await service.create_rfe_issue(request)
