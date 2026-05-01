
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from agent_framework import Agent, WorkflowBuilder, WorkflowContext, Executor, handler
from agent_framework.openai import OpenAIChatClient
from agent_framework import MCPStreamableHTTPTool
from agent_framework.devui import serve

# Suppress noisy framework-level warnings (from_str empty cache, annotation hints)
logging.getLogger("agent_framework").setLevel(logging.ERROR)

load_dotenv()


# ─────────────────────────────────────────────
# Shared Azure OpenAI client factory (confirmed working)
# ─────────────────────────────────────────────
def make_client() -> OpenAIChatClient:
    endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    return OpenAIChatClient(
        model=deployment,
        base_url=f"{endpoint}/openai/v1/",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2025-01-01-preview",
    )


# ─────────────────────────────────────────────
# Dispatcher Executor — START NODE
# ─────────────────────────────────────────────
class DispatcherExecutor(Executor):
    def __init__(self):
        super().__init__(id="dispatcher")

    @handler
    async def dispatch(self, topic: str, ctx: WorkflowContext) -> None:
        print(f"\n📡 Dispatcher received topic: '{topic}'")
        print("   └─ Forwarding to PubMed & ClinicalTrials agents in parallel...\n")
        await ctx.send_message(topic)


# ─────────────────────────────────────────────
# Agent Definitions
# ─────────────────────────────────────────────
def create_pubmed_agent() -> Agent:
    pubmed_tool = MCPStreamableHTTPTool(
        name="pubmed_mcp",
        url="https://pubmed.caseyjhand.com/mcp",
        description="PubMed search and biomedical literature tools",
        tool_name_prefix="pmxx_",
    )
    return Agent(
        name="PubMedSearchAgent",
        instructions="""
        You are a biomedical research expert specializing in PubMed literature searches.
        Search PubMed for articles related to the given topic.
        - Use the pubmed_search_articles tool to find relevant papers
        - Extract key information: PMIDs, titles, authors, years
        Format your response as:
        PUBMED_RESULTS:
        [List of PMIDs with brief context]
        """,
        client=make_client(),
        tools=[pubmed_tool],
    )


def create_clinical_trials_agent() -> Agent:
    trials_tool = MCPStreamableHTTPTool(
        name="clinical_trials_mcp",
        url="https://clinicaltrials.caseyjhand.com/mcp",
        description="Clinical trials search and information tools",
        tool_name_prefix="ctxx_",
    )
    return Agent(
        name="ClinicalTrialsSearchAgent",
        instructions="""
        You are a clinical trials expert specializing in finding relevant studies.
        Search for clinical trials related to the given topic.
        - Extract key information: Trial IDs, statuses, phases, conditions
        Format your response as:
        CLINICAL_TRIALS_RESULTS:
        [List of trials with key details]
        """,
        client=make_client(),
        tools=[trials_tool],
    )


def create_summarizer_agent() -> Agent:
    return Agent(
        name="SummarizerAgent",
        instructions="""
        You are an expert medical synthesizer and summarizer.
        You will receive combined output from a PubMed agent and a Clinical Trials agent.
        Create a comprehensive summary structured as:
        📚 Recent Research Findings
        🔬 Ongoing Clinical Trials
        💡 Key Insights & Opportunities
        📌 Summary
        """,
        client=make_client(),
        tools=[],
    )


# ─────────────────────────────────────────────
# Build the WorkflowBuilder Graph
# ─────────────────────────────────────────────
def build_research_workflow():
    """
    Topology:
        [Input]
           │
       Dispatcher          <- start_executor
      ┌────┴────┐          <- fan-out (2 add_edge calls)
      ▼         ▼
   PubMed   ClinicalTrials
      │         │
      └────┬────┘          <- fan-in (2 add_edge calls)
           ▼
       Summarizer           <- yields final output
    """
    dispatcher = DispatcherExecutor()
    pubmed     = create_pubmed_agent()
    trials     = create_clinical_trials_agent()
    summarizer = create_summarizer_agent()

    workflow = (
        WorkflowBuilder(start_executor=dispatcher)
        .add_edge(dispatcher, pubmed)       # fan-out edge 1
        .add_edge(dispatcher, trials)       # fan-out edge 2
        .add_edge(pubmed,     summarizer)   # fan-in edge 1
        .add_edge(trials,     summarizer)   # fan-in edge 2
        .build()
    )
    return workflow


# ─────────────────────────────────────────────
# DevUI mode — browser-based interactive UI
# Run with: python multiagent_workflow.py --devui
# ─────────────────────────────────────────────
def run_devui(port: int = 8080):
    print("\n" + "=" * 70)
    print("🖥️  Launching DevUI — Multi-Agent Research System")
    print("=" * 70)
    print(f"\n  URL     : http://127.0.0.1:{port}")
    print(  "  Workflow: Dispatcher -> [PubMed ║ ClinicalTrials] -> Summarizer")
    print(  "  Mode    : Developer (full debug traces)")
    print(  "\n  Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    workflow = build_research_workflow()

    serve(
        entities=[workflow],
        port=port,
        host="127.0.0.1",
        auto_open=True,
        ui_enabled=True,
        mode="developer",
    )


# ─────────────────────────────────────────────
# CLI mode — interactive terminal loop
# Run with: python multiagent_workflow.py
# ─────────────────────────────────────────────
async def main():
    print("\n" + "=" * 70)
    print("🏥 Multi-Agent Research System — Powered by WorkflowBuilder")
    print("=" * 70)
    print("\n📋 Topology: Input -> Dispatcher -> [PubMed ║ ClinicalTrials] -> Summarizer\n")
    print("Commands:")
    print("  - Type a research topic to start")
    print("  - Examples: 'cancer immunotherapy', 'diabetes treatment'")
    print("  - exit / quit to stop")
    print("=" * 70 + "\n")

    workflow = build_research_workflow()

    try:
        while True:
            try:
                user_input = input("Research Topic: ").strip()
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\nGoodbye! 👋")
                    break
                if not user_input:
                    continue

                print(f"\n🚀 Running workflow for: '{user_input}'\n")

                events  = await workflow.run(user_input)
                outputs = events.get_outputs()
                summary = outputs[-1] if outputs else "No summary generated."

                print(f"\n{'=' * 70}")
                print("📊 FINAL SUMMARY")
                print(f"{'=' * 70}")
                print(summary)
                print(f"{'=' * 70}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Allow MCP streamable_http async generators to finalize cleanly
        await asyncio.sleep(0.5)
        try:
            loop = asyncio.get_event_loop()
            await loop.shutdown_asyncgens()
        except Exception:
            pass


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if "--devui" in sys.argv:
        port = 8080
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        run_devui(port=port)
    else:
        asyncio.run(main())
