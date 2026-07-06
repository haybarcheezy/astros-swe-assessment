"""Player endpoints."""

from flask import Blueprint, jsonify

from app.models import Player
from app.schemas import PlayerSchema

players_bp = Blueprint("players", __name__)

players_schema = PlayerSchema(many=True)


@players_bp.route("/players", methods=["GET"])
def get_players():
    """Get all players (filtering to follow)."""
    players = Player.query.limit(1000).all()
    return jsonify(players_schema.dump(players)), 200
