import os
from pathlib import Path
from typing import Dict, Any, Optional
from research_agent.models import ResearchNotes, TopicSummary, FlashcardsGame, FlashcardItem
from research_agent.llm import LLMProvider

def load_game_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts" / "games"
    file_path = prompts_dir / filename
    if not file_path.exists():
        # Fallback to general prompts directory if not in games/
        file_path = Path(__file__).parent.parent / "prompts" / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class GamificationAgent:
    """
    Extensible agent responsible for generating gamified learning modules (Flashcards, Quizzes, etc.)
    derived from researched tech topics.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.flashcards_prompt_template = load_game_prompt("flashcards.md")

    def generate_game(
        self,
        topic: str,
        research_notes: Optional[ResearchNotes] = None,
        summary: Optional[TopicSummary] = None,
        game_type: str = "flashcards"
    ) -> Any:
        """
        Main dispatcher to generate a requested game type for a topic.
        """
        if game_type == "flashcards":
            return self.generate_flashcards(topic, research_notes, summary)
        else:
            raise ValueError(f"Unsupported game type: '{game_type}'. Currently supported: ['flashcards']")

    def generate_flashcards(
        self,
        topic: str,
        research_notes: Optional[ResearchNotes] = None,
        summary: Optional[TopicSummary] = None
    ) -> FlashcardsGame:
        """
        Generates a deck of interview flashcards for a specific topic.
        """
        context_parts = []
        if research_notes:
            context_parts.append(f"Definition: {research_notes.definition}")
            context_parts.append("Technical Details:\n" + "\n".join(f"- {x}" for x in research_notes.technical_details))
            context_parts.append("Trade-offs / Limitations:\n" + "\n".join(f"- {x}" for x in research_notes.limitations))
            context_parts.append("Use Cases:\n" + "\n".join(f"- {x}" for x in research_notes.use_cases))
        if summary:
            context_parts.append(f"Summary Document:\n{summary.summary_markdown}")

        context_str = "\n\n".join(context_parts) if context_parts else f"Topic technical overview for {topic}."

        prompt = self.flashcards_prompt_template.format(
            topic=topic,
            context=context_str
        )

        system_instruction = (
            "You are a technical interview coach crafting interactive flashcards for senior engineering interviews. "
            "Focus on deep architectural mechanics, failure modes, and trade-offs."
        )

        try:
            game = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=FlashcardsGame,
                system_instruction=system_instruction
            )
            game.topic = topic
            game.total_cards = len(game.cards)
            return game
        except Exception as e:
            print(f"Warning: GamificationAgent structured call failed for topic '{topic}': {e}. Generating fallback flashcards.")
            return self._generate_fallback_flashcards(topic, research_notes, summary)

    def _generate_fallback_flashcards(
        self,
        topic: str,
        research_notes: Optional[ResearchNotes],
        summary: Optional[TopicSummary]
    ) -> FlashcardsGame:
        cards = [
            FlashcardItem(
                id="card_1",
                category="Core Architecture",
                difficulty="Medium",
                front_prompt=f"What core architectural problem does {topic} solve, and how does it work?",
                back_explanation=(
                    research_notes.definition if research_notes and research_notes.definition 
                    else f"{topic} standardizes and optimizes distributed engineering workflows and system integration."
                ),
                hint="Think about the primary motivation and architectural components.",
                key_takeaway=f"{topic} addresses core distributed system scalability and abstraction boundaries."
            ),
            FlashcardItem(
                id="card_2",
                category="Trade-offs & Scalability",
                difficulty="Hard",
                front_prompt=f"What are the major engineering trade-offs and limitations to consider when adopting {topic}?",
                back_explanation=(
                    "; ".join(research_notes.limitations[:2]) if research_notes and research_notes.limitations 
                    else f"Adoption overhead, potential latency trade-offs, and operational complexity."
                ),
                hint="Consider latency, consistency, and maintenance overhead.",
                key_takeaway="Every architectural pattern trades implementation complexity for scalability and isolation."
            ),
            FlashcardItem(
                id="card_3",
                category="System Design",
                difficulty="Medium",
                front_prompt=f"In what production scenario is {topic} best suited vs traditional alternatives?",
                back_explanation=(
                    "; ".join(research_notes.use_cases[:2]) if research_notes and research_notes.use_cases
                    else f"High-scale distributed applications requiring resilient decoupling and modern tool integration."
                ),
                hint="Focus on scaling bottlenecks and operational requirements.",
                key_takeaway="Select patterns based on workload characteristics and integration surface area."
            )
        ]
        return FlashcardsGame(
            topic=topic,
            game_type="flashcards",
            total_cards=len(cards),
            cards=cards
        )
