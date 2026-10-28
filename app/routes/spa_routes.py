"""Serves the built Vue front end (frontend/dist) under /app/."""
from pathlib import Path

from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("spa", __name__)

DEFAULT_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def _dist() -> Path:
    return Path(current_app.config.get("FRONTEND_DIST") or DEFAULT_DIST)


@bp.get("/app", defaults={"path": ""})
@bp.get("/app/", defaults={"path": ""})
@bp.get("/app/<path:path>")
def frontend(path):
    dist = _dist()
    if not (dist / "index.html").is_file():
        return ("The front end has not been built yet. Run: cd frontend && npm install && "
                "npm run build", 503)
    target = (dist / path).resolve()
    if path and target.is_file() and dist.resolve() in target.parents:
        response = send_from_directory(dist, path)
        if path.startswith("assets/"):          # file names contain a content hash
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
    return send_from_directory(dist, "index.html")
