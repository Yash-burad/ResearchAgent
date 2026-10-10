# AI Tech Topic Research Agent

A multi-agent AI system that discovers hot technology topics from the internet, filters and refines them according to your interests, researches selected topics in depth, and generates interview-optimized summaries.

## Features

- **Topic Discovery**: Crawls tech news and trends via DuckDuckGo search.
- **Mid-Senior Interest Tuning**: Refines and ranks discovered topics using local LLMs.
- **Deep Research**: Searches standard documentation, engineering blogs, and resources for tech topics.
- **Interview Summaries**: Generates high-quality markdown summaries optimized for mid-senior SDE interviews.
- **Web UI**: Review discovered topics, toggle manual override, and read summaries in a clean dashboard.

## Setup & Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd /Users/yashburad/Workspace/AntigravityProjects/ResearchAgent
   ```

2. **Environment Configuration**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Configure your preferred `LLM_PROVIDER` in `.env`:
   - `ollama` *(Default free & local)*: Run `ollama run qwen2.5:7b` (or `llama3.1:8b`)
   - `gemini`: Provide `GEMINI_API_KEY`
   - `openai`: Provide `OPENAI_API_KEY`
   - `mock`: Instant offline dry-runs without any external LLM dependencies

3. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

---

## Usage

### 1. CLI Pipeline (`Phase 1`)
Run the research agent pipeline directly from the command line:

```bash
# Automated run with default auto-selection
python3 -m research_agent.main run --interests "AI agents, distributed systems, cloud infra" --topic-count 3

# Run with manual topic selection prompt
python3 -m research_agent.main run --interests "databases, rust, wasm" --manual

# Fast offline dry-run test
LLM_PROVIDER=mock python3 -m research_agent.main run --interests "developer tools"
```

Outputs are automatically generated under `outputs/run_<timestamp>/`:
- `trending_topics.md` & `trending_topics.json`
- `refined_topics.md` & `refined_topics.json`
- `research/<topic_slug>.md` & `.json`
- `summaries/<topic_slug>.md` & `.json`
- `final_interview_pack.md`

### 2. Web UI Dashboard (`Phase 2`)
Launch the interactive FastAPI web dashboard:

```bash
python3 -m research_agent.main web --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to:
- Enter your interest profile and launch research runs.
- Monitor real-time agent execution status and live terminal logs.
- Interactively select and filter topic cards before deep research.
- Read and export the generated interview packs with syntax highlighting.

---

## Running Tests

Run the full pytest suite (covering agents, storage, LangGraph orchestration, and FastAPI REST endpoints):
```bash
pytest
```
