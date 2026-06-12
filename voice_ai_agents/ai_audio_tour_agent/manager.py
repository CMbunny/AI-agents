from __future__ import annotations

import asyncio
from rich.console import Console
from agents import Runner, gen_trace_id, trace

from agent import MOCK_MODE
from agent import History, historical_agent
from agent import Culinary, culinary_agent
from agent import Culture, culture_agent
from agent import Architecture, architecture_agent
from agent import Planner, planner_agent
from agent import FinalTour, orchestrator_agent
from agent import LocationSuggestions, location_suggestion_agent
from printer import Printer


MOCK_SUGGESTIONS = LocationSuggestions(
    stops=[
        {"name": "Hawa Mahal", "description": "The iconic Palace of Winds with 953 windows, built in 1799 for royal women to observe street life unseen."},
        {"name": "Amber Fort", "description": "A magnificent hilltop fortress blending Rajput and Mughal architecture with stunning mirror-work interiors."},
        {"name": "Jantar Mantar", "description": "A UNESCO World Heritage Site featuring 19 astronomical instruments including the world's largest stone sundial."},
        {"name": "City Palace", "description": "A sprawling royal complex at the heart of Jaipur still partially home to the royal family, with museums and courtyards."},
        {"name": "Nahargarh Fort", "description": "A hilltop fort offering panoramic views of Jaipur city, originally built as a retreat for Maharaja Sawai Jai Singh II."},
        {"name": "Johri Bazaar", "description": "Jaipur's most famous market street, lined with jewellers, gem cutters, and traditional Rajasthani textile shops."},
    ]
)

MOCK_STOP_CONTENT = {
    "Hawa Mahal": FinalTour(
        introduction="Welcome to Hawa Mahal, one of Jaipur's most recognizable landmarks.",
        architecture="As you stand before the Hawa Mahal, you're looking at one of the most unusual structures in all of India. The facade rises five stories but is only one room deep in most places — it's essentially an enormous ornamental screen. Those 953 small windows, called jharokhas, are arranged in a perfect honeycomb pattern, each one unique. The latticework was designed so that even a gentle breeze would cool the interior — that's how it earned the name Palace of Winds. Built in 1799 by Maharaja Sawai Pratap Singh, the architecture blends Rajput and Mughal styles in a way that was completely ahead of its time.",
        history="The Hawa Mahal was built with a very specific purpose — to allow the women of the royal household to observe street festivals and daily life without being seen themselves. This was a common practice in Rajput culture known as purdah. What's remarkable is that despite its grand appearance from the outside, most of the structure is just a series of corridors and small chambers. The building has survived over two centuries largely intact and remains one of the best preserved examples of late Rajput architecture in India.",
        culture="The Hawa Mahal sits right at the edge of the old city bazaar, which means standing here you're at the intersection of royal Jaipur and everyday Jaipur. The streets below have been bustling with traders, musicians, and craftsmen for over two hundred years. During festivals like Teej and Gangaur, this entire stretch fills with processions, music, and colour — much as it did when the royal women watched from these very windows.",
        culinary="Just steps from the Hawa Mahal you'll find some of Jaipur's best street food. The pyaaz kachori stalls along this stretch have been here for generations — flaky pastry stuffed with spiced onions, served hot with tamarind chutney. If you're here in the morning, look for the milk and mawa shops that open at sunrise and serve fresh rabri and lassi to the early market crowd.",
        conclusion="Hawa Mahal is the perfect starting point for any Jaipur tour — it sets the tone for everything that follows."
    ),
    "default": FinalTour(
        introduction="Welcome to this incredible stop on your Jaipur tour.",
        architecture="This location is a remarkable example of Rajasthani architecture, blending traditional craftsmanship with historical significance. The structures here reflect centuries of skilled artisanship passed down through generations of local builders.",
        history="This site has witnessed centuries of Jaipur's rich history, from the founding of the Pink City in 1727 to the present day. Each stone here carries stories of royalty, trade, and cultural exchange that shaped the city you see around you.",
        culture="The cultural significance of this place runs deep in Jaipur's identity. Local traditions, festivals, and artistic practices are all connected to sites like this one, which continue to play a role in the living culture of the city.",
        culinary="The area around this stop has its own food culture worth exploring. Look for local vendors selling traditional Rajasthani snacks and sweets that have been made the same way for generations.",
        conclusion="This stop is a wonderful example of what makes Jaipur such a unique and rewarding city to explore."
    )
}


class TourManager:
    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    async def get_suggestions(self, city: str, preference: str) -> LocationSuggestions:
        """Fetch stop suggestions for a city. Returns mock data if MOCK_MODE is on."""
        if MOCK_MODE:
            return MOCK_SUGGESTIONS

        self.printer.update_item("Suggestions", f"Finding {preference.lower()} spots in {city}...")
        result = await Runner.run(
            location_suggestion_agent,
            f"City: {city}\nPreference: {preference}\n\nFind 6 real visitable locations in this city matching the preference."
        )
        self.printer.update_item("Suggestions", "Found locations", is_done=True)
        self.printer.end()
        return result.final_output_as(LocationSuggestions)

     async def run(self, city: str, selected_stops: list, interests: list, duration: str, language: str = "English", persona: str = "Friendly Local") -> str:
        """Main tour generation flow."""
        if MOCK_MODE:
            return self._run_mock(selected_stops, interests)

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
            planner = await self._get_plan(city, interests, duration)

            # Step 2: Calculate word limits per stop
            
           
           # Persona emphasis mapping — emphasized interest gets 40% more words
            PERSONA_EMPHASIS = {
                    "Friendly Local": "culture",
                    "History Professor": "history",
                    "Food Critic": "culinary",
                    "Architecture Enthusiast": "architecture",
                    "Storyteller": "history"
            }

            words_per_minute = 150
            num_stops = len(selected_stops)
            base_limit = int((planner.architecture * words_per_minute) / num_stops)
            emphasis_key = PERSONA_EMPHASIS.get(persona, None)

            word_limits = {
                "architecture": int((planner.architecture * words_per_minute) / num_stops),
                "history": int((planner.history * words_per_minute) / num_stops),
                "culinary": int((planner.culinary * words_per_minute) / num_stops),
                "culture": int((planner.culture * words_per_minute) / num_stops),
            }

            # Give emphasized interest 40% more words
            if emphasis_key and emphasis_key in word_limits:
                word_limits[emphasis_key] = int(word_limits[emphasis_key] * 1.4)

            # Step 3: Generate content for all stops concurrently
            stop_tasks = []
            for stop in selected_stops:
                stop_tasks.append(
                    self._get_stop_content(stop, interests, word_limits,language,persona)
                )

            try:
                stop_results = await asyncio.gather(*stop_tasks)
            except Exception as e:
                self.printer.end()
                raise RuntimeError(f"One or more agents failed during research: {str(e)}")

            # Step 4: Assemble final tour
            final_tour = await self._get_final_tour(
                city,
                selected_stops,
                interests,
                duration,
                stop_results,
                language,
                persona
            )

            self.printer.update_item("final_report", "", is_done=True)
            self.printer.end()

        return self._assemble_output(city, selected_stops, stop_results, final_tour)

    def _run_mock(self, selected_stops: list, interests: list) -> str:
        """Returns mock tour content without any API calls."""
        stop_results = []
        for stop in selected_stops:
            content = MOCK_STOP_CONTENT.get(stop, MOCK_STOP_CONTENT["default"])
            stop_results.append((stop, content))

        sections = []

        # Overall intro
        sections.append(
            f"Welcome to your personalized tour! Today we'll be visiting {len(selected_stops)} "
            f"amazing {'stop' if len(selected_stops) == 1 else 'stops'}: "
            f"{', '.join(selected_stops)}. Let's get started!"
        )

        # Each stop
        for stop_name, content in stop_results:
            sections.append(f"--- {stop_name} ---")
            sections.append(content.introduction)
            if "Architecture" in interests:
                sections.append(content.architecture)
            if "History" in interests:
                sections.append(content.history)
            if "Culture" in interests:
                sections.append(content.culture)
            if "Culinary" in interests:
                sections.append(content.culinary)

        # Overall conclusion
        sections.append(
            f"And that wraps up our tour of {', '.join(selected_stops)}. "
            "Each of these places tells a different story, but together they paint a "
            "vivid picture of this incredible destination. Safe travels!"
        )

        return "\n\n".join(sections)

    def _assemble_output(self, city: str, selected_stops: list, stop_results: list, final_tour: FinalTour) -> str:
        """Assembles final tour text from real agent outputs."""
        sections = []
        sections.append(final_tour.introduction)

        for stop_name, content in zip(selected_stops, stop_results):
            sections.append(f"--- {stop_name} ---")
            sections.append(content.introduction)
            if content.architecture:
                sections.append(content.architecture)
            if content.history:
                sections.append(content.history)
            if content.culture:
                sections.append(content.culture)
            if content.culinary:
                sections.append(content.culinary)

        sections.append(final_tour.conclusion)
        return "\n\n".join(sections)

   async def _get_stop_content(self, stop: str, interests: list, word_limits: dict, language: str = "English", persona: str = "Friendly Local") -> FinalTour:
        """Runs all selected specialist agents for a single stop concurrently."""
        tasks = {}
        if "Architecture" in interests:
            tasks["architecture"] = self._get_architecture(stop, interests, word_limits["architecture"],language,persona)
        if "History" in interests:
            tasks["history"] = self._get_history(stop, interests, word_limits["history"],language,persona)
        if "Culinary" in interests:
            tasks["culinary"] = self._get_culinary(stop, interests, word_limits["culinary"],language,persona)
        if "Culture" in interests:
            tasks["culture"] = self._get_culture(stop, interests, word_limits["culture"],language,persona)

        results = await asyncio.gather(*tasks.values())
        research_results = dict(zip(tasks.keys(), results))

        return FinalTour(
            introduction=f"Next, we arrive at {stop}.",
            architecture=research_results.get("architecture", Architecture(output="")).output if "architecture" in research_results else "",
            history=research_results.get("history", History(output="")).output if "history" in research_results else "",
            culture=research_results.get("culture", Culture(output="")).output if "culture" in research_results else "",
            culinary=research_results.get("culinary", Culinary(output="")).output if "culinary" in research_results else "",
            conclusion=""
        )

    async def _get_plan(self, query: str, interests: list, duration: str,) -> Planner:
        self.printer.update_item("Planner", "Planning your personalized tour...")
        result = await Runner.run(
            planner_agent,
            "Query: {} Interests: {} Duration: {}".format(query, ', '.join(interests), duration)
        )
        self.printer.update_item("Planner", "Completed planning", is_done=True)
        return result.final_output_as(Planner)

    async def _get_history(self, query: str, interests: list, word_limit: int, language: str = "English", persona: str = "Friendly Local") -> History:
        self.printer.update_item(f"History-{query}", f"Researching history of {query}...")
        result = await Runner.run(
            historical_agent,
            "Query: {} Interests: {} Word Limit: {} - {} Output Language: {} Persona: {}\n\nInstructions: Create engaging historical content for an audio tour. Adopt the voice and tone of a {}. Focus on interesting stories and personal connections. Make it conversational and include specific details that would be interesting to hear while walking. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, language, persona, persona, word_limit)
        )
        self.printer.update_item(f"History-{query}", f"Completed history for {query}", is_done=True)
        return result.final_output_as(History)

    async def _get_architecture(self, query: str, interests: list, word_limit: int, language: str = "English", persona: str = "Friendly Local") -> Architecture:
        self.printer.update_item(f"Architecture-{query}", f"Exploring architecture of {query}...")
        result = await Runner.run(
            architecture_agent,
            "Query: {} Interests: {} Word Limit: {} - {} Output Language: {} Persona: {}\n\nInstructions: Create engaging architectural content for an audio tour. Adopt the voice and tone of a {}. Focus on visual descriptions and interesting design details. Make it conversational and include specific buildings and their unique features. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, language, persona, persona, word_limit)
        )
        self.printer.update_item(f"Architecture-{query}", f"Completed architecture for {query}", is_done=True)
        return result.final_output_as(Architecture)

    async def _get_culinary(self, query: str, interests: list, word_limit: int, language: str = "English", persona: str = "Friendly Local") -> Culinary:
        self.printer.update_item(f"Culinary-{query}", f"Discovering flavors near {query}...")
        result = await Runner.run(
            culinary_agent,
            "Query: {} Interests: {} Word Limit: {} - {} Output Language: {} Persona: {}\n\nInstructions: Create engaging culinary content for an audio tour. Adopt the voice and tone of a {}. Focus on local specialties, food history, and interesting stories about restaurants and dishes. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, language, persona, persona, word_limit)
        )
        self.printer.update_item(f"Culinary-{query}", f"Completed culinary for {query}", is_done=True)
        return result.final_output_as(Culinary)

    async def _get_culture(self, query: str, interests: list, word_limit: int, language: str = "English", persona: str = "Friendly Local") -> Culture:
        self.printer.update_item(f"Culture-{query}", f"Exploring culture of {query}...")
        result = await Runner.run(
            culture_agent,
            "Query: {} Interests: {} Word Limit: {} - {} Output Language: {} Persona: {}\n\nInstructions: Create engaging cultural content for an audio tour. Adopt the voice and tone of a {}. Focus on local traditions, arts, and community life. The content should be approximately {} words when spoken at a natural pace.".format(
                query, ', '.join(interests), word_limit, word_limit + 20, language, persona, persona, word_limit)
        )
        self.printer.update_item(f"Culture-{query}", f"Completed culture for {query}", is_done=True)
        return result.final_output_as(Culture)

    async def _get_final_tour(self, city: str, selected_stops: list, interests: list, duration: float, stop_results: list,language: str = "English",persona: str = "Friendly Local") -> FinalTour:
        self.printer.update_item("Final Tour", "Assembling your complete tour...")

        stop_summaries = []
        for stop_name, content in zip(selected_stops, stop_results):
            parts = [f"Stop: {stop_name}"]
            if content.architecture:
                parts.append(content.architecture)
            if content.history:
                parts.append(content.history)
            if content.culture:
                parts.append(content.culture)
            if content.culinary:
                parts.append(content.culinary)
            stop_summaries.append("\n".join(parts))

        prompt = (
            "City: {}\n"
            "Selected Stops: {}\n"
            "Selected Interests: {}\n"
            "Total Tour Duration (in minutes): {}\n\n"
            "Output Language: {}\n\n"
            "Tour Persona: {}\n\n"
            "Stop Content:\n{}\n\n"
            "Instructions: Write a warm introduction welcoming the user to the city and outlining the stops. "
            "Adopt the voice and tone of a {}."
            "Then write a short conclusion summarizing the tour. "
            "Keep both conversational, natural, and suitable for audio. No formatting or headers."
            
        ).format(
            city,
            ', '.join(selected_stops),
            ', '.join(interests),
            duration,
            language,
            '\n\n---\n\n'.join(stop_summaries),
            persona
        )

        result = await Runner.run(orchestrator_agent, prompt)
        self.printer.update_item("Final Tour", "Tour assembly complete", is_done=True)
        return result.final_output_as(FinalTour)