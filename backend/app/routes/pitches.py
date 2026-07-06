"""Pitch endpoints: filtered, paginated pitch retrieval."""

from flask import Blueprint, jsonify, request
from sqlalchemy import Float, cast, or_

from app.extensions import db
from app.models import Pitch
from app.routes import load_query_params, paginate
from app.schemas import PitchQuerySchema, PitchSchema

pitches_bp = Blueprint("pitches", __name__)

pitches_schema = PitchSchema(many=True)
pitch_query_schema = PitchQuerySchema()


@pitches_bp.route("/pitches", methods=["GET"])
def get_pitches():
    """List pitches with optional filters and pagination.

    Query params:
        pitcher      - player_id, pitches *thrown* by the player
        batter       - player_id, pitches *seen* by the player
        player_id    - pitches thrown OR seen by the player
        pitch_type   - e.g. FF, SL, CH
        team         - pitches from games involving the team (home or away)
        min_velocity / max_velocity - release speed bounds in mph
        start_date / end_date       - game date bounds (YYYY-MM-DD)
        page / per_page             - pagination (default 1 / 50, max 500)

    NOTE: release_speed is stored as TEXT in the SQLite DB (raw CSV ingest),
    so velocity filters CAST to REAL. Without the cast SQLite compares
    TEXT > INTEGER for *any* string value and the filter silently returns
    wrong rows.
    """
    params = load_query_params(pitch_query_schema, request.args)

    query = Pitch.query
    if "pitcher" in params:
        query = query.filter(Pitch.pitcher == params["pitcher"])
    if "batter" in params:
        query = query.filter(Pitch.batter == params["batter"])
    if "player_id" in params:
        query = query.filter(
            or_(Pitch.pitcher == params["player_id"], Pitch.batter == params["player_id"])
        )
    if "pitch_type" in params:
        query = query.filter(Pitch.pitch_type == params["pitch_type"].upper())
    if "team" in params:
        team = params["team"].upper()
        query = query.filter(or_(Pitch.home_team == team, Pitch.away_team == team))

    speed = cast(Pitch.release_speed, Float)
    if "min_velocity" in params or "max_velocity" in params:
        # Exclude rows with no recorded velocity from range filters.
        query = query.filter(Pitch.release_speed.isnot(None), Pitch.release_speed != "")
    if "min_velocity" in params:
        query = query.filter(speed >= params["min_velocity"])
    if "max_velocity" in params:
        query = query.filter(speed <= params["max_velocity"])

    if "start_date" in params:
        query = query.filter(Pitch.game_date >= params["start_date"].isoformat())
    if "end_date" in params:
        query = query.filter(Pitch.game_date <= params["end_date"].isoformat())

    query = query.order_by(Pitch.game_date.desc(), Pitch.rowid)

    pitches, pagination = paginate(query, params["page"], params["per_page"])
    return jsonify({"data": pitches_schema.dump(pitches), "pagination": pagination}), 200


@pitches_bp.route("/pitches/types", methods=["GET"])
def get_pitch_types():
    """Distinct pitch types with display names (drives the filter dropdown)."""
    rows = (
        db.session.query(Pitch.pitch_type, Pitch.pitch_name)
        .filter(Pitch.pitch_type.isnot(None), Pitch.pitch_type != "")
        .distinct()
        .order_by(Pitch.pitch_type)
        .all()
    )
    return jsonify([{"code": r.pitch_type, "name": r.pitch_name} for r in rows]), 200
