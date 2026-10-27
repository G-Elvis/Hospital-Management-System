from datetime import date, time

from flask import current_app


def svc(name: str):
    """Fetch a service that create_app() registered (the composition root)."""
    return current_app.extensions[name]


def parse_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def parse_time(value):
    try:
        return time.fromisoformat(value) if value else None
    except ValueError:
        return None
