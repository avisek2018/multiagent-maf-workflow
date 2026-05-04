# Multi‑Agent Orchestration with Microsoft Agent Framework

This repository demonstrates a **fan‑out / fan‑in multi‑agent orchestration pattern** built using the **Microsoft Agent Framework (MAF)**.  
It showcases how multiple specialized AI agents can run **in parallel**, retrieve grounded data via **public MCP (Model Context Protocol) servers**, and then **converge into a single synthesized response**.

---

## 🧠 What This Project Does

Given a medical or life‑sciences research topic (for example, *“cancer immunotherapy”*), the system:

1. Fans the topic out to **two specialized agents running in parallel**
2. Grounds each agent using **publicly hosted MCP servers**
3. Merges the outputs into a **single, structured summary**

This pattern is well‑suited for **research, analysis, and decision‑support scenarios** where insights must be drawn from multiple authoritative sources.

---

## 🏗 Architecture Overview

**Workflow topology (fan‑out / fan‑in):**

```
User Input
   │
Dispatcher (start node)
   │
   ├── PubMed Research Agent ──┐
   │                           ├── Summarizer Agent → Final Output
   └── Clinical Trials Agent ──┘
```

### Key Components

- **Dispatcher (Executor)**
  - Entry point of the workflow
  - Broadcasts the input topic to downstream agents

- **PubMed Research Agent**
  - Connects to a **public PubMed MCP server**
  - Retrieves scientific literature, papers, and metadata

- **Clinical Trials Agent**
  - Connects to a **public ClinicalTrials.gov MCP server**
  - Retrieves active and historical clinical trial data

- **Summarizer Agent**
  - Performs fan‑in
  - Synthesizes outputs from both agents into a single report

---

## 🔌 Model Context Protocol (MCP)

This project uses `MCPStreamableHTTPTool` to connect agents to **external MCP servers** over streamable HTTP.

Public MCP endpoints used:
- **PubMed MCP** – Biomedical literature and metadata
- **ClinicalTrials.gov MCP** – Structured clinical trial information

### Why MCP?
- Tool‑grounded responses (reduced hallucination)
- Clean separation between orchestration logic and data providers
- Easy replacement with private or internal MCP servers later

---

## 🔁 Orchestration Pattern

### Fan‑Out
- A single input message is sent to multiple agents simultaneously
- Agents run **concurrently**, each using different tools and data sources

### Fan‑In
- The workflow waits for **all parallel agents** to complete
- Results are routed into a single summarization agent

This pattern is implemented directly using `WorkflowBuilder.add_edge(...)`, without custom threading or async coordination logic.

---

## 🧪 Running the Project

### Prerequisites
- Python 3.10+
- Microsoft Agent Framework
- Azure OpenAI or OpenAI‑compatible endpoint
- (Optional) Agent Framework DevUI

### Install Dependencies
```bash
pip install agent-framework agent-framework-devui python-dotenv
```

### Run in CLI Mode
```bash
python multiagent_workflow_devui.py
```

### Run with DevUI (Browser‑based Debugging)
```bash
python multiagent_workflow_devui.py --devui
```

DevUI provides:
- Workflow visualization
- Step‑by‑step agent execution
- OpenAI‑compatible `/v1` API for testing

---

## 🎯 Why This Pattern Matters

- ✅ Parallel execution reduces latency
- ✅ Specialized agents improve output quality
- ✅ Explicit orchestration improves transparency and auditability
- ✅ MCP enables reusable, protocol‑based integrations
- ✅ Works locally and scales toward enterprise‑grade deployments

---

## 🔮 Extensions & Ideas

- Add additional specialist agents (e.g., FDA filings, patents, internal knowledge)
- Replace public MCP servers with private or internal ones
- Add evaluation, traceability, or human‑in‑the‑loop approvals
- Expose the workflow via an API or UI (Teams, web app, etc.)

---

## 📜 Disclaimer

This project is for **educational and experimental purposes**.  
Public MCP servers used here are maintained by third parties—review and govern external data usage appropriately before production use.
