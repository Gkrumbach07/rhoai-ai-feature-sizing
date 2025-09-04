"""
DeepWiki MCP (Model Context Protocol) Client

This module provides a client interface to the DeepWiki MCP server for
agents to conduct enhanced research on GitHub repositories.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPConfig:
    """Configuration for MCP server connection"""

    server_url: str = "https://mcp.deepwiki.com/sse"
    protocol: str = "sse"  # or "mcp" for streamable HTTP
    timeout: int = 30
    max_retries: int = 3
    fallback_mode: bool = True  # Enable fallback when MCP server unavailable
    demo_mode: bool = False  # Use demo responses for testing


class DeepWikiMCPClient:
    """Client for interacting with DeepWiki MCP server"""

    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.mcp_available = None  # Track server availability

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _check_server_availability(self) -> bool:
        """Check if MCP server is available"""
        if self.mcp_available is not None:
            return self.mcp_available

        try:
            async with self.session.get(
                self.config.server_url.replace("/sse", "/health")
            ) as response:
                self.mcp_available = response.status == 200
        except:
            self.mcp_available = False

        return self.mcp_available

    def _get_demo_response(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return demo responses for testing when MCP server unavailable"""
        repo_url = arguments.get("repo_url", "")
        repo_name = repo_url.split("/")[-1] if repo_url else "repository"

        if tool_name == "read_wiki_structure":
            return {
                "topics": [
                    {"title": "Getting Started", "path": "getting-started"},
                    {"title": "Architecture", "path": "architecture"},
                    {"title": "API Reference", "path": "api-reference"},
                    {"title": "Contributing", "path": "contributing"},
                ]
            }
        elif tool_name == "read_wiki_contents":
            return {
                "content": f"""
# {repo_name} Documentation

## Overview
This is a demo response for {repo_name}. The actual MCP server is not available.

## Key Features
- Modern architecture and design patterns
- Comprehensive API and SDK support
- Scalable deployment options
- Active community and development

## Getting Started
1. Clone the repository
2. Install dependencies
3. Configure the application
4. Run the application

Note: This is a fallback response when the DeepWiki MCP server is unavailable.
"""
            }
        elif tool_name == "ask_question":
            question = arguments.get("question", "")
            return {
                "answer": f"""
Based on the repository {repo_name} and your question "{question}", here's a demo response:

This appears to be a well-structured project following modern software engineering practices. 
The architecture likely uses microservices patterns with containerized deployments. 
For implementation, consider following the established patterns in the codebase and 
consulting the documentation for specific integration requirements.

Note: This is a fallback response. For accurate information, please ensure the 
DeepWiki MCP server is properly configured and accessible.
"""
            }

        return {}

    async def _make_request(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a request to the MCP server with fallback support"""
        if not self.session:
            raise RuntimeError(
                "Client session not initialized. Use async context manager."
            )

        # Use demo mode if configured
        if self.config.demo_mode:
            logger.info(f"Using demo response for {tool_name}")
            return self._get_demo_response(tool_name, arguments)

        # Check server availability
        server_available = await self._check_server_availability()
        if not server_available and self.config.fallback_mode:
            logger.warning(f"MCP server unavailable, using fallback for {tool_name}")
            return self._get_demo_response(tool_name, arguments)

        payload = {
            "jsonrpc": "2.0",
            "id": f"{tool_name}_{hash(str(arguments))}",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(
                    self.config.server_url, json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "error" in result:
                            raise Exception(f"MCP Server Error: {result['error']}")
                        self.mcp_available = True
                        return result.get("result", {})
                    else:
                        logger.warning(
                            f"HTTP {response.status} on attempt {attempt + 1}"
                        )

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")

            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2**attempt)  # Exponential backoff

        # If all attempts failed and fallback is enabled, use demo response
        if self.config.fallback_mode:
            logger.warning(f"All requests failed, using fallback for {tool_name}")
            self.mcp_available = False
            return self._get_demo_response(tool_name, arguments)

        raise Exception(
            f"Failed to complete request after {self.config.max_retries} attempts"
        )

    async def read_wiki_structure(self, repo_url: str) -> List[Dict[str, Any]]:
        """
        Retrieve documentation topics for a GitHub repository

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/user/repo')

        Returns:
            List of documentation topics with metadata
        """
        try:
            result = await self._make_request(
                "read_wiki_structure", {"repo_url": repo_url}
            )
            return result.get("topics", [])
        except Exception as e:
            logger.error(f"Failed to read wiki structure for {repo_url}: {e}")
            return []

    async def read_wiki_contents(
        self, repo_url: str, topic: Optional[str] = None
    ) -> str:
        """
        Fetch documentation content for a GitHub repository

        Args:
            repo_url: GitHub repository URL
            topic: Specific topic to read (optional)

        Returns:
            Documentation content as string
        """
        try:
            arguments = {"repo_url": repo_url}
            if topic:
                arguments["topic"] = topic

            result = await self._make_request("read_wiki_contents", arguments)
            return result.get("content", "")
        except Exception as e:
            logger.error(f"Failed to read wiki contents for {repo_url}: {e}")
            return ""

    async def ask_question(self, repo_url: str, question: str) -> str:
        """
        Ask a question about a GitHub repository using AI

        Args:
            repo_url: GitHub repository URL
            question: Question to ask about the repository

        Returns:
            AI-powered response with context from the repository
        """
        try:
            result = await self._make_request(
                "ask_question", {"repo_url": repo_url, "question": question}
            )
            return result.get("answer", "")
        except Exception as e:
            logger.error(f"Failed to ask question for {repo_url}: {e}")
            return ""


class MCPResearchService:
    """Service for conducting research using MCP client"""

    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig()

    async def research_repositories(
        self, repo_urls: List[str], research_questions: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Conduct comprehensive research across multiple repositories

        Args:
            repo_urls: List of GitHub repository URLs
            research_questions: List of questions to research

        Returns:
            Dict mapping repo URLs to research results
        """
        results = {}

        async with DeepWikiMCPClient(self.config) as client:
            for repo_url in repo_urls:
                logger.info(f"Researching repository: {repo_url}")

                repo_results = {"structure": [], "content": "", "qa_results": {}}

                try:
                    # Get repository structure
                    repo_results["structure"] = await client.read_wiki_structure(
                        repo_url
                    )

                    # Get general content
                    repo_results["content"] = await client.read_wiki_contents(repo_url)

                    # Ask research questions
                    for question in research_questions:
                        answer = await client.ask_question(repo_url, question)
                        repo_results["qa_results"][question] = answer

                except Exception as e:
                    logger.error(f"Error researching {repo_url}: {e}")
                    repo_results["error"] = str(e)

                results[repo_url] = repo_results

        return results

    async def focused_research(
        self, repo_url: str, persona: str, rfe_description: str
    ) -> Dict[str, Any]:
        """
        Conduct focused research for a specific agent persona

        Args:
            repo_url: GitHub repository URL
            persona: Agent persona (e.g., "STAFF_ENGINEER")
            rfe_description: RFE description to research

        Returns:
            Focused research results for the persona
        """
        # Define persona-specific research questions
        persona_questions = {
            "STAFF_ENGINEER": [
                "What are the main technical architecture patterns used?",
                "What are the performance optimization strategies?",
                "What testing frameworks and patterns are implemented?",
                "What are the security best practices followed?",
            ],
            "ENGINEERING_MANAGER": [
                "What is the team organization and development process?",
                "What are the CI/CD and deployment practices?",
                "How is code quality ensured?",
                "What are the main dependencies and integration points?",
            ],
            "UX_ARCHITECT": [
                "What user interface patterns and frameworks are used?",
                "How is user experience designed and tested?",
                "What accessibility standards are followed?",
                "What are the user interaction patterns?",
            ],
        }

        questions = persona_questions.get(
            persona,
            [
                "What are the main features and capabilities?",
                "What are the key technical requirements?",
                "What are the main implementation patterns?",
            ],
        )

        # Add RFE-specific question
        rfe_question = f"How would you implement or approach: {rfe_description}"
        questions.append(rfe_question)

        async with DeepWikiMCPClient(self.config) as client:
            results = {
                "repo_url": repo_url,
                "persona": persona,
                "rfe_description": rfe_description,
                "structure": [],
                "research_results": {},
            }

            try:
                # Get repository structure for context
                results["structure"] = await client.read_wiki_structure(repo_url)

                # Ask persona-specific questions
                for question in questions:
                    answer = await client.ask_question(repo_url, question)
                    results["research_results"][question] = answer

            except Exception as e:
                logger.error(f"Error in focused research for {repo_url}: {e}")
                results["error"] = str(e)

            return results


def get_mcp_config() -> MCPConfig:
    """Get MCP configuration from environment variables"""
    return MCPConfig(
        server_url=os.getenv("DEEPWIKI_MCP_URL", "https://mcp.deepwiki.com/sse"),
        protocol=os.getenv("DEEPWIKI_MCP_PROTOCOL", "sse"),
        timeout=int(os.getenv("DEEPWIKI_MCP_TIMEOUT", "30")),
        max_retries=int(os.getenv("DEEPWIKI_MCP_MAX_RETRIES", "3")),
        fallback_mode=os.getenv("DEEPWIKI_MCP_FALLBACK", "true").lower() == "true",
        demo_mode=os.getenv("DEEPWIKI_MCP_DEMO_MODE", "false").lower() == "true",
    )


# Convenience functions for direct usage
async def quick_research(repo_url: str, question: str) -> str:
    """Quick research function for single question"""
    config = get_mcp_config()
    async with DeepWikiMCPClient(config) as client:
        return await client.ask_question(repo_url, question)


async def get_repo_overview(repo_url: str) -> Dict[str, Any]:
    """Get complete repository overview"""
    config = get_mcp_config()
    async with DeepWikiMCPClient(config) as client:
        return {
            "structure": await client.read_wiki_structure(repo_url),
            "content": await client.read_wiki_contents(repo_url),
        }
