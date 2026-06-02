from __future__ import annotations

import asyncio
from rich.console import Console
from agents import Runner, gen_trace_id, trace

from agent import History, historical_agent
from agent import Culinary, culinary_agent
from agent import Culture, culture_agent
from agent import Architecture, architecture_agent
from agent import Planner, planner_agent
from agent import FinalTour, orchestrator_agent
from printer import Printer


class TourManager:
    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, query: str, interests: list, duration: str) -> None:
        trace_id = gen_trace_id()
        with trace("Tour Research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                "View trace: https://platform.openai.com/traces/{}".format(trace_id),
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item("start", "Starting tour research...", is_done=True)

            # Step 1: Get time allocation plan
            planner = await self._get_plan(query, interests, duration)

            # Step 2: Calculate word limits from planner output
            words_per_minute = 150
            word_limits = {
                "architecture": int(planner.architecture * words_per_minute),
                "history": int(planner.history * words_per_minute),
                "culinary": int(planner.culinary * words_per_minute),
                "culture": int(planner.culture * words_per_minute),
            }

            # Step 3: Build tasks dict for only selected interests
            tasks = {}
            if "Architecture" in interests:
                tasks["architecture"] = self._get_architecture(query, interests, word_limits["architecture"])
            if "History" in interests:
                tasks["history"] = self._get_history(query, interests, word_limits["history"])
            if "Culinary" in interests:
                tasks["culinary"] = self._get_culinary(query, interests, word_limits["culinary"])
            if "Culture" in interests:
                tasks["culture"] = self._get_culture(query, interests, word_limits["culture"])

            # Step 4: Run all selected agents concurrently
            try:
                results = await asyncio.gather(*tasks.values())
                research_results = dict(zip(tasks.keys(), results))
            except Exception as e:
                self.printer.end()
                raise RuntimeError(f"One or more agents failed during research: {str(e)}")

            # Step 5: Assemble final tour
            final_tour = await self._get_final_tour(
                query,
                interests,
                duration,
                research_results
            )

            self.printer.update_item("final_report", "", is_done=True)
            self.printer.end()

        # Build output text from selected sections only
        sections = []

        # Always include intro
        sections.append(final_tour.introduction)

        if "Architecture" in interests:
            sections.append(final_tour.architecture)
        if "History" in interests:
            sections.append(final_tour.history)
        if "Culture" in interests:
            sections.append(final_tour.culture)
        if "Culinary" in interests:
            sections.append(final_tour.culinary)

        # Always include conclusion
        sections.append(final_tour.conclusion)

        final = ""
        for i, content in enumerate(sections):
            if i > 0:
                final += "\n\n"
            final += content

        return final

    async def _get_plan(self, query: str, interests: list, duration: str) -> Planner:
        self.printer.update_item("Planner", "Planning your personalized tour...")
        result = await Runner.run(
            planner_agent,
            "Query: {} Interests: {} Duration: {}".format(query, ', '.join(interests), duration)
        )
        self.printer.update_item("Planner", "Completed planning", is_done=True)
        return result.final_output_as(Planner)

    async def _get_history(self, query: str, interests: list, word_limit: int) -> History:
        self.printer.update_item("History", "Researching historical highlights...")
        result = await Runner.run(
            historical_agent,
            "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging historical content for an audio tour. Focus on interesting stories and personal connections. Make it conversational and include specific details that would be interesting to hear while walking. Include specific locations and landmarks where possible. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
        )
        self.printer.update_item("History", "Completed history research", is_done=True)
        return result.final_output_as(History)

    async def _get_architecture(self, query: str, interests: list, word_limit: int) -> Architecture:
        self.printer.update_item("Architecture", "Exploring architectural wonders...")
        result = await Runner.run(
            architecture_agent,
            "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging architectural content for an audio tour. Focus on visual descriptions and interesting design details. Make it conversational and include specific buildings and their unique features. Describe what visitors should look for and why it matters. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
        )
        self.printer.update_item("Architecture", "Completed architecture research", is_done=True)
        return result.final_output_as(Architecture)

    async def _get_culinary(self, query: str, interests: list, word_limit: int) -> Culinary:
        self.printer.update_item("Culinary", "Discovering local flavors...")
        result = await Runner.run(
            culinary_agent,
            "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging culinary content for an audio tour. Focus on local specialties, food history, and interesting stories about restaurants and dishes. Make it conversational and include specific recommendations. Describe the flavors and cultural significance of the food. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
        )
        self.printer.update_item("Culinary", "Completed culinary research", is_done=True)
        return result.final_output_as(Culinary)

    async def _get_culture(self, query: str, interests: list, word_limit: int) -> Culture:
        self.printer.update_item("Culture", "Exploring cultural highlights...")
        result = await Runner.run(
            culture_agent,
            "Query: {} Interests: {} Word Limit: {} - {}\n\nInstructions: Create engaging cultural content for an audio tour. Focus on local traditions, arts, and community life. Make it conversational and include specific cultural venues and events. Describe the atmosphere and significance of cultural landmarks. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, word_limit)
        )
        self.printer.update_item("Culture", "Completed culture research", is_done=True)
        return result.final_output_as(Culture)

    async def _get_final_tour(self, query: str, interests: list, duration: float, research_results: dict) -> FinalTour:
        self.printer.update_item("Final Tour", "Creating your personalized tour...")

        content_sections = []
        for interest in interests:
            if interest.lower() in research_results:
                content_sections.append(research_results[interest.lower()].output)

        words_per_minute = 150
        total_words = int(duration) * words_per_minute

        prompt = (
            "Query: {}\n"
            "Selected Interests: {}\n"
            "Total Tour Duration (in minutes): {}\n"
            "Target Word Count: {}\n\n"
            "Content Sections:\n{}\n\n"
            "Instructions: Create a natural, conversational audio tour that focuses only on the selected interests. "
            "Make it feel like a friendly guide walking alongside the visitor, sharing interesting stories and insights. "
            "Use natural transitions between topics and maintain an engaging but relaxed pace. "
            "Include specific locations and landmarks where possible. "
            "Add natural pauses and transitions as if walking between locations. "
            "Use phrases like 'as we walk', 'look to your left', 'notice how', etc. "
            "Make it interactive and engaging, as if the guide is actually there with the visitor. "
            "Start with a warm welcome and end with a natural closing thought. "
            "The total content should be approximately {} words when spoken at a natural pace of 150 words per minute. "
            "This will ensure the tour lasts approximately {} minutes."
        ).format(
            query,
            ', '.join(interests),
            duration,
            total_words,
            '\n\n'.join(content_sections),
            total_words,
            duration
        )

        result = await Runner.run(orchestrator_agent, prompt)
        self.printer.update_item("Final Tour", "Completed Final Tour Guide Creation", is_done=True)
        return result.final_output_as(FinalTour)