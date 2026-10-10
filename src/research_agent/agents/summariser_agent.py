import os
import json
from pathlib import Path
from research_agent.models import ResearchNotes, TopicSummary
from research_agent.llm import LLMProvider

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class SummariserAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("summariser_agent.md")

    def summarize_research(self, notes: ResearchNotes) -> TopicSummary:
        """
        Translates raw research notes into a structured, highly-readable markdown interview summary guide.
        """
        topic_title = notes.topic

        # Format sources for the notes string
        sources_list = []
        for s in notes.sources:
            sources_list.append(f"- [{s.title}]({s.url}) (Publisher: {s.publisher or 'Unknown'})")
        sources_str = "\n".join(sources_list)

        # Build research notes dump for LLM prompt
        notes_str = (
            f"Topic: {notes.topic}\n"
            f"Definition: {notes.definition}\n"
            f"Why It Matters:\n" + "\n".join(f"- {x}" for x in notes.why_it_matters) + "\n"
            f"Technical Details:\n" + "\n".join(f"- {x}" for x in notes.technical_details) + "\n"
            f"Examples:\n" + "\n".join(f"- {x}" for x in notes.examples) + "\n"
            f"Use Cases:\n" + "\n".join(f"- {x}" for x in notes.use_cases) + "\n"
            f"Limitations:\n" + "\n".join(f"- {x}" for x in notes.limitations) + "\n"
            f"Related Topics:\n" + "\n".join(f"- {x}" for x in notes.related_topics) + "\n"
            f"Sources:\n{sources_str}"
        )

        prompt = self.prompt_template.format(
            topic=topic_title,
            research_notes=notes_str
        )

        system_instruction = "You are an expert technical educator and interview coach."

        try:
            summary = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=TopicSummary,
                system_instruction=system_instruction
            )
            return summary
        except Exception as e:
            print(f"Warning: SummariserAgent LLM call failed: {e}. Generating fallback summary markdown.")
            
            # Simple fallback markdown structure
            fallback_markdown = (
                f"# {topic_title}\n\n"
                f"## One-Line Explanation\n{notes.definition}\n\n"
                f"## Simple Explanation\nA technology trend related to {topic_title}.\n\n"
                f"## Why This Is Trending\n" + "\n".join(f"- {x}" for x in notes.why_it_matters) + "\n\n"
                f"## How It Works\n" + "\n".join(f"- {x}" for x in notes.technical_details) + "\n\n"
                f"## Pros\n" + "\n".join(f"- {x}" for x in notes.why_it_matters[:2]) + "\n\n"
                f"## Cons / Limitations\n" + "\n".join(f"- {x}" for x in notes.limitations[:2] if notes.limitations) + "\n\n"
                f"## Common Interview Questions\n1. What is {topic_title}?\n2. What are the key architectural tradeoffs of {topic_title}?\n\n"
                f"## Sources\n{sources_str}"
            )
            return TopicSummary(
                topic=topic_title,
                summary_markdown=fallback_markdown
            )
