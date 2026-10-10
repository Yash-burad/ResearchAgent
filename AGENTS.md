# Agent Guidelines & Context

Please refer to [`STEERING_DOCUMENT.md`](file:///Users/yashburad/Workspace/AntigravityProjects/ResearchAgent/STEERING_DOCUMENT.md) for the complete architecture, graph topology, agent roles, schemas, storage conventions, and developer guidelines.

## Quick Reference
- **Run Dev Server**: `uvicorn research_agent.web.app:app --host 127.0.0.1 --port 8000 --reload`
- **Run Tests**: `pytest`
- **Key Modules**:
  - `src/research_agent/graph.py` (LangGraph State Machine)
  - `src/research_agent/agents/` (TopicAgent, FineTunerAgent, ResearcherAgent, SummariserAgent, InterviewIntelAgent, GamificationAgent, MockInterviewerAgent)
  - `src/research_agent/llm/` (LLM Provider abstraction: Gemini, Ollama, OpenAI, Mock)
  - `src/research_agent/storage/` (RunStore & Markdown writers, anchored to project root)
  - `src/research_agent/web/` (FastAPI backend & Vanilla HTML/CSS/JS frontend)
