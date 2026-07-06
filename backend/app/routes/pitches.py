"""Pitch endpoints."""

from flask import Blueprint, jsonify

from app.models import Pitch
from app.schemas import PitchSchema

pitches_bp = Blueprint("pitches", __name__)

pitches_schema = PitchSchema(many=True)


@pitches_bp.route("/pitches", methods=["GET"])
def get_pitches():
    """Get all pitches (filtering to follow)."""
    pitches = Pitch.query.limit(1000).all()
    return jsonify(pitches_schema.dump(pitches)), 200
