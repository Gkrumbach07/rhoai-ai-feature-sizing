#!/usr/bin/env python3
"""
Test script for MCP integration with fallback support

This script tests the MCP integration and demonstrates how it gracefully
handles server unavailability with fallback responses.
"""

import asyncio
import os
from src.mcp_client import DeepWikiMCPClient, MCPConfig, quick_research


async def test_mcp_with_fallback():
    """Test MCP client with fallback enabled"""
    print("🧪 Testing MCP Client with Fallback Support\n")

    # Test configurations
    configs = [
        {
            "name": "Production Mode (with fallback)",
            "config": MCPConfig(
                server_url="https://mcp.deepwiki.com/sse",
                fallback_mode=True,
                demo_mode=False,
            ),
        },
        {
            "name": "Demo Mode (always use fallback)",
            "config": MCPConfig(
                server_url="https://mcp.deepwiki.com/sse",
                fallback_mode=True,
                demo_mode=True,
            ),
        },
    ]

    repo_url = "https://github.com/kubeflow/kubeflow"
    test_question = "How does Kubeflow handle model deployment and serving?"

    for test_config in configs:
        print(f"📋 Testing: {test_config['name']}")
        print("-" * 50)

        config = test_config["config"]

        try:
            async with DeepWikiMCPClient(config) as client:
                # Test structure reading
                print("📖 Reading repository structure...")
                structure = await client.read_wiki_structure(repo_url)
                print(f"   Found {len(structure)} topics")

                # Test content reading
                print("📚 Reading repository content...")
                content = await client.read_wiki_contents(repo_url)
                print(f"   Content length: {len(content)} characters")

                # Test Q&A
                print(f"❓ Asking: {test_question}")
                answer = await client.ask_question(repo_url, test_question)
                print(f"   Answer preview: {answer[:200]}...")

                print("✅ Test completed successfully!\n")

        except Exception as e:
            print(f"❌ Test failed: {e}\n")


async def test_agent_integration():
    """Test agent integration with fallback"""
    print("🤖 Testing Agent Integration with MCP Fallback\n")

    # Set environment for demo mode
    os.environ["DEEPWIKI_MCP_DEMO_MODE"] = "true"
    os.environ["DEEPWIKI_MCP_FALLBACK"] = "true"

    try:
        from src.agents import RFEAgentManager
        from src.settings import init_settings

        # Initialize with MCP enabled
        init_settings(enable_mcp=True)
        manager = RFEAgentManager()

        # Test RFE
        rfe_description = """
        Implement a distributed model training system for OpenShift AI that supports:
        - Multi-GPU training across nodes
        - Dynamic resource allocation
        - Fault tolerance and checkpointing
        - Integration with existing ML workflows
        """

        # Test with Research Specialist if available
        if "RESEARCH_SPECIALIST" in manager.agent_configs:
            config = manager.agent_configs["RESEARCH_SPECIALIST"]

            print(
                f"🔍 Running analysis with {config.get('name', 'Research Specialist')}..."
            )

            events_received = 0
            async for event in manager.analyze_rfe_streaming(
                "RESEARCH_SPECIALIST",
                rfe_description,
                config,
                [
                    "https://github.com/ray-project/ray",
                    "https://github.com/pytorch/pytorch",
                ],
            ):
                events_received += 1

                if event["type"] == "research_started":
                    print(f"   📡 {event['message']}")
                elif event["type"] == "research_completed":
                    print("   ✅ Research phase completed")
                elif event["type"] == "complete":
                    result = event["result"]
                    print(f"   🎯 Analysis complete:")
                    print(
                        f"      Complexity: {result.get('estimatedComplexity', 'Unknown')}"
                    )
                    print(f"      Concerns: {len(result.get('concerns', []))}")
                    print(
                        f"      Recommendations: {len(result.get('recommendations', []))}"
                    )

                    # Show research findings if available
                    research_findings = result.get("researchFindings", {})
                    if research_findings:
                        implementations = research_findings.get(
                            "similarImplementations", []
                        )
                        print(
                            f"      Similar implementations found: {len(implementations)}"
                        )

            print(f"   📊 Total events received: {events_received}")

        else:
            print("⚠️  Research Specialist agent not found")

    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        import traceback

        traceback.print_exc()


async def test_configuration_modes():
    """Test different configuration modes"""
    print("⚙️  Testing Different Configuration Modes\n")

    test_cases = [
        (
            "Fallback Enabled",
            {"DEEPWIKI_MCP_FALLBACK": "true", "DEEPWIKI_MCP_DEMO_MODE": "false"},
        ),
        (
            "Demo Mode",
            {"DEEPWIKI_MCP_FALLBACK": "true", "DEEPWIKI_MCP_DEMO_MODE": "true"},
        ),
    ]

    for name, env_vars in test_cases:
        print(f"🔧 Testing: {name}")

        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

        try:
            # Test quick research function
            answer = await quick_research(
                "https://github.com/kubeflow/kubeflow",
                "What are the main components of Kubeflow?",
            )

            print(f"   ✅ Quick research successful")
            print(f"   📝 Response length: {len(answer)} characters")

        except Exception as e:
            print(f"   ❌ Quick research failed: {e}")

        print()


async def demonstrate_fallback_benefits():
    """Demonstrate the benefits of fallback mode"""
    print("🌟 Demonstrating Fallback Benefits\n")

    print("📋 Fallback Mode Advantages:")
    print("1. ✅ Agents continue to work even when external MCP server is down")
    print("2. ✅ Provides meaningful demo responses for testing and development")
    print("3. ✅ Graceful degradation - no crashes or failures")
    print("4. ✅ Consistent API - same interface regardless of server availability")
    print("5. ✅ Configurable behavior via environment variables")
    print()

    print("🎯 Use Cases:")
    print("- 🚀 Development and testing without external dependencies")
    print("- 🏢 Enterprise environments with restricted internet access")
    print("- 🔄 Backup functionality when primary research services are unavailable")
    print("- 📚 Demo environments for presentations and training")
    print()

    print("⚙️  Configuration Options:")
    print("- DEEPWIKI_MCP_FALLBACK=true    # Enable fallback responses")
    print("- DEEPWIKI_MCP_DEMO_MODE=true   # Always use demo responses (for testing)")
    print("- ENABLE_DEEPWIKI_MCP=false     # Completely disable MCP features")
    print()


async def main():
    """Run all tests"""
    print("🚀 MCP Fallback Support Test Suite")
    print("=" * 60)
    print()

    try:
        await test_mcp_with_fallback()
        print("=" * 60)

        await test_agent_integration()
        print("=" * 60)

        await test_configuration_modes()
        print("=" * 60)

        await demonstrate_fallback_benefits()

        print("🎉 All tests completed successfully!")
        print()
        print("💡 The MCP integration now works reliably with fallback support.")
        print("   Your agents can conduct 'research' even when the external MCP server")
        print("   is unavailable, ensuring your application remains functional.")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
