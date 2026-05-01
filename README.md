# Multi‑Agent Orchestration with Microsoft Agent Framework
Multi‑Agent Research Orchestration with Microsoft Agent Framework
This repository demonstrates a fan‑out / fan‑in multi‑agent orchestration pattern built using the Microsoft Agent Framework (MAF).
It showcases how multiple specialized AI agents can run in parallel, retrieve grounded data via public MCP (Model Context Protocol) servers, and then converge into a single synthesized response.

🧠 What This Project Does
Given a medical or life‑sciences research topic (e.g. “cancer immunotherapy”), the system:

Fans the topic out to two specialized agents running in parallel
Grounds each agent using publicly hosted MCP servers
Merges the outputs into a single, structured summary

This pattern is particularly useful for research, analysis, and decision‑support scenarios where multiple perspectives must be combined deterministically.

🏗 Architecture Overview
Workflow topology (fan‑out / fan‑in):
User Input
   │
Dispatcher (start node)
   │
   ├── PubMed Research Agent ──┐
   │                           ├── Summarizer Agent → Final Output
   └── Clinical Trials Agent ──┘

Key Components


Dispatcher (Executor)

Entry point of the workflow
Broadcasts the input topic to downstream agents



PubMed Research Agent

Connects to a public PubMed MCP server
Retrieves scientific literature, papers, and metadata



Clinical Trials Agent

Connects to a public ClinicalTrials.gov MCP server
Retrieves active and historical clinical trial data



Summarizer Agent

Performs fan‑in
Synthesizes outputs from both agents into a single report




🔌 Model Context Protocol (MCP)
This project uses MCPStreamableHTTPTool to connect agents to external MCP servers over streamable HTTP.
Public MCP endpoints used:


PubMed MCP
Accesses PubMed / NCBI literature


ClinicalTrials.gov MCP
Accesses structured clinical trial data


Benefits of using MCP:

Tool‑grounded responses (reduced hallucination)
Clean separation between orchestration logic and data providers
Easy swap‑in of internal or private MCP servers later


🔁 Orchestration Pattern
Fan‑Out

A single input message is sent to multiple agents simultaneously
Agents run concurrently, each using different tools and data sources

Fan‑In

The workflow waits for all parallel agents to complete
Results are routed into a single summarization agent

This pattern is implemented directly using WorkflowBuilder.add_edge(...), without custom threading or async coordination logic.

🧪 Running the Project
Prerequisites

Python 3.10+
Microsoft Agent Framework
Azure OpenAI or OpenAI‑compatible endpoint
(Optional) Agent Framework DevUI

Install dependencies
Shellpip install agent-framework agent-framework-devui python-dotenvShow more lines
Run in CLI mode
Shellpython multiagent_workflow.pyShow more lines
Run with DevUI (browser-based debugging)
Shellpython multiagent_workflow.py --devuiShow more lines
This launches a local DevUI instance with:

Workflow visualization
Step‑by‑step agent execution
OpenAI‑compatible /v1 API


🎯 Why This Pattern Matters

✅ Parallel execution reduces latency
✅ Specialized agents improve output quality
✅ Explicit orchestration improves transparency and auditability
✅ MCP enables reusable, protocol‑based integrations
✅ Works locally and scales toward enterprise‑grade deployments


🔮 Extensions & Ideas

Add more specialist agents (e.g. FDA filings, patents, internal knowledge)
Replace public MCP servers with private/internal ones
Add evaluation, traceability, or human‑in‑the‑loop approvals
Host the workflow behind an API or UI (Teams, web app, etc.)
