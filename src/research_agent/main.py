import typer
from typing import Optional
from research_agent.graph import create_research_graph
from research_agent.storage import RunStore

app = typer.Typer(help="AI Tech Topic Research Agent CLI")

@app.command()
def run(
    interests: str = typer.Option(
        ...,
        "--interests", "-i",
        help="Comma-separated user interest profile"
    ),
    topic_count: int = typer.Option(
        5,
        "--topic-count", "-c",
        help="Number of final topics to research and summarize"
    ),
    depth: str = typer.Option(
        "standard",
        "--depth", "-d",
        help="Research depth: standard or deep"
    ),
    manual_selection: bool = typer.Option(
        False,
        "--manual", "-m",
        help="Manually review and select topics after discovery"
    )
):
    """
    Run the research agent pipeline.
    """
    typer.echo("Starting pipeline run...")
    
    # 1. Initialize storage run folder
    store = RunStore()
    run_id = store.create_run()
    
    # 2. Build graph and run
    graph = create_research_graph()
    
    initial_state = {
        "user_interests": interests,
        "target_audience": "Mid-Senior Level",
        "raw_topics": [],
        "refined_topics": [],
        "selected_topics": [],
        "research_notes": {},
        "summaries": {},
        "errors": [],
        "run_id": run_id,
        "manual_selection": manual_selection
    }
    
    typer.echo(f"Run ID: {run_id}")
    typer.echo(f"Outputs will be saved to: {store.run_path}")
    typer.echo("-" * 50)
    
    try:
        graph.invoke(initial_state)
    except Exception as e:
        typer.echo(f"Pipeline execution failed: {e}")

@app.command()
def web(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the web server on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address")
):
    """
    Start the FastAPI web server.
    """
    import uvicorn
    typer.echo(f"Starting web server on http://{host}:{port}")
    # We will import and run the FastAPI app dynamically to avoid early import errors
    uvicorn.run("research_agent.web.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    app()
