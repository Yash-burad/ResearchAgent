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
        try:
            self.targeted_drill_prompt_template = load_game_prompt("targeted_drill.md")
        except Exception:
            self.targeted_drill_prompt_template = self.flashcards_prompt_template

    def generate_targeted_drill(
        self,
        stumble_items: list
    ) -> FlashcardsGame:
        """
        Generates a targeted retention drill deck derived from candidate's logged stumbles.
        """
        if not stumble_items:
            stumble_items = [{
                "title": "Core Distributed Systems & Algorithms",
                "category": "Core CS",
                "what_tripped_me": "Revisiting foundational concurrency and algorithmic patterns."
            }]

        profile_lines = []
        for i, item in enumerate(stumble_items, 1):
            title = item.get("title", f"Concept {i}")
            cat = item.get("category", "DSA")
            comp = f" (Company: {item.get('company')})" if item.get("company") else ""
            tripped = item.get("what_tripped_me", "Stumbled during technical evaluation.")
            profile_lines.append(f"{i}. [{cat}] {title}{comp}\n   What tripped candidate: {tripped}")

        stumble_profile = "\n\n".join(profile_lines)
        prompt = self.targeted_drill_prompt_template.format(stumble_profile=stumble_profile)
        system_instruction = (
            "You are a Staff/Principal interview coach deconstructing the candidate's exact interview stumbles. "
            "Generate rigorous flashcards that resolve their confusion and build deep intuition."
        )

        try:
            game = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=FlashcardsGame,
                system_instruction=system_instruction
            )
            game.topic = "Adaptive Retention Drill"
            game.total_cards = len(game.cards)
            return game
        except Exception as e:
            print(f"Warning: generate_targeted_drill structured LLM call failed: {e}. Generating fallback drill.")
            return self._generate_fallback_targeted_drill(stumble_items)

    def _generate_fallback_targeted_drill(self, stumble_items: list) -> FlashcardsGame:
        cards = []
        for i, item in enumerate(stumble_items[:5], 1):
            title = item.get("title", "Algorithmic Invariant")
            cat = item.get("category", "DSA")
            tripped = item.get("what_tripped_me", "Missed edge case.")
            cards.append(FlashcardItem(
                id=f"drill_{i}",
                category=cat,
                difficulty="Hard" if i % 2 == 0 else "Medium",
                front_prompt=f"When solving {title}, what is the critical edge case or trap that candidates frequently miss?",
                back_explanation=f"Trap analysis: {tripped}\n\nTo prevent this, define the state invariant upfront and test with extreme inputs.",
                hint="Recall where the algorithm can enter an infinite cycle or off-by-one condition.",
                key_takeaway=f"For {title}, systematically check empty states, single-element collections, and cycles."
            ))
        while len(cards) < 3:
            idx = len(cards) + 1
            cards.append(FlashcardItem(
                id=f"drill_{idx}",
                category="System Design",
                difficulty="Medium",
                front_prompt="How do you handle split-brain in leader election protocols?",
                back_explanation="Quorum consensus requires majority agreement ((N/2) + 1). Nodes reject stale terms.",
                hint="Think about odd vs even node cluster counts.",
                key_takeaway="A partition cannot elect a leader without a strict majority."
            ))
        return FlashcardsGame(
            topic="Adaptive Retention Drill",
            game_type="flashcards",
            total_cards=len(cards),
            cards=cards
        )

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
