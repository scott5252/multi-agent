from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def fixture_for_tool(
    tool_name: str, request_input: Mapping[str, Any]
) -> dict[str, Any]:
    if tool_name == "google_calendar.events.read":
        return {
            "events": [
                {
                    "title": "Product Review",
                    "starts_at": "2026-05-04T11:00:00-04:00",
                    "ends_at": "2026-05-04T12:00:00-04:00",
                    "location": "Zoom",
                    "priority": "high",
                    "conflict": False,
                },
                {
                    "title": "Investor Call",
                    "starts_at": "2026-05-04T14:00:00-04:00",
                    "ends_at": "2026-05-04T15:00:00-04:00",
                    "location": "Remote",
                    "priority": "high",
                    "conflict": False,
                },
            ],
            "date": str(request_input.get("date") or "2026-05-04"),
        }
    if tool_name == "gmail.messages.read":
        return {
            "messages": [
                {
                    "sender": "Sarah K. <sarah@example.com>",
                    "subject": "Launch date moved up",
                    "received_at": "2026-05-04T07:30:00-04:00",
                    "action_required": True,
                    "urgency": "high",
                    "summary": "Decision needed on launch sequencing.",
                    "body": "Raw email body stays provider-side.",
                },
                {
                    "sender": "Legal <legal@example.com>",
                    "subject": "Contract redline ready",
                    "received_at": "2026-05-04T08:05:00-04:00",
                    "action_required": True,
                    "urgency": "medium",
                    "summary": "Review and signature requested.",
                    "body": "Raw legal email body stays provider-side.",
                },
            ],
            "unread_only": bool(request_input.get("unread_only", True)),
        }
    if tool_name == "news.search":
        return {
            "items": [
                {
                    "headline": "AI infrastructure investment accelerates",
                    "source": "Example Business News",
                    "url": "https://news.example/articles/ai-infrastructure?utm_source=fixture",
                    "published_at": "2026-05-04T06:45:00-04:00",
                    "relevance": 0.92,
                    "summary": "Market coverage relevant to configured interests.",
                }
            ],
            "query": str(request_input.get("query") or "AI infrastructure"),
        }
    if tool_name == "weather.forecast.read":
        return {
            "forecast": {
                "location": str(request_input.get("location") or "Providence"),
                "forecast_date": str(request_input.get("date") or "2026-05-04"),
                "condition": "Partly cloudy with light rain by afternoon",
                "high_f": 61,
                "low_f": 49,
                "precipitation_chance": 0.42,
            }
        }
    if tool_name == "commute.lookup":
        return {
            "commute": {
                "origin_label": str(request_input.get("origin_label") or "Home"),
                "destination_label": str(
                    request_input.get("destination_label") or "Downtown office"
                ),
                "mode": str(request_input.get("mode") or "driving"),
                "estimated_minutes": 28,
                "status": "normal",
            }
        }
    raise KeyError(f"unknown fixture tool: {tool_name}")
