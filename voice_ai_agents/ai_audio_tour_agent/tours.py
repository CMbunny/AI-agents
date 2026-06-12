import json
import uuid
from pathlib import Path
from datetime import datetime

TOURS_FILE = Path(__file__).parent / "tours.json"


def _load_all() -> list:
    """Load all tours from disk. Returns empty list if file doesn't exist."""
    try:
        if TOURS_FILE.exists():
            with open(TOURS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save_all(tours: list) -> None:
    """Write full tours list to disk."""
    with open(TOURS_FILE, "w", encoding="utf-8") as f:
        json.dump(tours, f, ensure_ascii=False, indent=2)


def save_tour(city: str, stops: list, interests: list, language: str, persona: str, duration: int, content: str) -> str:
    """Save a new tour and return its ID."""
    tours = _load_all()
    tour_id = str(uuid.uuid4())[:8]
    tours.append({
        "id": tour_id,
        "city": city,
        "stops": stops,
        "interests": interests,
        "language": language,
        "persona": persona,
        "duration": duration,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    _save_all(tours)
    return tour_id


def get_all_tours() -> list:
    """Return all saved tours, newest first."""
    tours = _load_all()
    return list(reversed(tours))


def delete_tour(tour_id: str) -> None:
    """Delete a tour by ID."""
    tours = _load_all()
    tours = [t for t in tours if t["id"] != tour_id]
    _save_all(tours)


def get_tour_by_id(tour_id: str) -> dict | None:
    """Fetch a single tour by ID."""
    for tour in _load_all():
        if tour["id"] == tour_id:
            return tour
    return None