import json
from pathlib import Path

from mcp.server import MCPServer

SESSIONS = json.loads((Path(__file__).parent / "sessions.json").read_text())

server = MCPServer("sessions")


@server.tool()
def list_sessions(day: str | None = None, track: str | None = None) -> list[dict]:
    """List conference sessions, optionally filtered by day or track.

    Args:
        day: Day name, for example "Friday".
        track: Track name, for example "Data & AI".
    """
    results = SESSIONS
    if day:
        results = [s for s in results if s["day"].lower() == day.lower()]
    if track:
        results = [s for s in results if s["track"].lower() == track.lower()]
    return results


@server.tool()
def get_session(session_id: str) -> dict | None:
    """Get one session by its id.

    Args:
        session_id: The session id, for example "s-04".
    """
    return next((s for s in SESSIONS if s["id"] == session_id), None)


@server.tool()
def search_speakers(query: str) -> list[dict]:
    """Find sessions whose speaker name matches a query.

    Args:
        query: Part of a speaker's name.
    """
    q = query.lower()
    return [s for s in SESSIONS if q in s["speaker"].lower()]


if __name__ == "__main__":
    server.run(transport="stdio")
