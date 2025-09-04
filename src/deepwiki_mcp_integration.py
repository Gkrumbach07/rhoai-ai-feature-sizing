#!/usr/bin/env python3
"""
DeepWiki MCP Integration Example

This script demonstrates how to use the DeepWiki MCP server integration
for enhanced agent research capabilities.
"""

import asyncio
import json
from typing import List, Dict, Any

from src.agents import RFEAgentManager
from src.settings import init_settings
from src.mcp_client import quick_research, get_repo_overview


async def example_basic_mcp_usage():
    """Example of basic MCP functionality"""
    print("🚀 Testing basic DeepWiki MCP functionality...\n")

    repo_url = "https://github.com/kubeflow/kubeflow"

    # Quick research example
    question = "How does Kubeflow handle model serving and deployment?"
    print(f"Question: {question}")
    print("Researching...")

    try:
        answer = await quick_research(repo_url, question)
        print(f"Answer: {answer[:500]}...\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Repository overview example
    print("Getting repository overview...")
    try:
        overview = await get_repo_overview(repo_url)
        print(f"Repository structure: {len(overview.get('structure', []))} topics")
        print(f"Content length: {len(overview.get('content', ''))} characters\n")
    except Exception as e:
        print(f"Error: {e}\n")


async def example_agent_research():
    """Example of enhanced agent analysis with MCP research"""
    print("🤖 Testing enhanced agent analysis with MCP research...\n")

    # Initialize settings with MCP enabled
    init_settings(enable_mcp=True)

    # Create agent manager
    manager = RFEAgentManager()

    # Example RFE
    rfe_description = """
    Implement a new model versioning system for OpenShift AI that supports:
    - Automatic version tracking for ML models
    - Integration with existing model registry
    - Support for A/B testing of different model versions
    - Performance monitoring and rollback capabilities
    """

    # Research repositories specific to this RFE
    research_repos = [
        "https://github.com/mlflow/mlflow",
        "https://github.com/kubeflow/kubeflow",
        "https://github.com/bentoml/BentoML",
    ]

    # Test with Research Specialist agent
    if "RESEARCH_SPECIALIST" in manager.agent_configs:
        config = manager.agent_configs["RESEARCH_SPECIALIST"]

        print(f"Running analysis with {config.get('name', 'Research Specialist')}...")

        async for event in manager.analyze_rfe_streaming(
            "RESEARCH_SPECIALIST", rfe_description, config, research_repos
        ):
            if event["type"] == "research_started":
                print(f"🔬 {event['message']}")
            elif event["type"] == "research_completed":
                print("✅ Research completed!")
                research_data = event.get("research_data", {})
                repos_researched = len(research_data.get("repositories", {}))
                print(f"   Researched {repos_researched} repositories")
            elif event["type"] == "complete":
                print("🎯 Analysis complete!")
                result = event["result"]
                print(f"   Complexity: {result.get('estimatedComplexity', 'Unknown')}")
                print(f"   Recommendations: {len(result.get('recommendations', []))}")
                print(
                    f"   Research findings: {len(result.get('researchFindings', {}).get('similarImplementations', []))}"
                )
    else:
        print(
            "❌ Research Specialist agent not found. Make sure research_specialist.yaml is loaded."
        )


async def example_multi_agent_research():
    """Example of multi-agent analysis with different research focuses"""
    print("🎭 Testing multi-agent analysis with specialized research...\n")

    init_settings(enable_mcp=True)
    manager = RFEAgentManager()

    rfe_description = """
    Add support for distributed model training using Ray on OpenShift AI platform
    """

    # Different research repos for different agent perspectives
    research_configs = {
        "STAFF_ENGINEER": [
            "https://github.com/ray-project/ray",
            "https://github.com/pytorch/pytorch",
        ],
        "ENGINEERING_MANAGER": [
            "https://github.com/kubeflow/training-operator",
            "https://github.com/ray-project/kuberay",
        ],
        "RESEARCH_SPECIALIST": [
            "https://github.com/ray-project/ray",
            "https://github.com/ray-project/kuberay",
            "https://github.com/pytorch/pytorch",
        ],
    }

    results = {}

    for persona, repos in research_configs.items():
        if persona in manager.agent_configs:
            print(f"🤖 Running {persona} analysis...")

            config = manager.agent_configs[persona]

            async for event in manager.analyze_rfe_streaming(
                persona, rfe_description, config, repos
            ):
                if event["type"] == "complete":
                    results[persona] = event["result"]
                    print(f"✅ {persona} completed")

    # Display summary
    print("\n📊 Multi-Agent Analysis Summary:")
    for persona, result in results.items():
        print(f"\n{persona}:")
        print(f"  Complexity: {result.get('estimatedComplexity', 'Unknown')}")
        print(f"  Key Concerns: {len(result.get('concerns', []))}")
        print(f"  Recommendations: {len(result.get('recommendations', []))}")


async def example_custom_research():
    """Example of custom research for specific use cases"""
    print("🔍 Testing custom research scenarios...\n")

    from src.mcp_client import MCPResearchService, get_mcp_config

    config = get_mcp_config()
    research_service = MCPResearchService(config)

    # Custom research questions for different domains
    research_scenarios = [
        {
            "name": "Security Research",
            "repos": ["https://github.com/kubeflow/kubeflow"],
            "questions": [
                "What security best practices are implemented?",
                "How is authentication and authorization handled?",
                "What are the known security vulnerabilities?",
            ],
        },
        {
            "name": "Performance Research",
            "repos": ["https://github.com/ray-project/ray"],
            "questions": [
                "What are the performance optimization strategies?",
                "How is resource utilization managed?",
                "What are the scalability limits?",
            ],
        },
    ]

    for scenario in research_scenarios:
        print(f"📋 {scenario['name']}:")

        for repo_url in scenario["repos"]:
            results = await research_service.research_repositories(
                [repo_url], scenario["questions"]
            )

            repo_data = results.get(repo_url, {})
            if "error" not in repo_data:
                print(f"  ✅ {repo_url}")
                qa_results = repo_data.get("qa_results", {})
                for question, answer in qa_results.items():
                    print(f"    Q: {question}")
                    print(f"    A: {answer[:150]}...")
            else:
                print(f"  ❌ {repo_url}: {repo_data['error']}")
        print()


async def main():
    """Run all examples"""
    print("🌟 DeepWiki MCP Integration Examples\n")
    print("=" * 50)

    try:
        await example_basic_mcp_usage()
        print("=" * 50)

        await example_agent_research()
        print("=" * 50)

        await example_multi_agent_research()
        print("=" * 50)

        await example_custom_research()

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback

        traceback.print_exc()

    print("🏁 Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
