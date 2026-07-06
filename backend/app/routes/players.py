"""Player endpoints: listing/filtering, detail, and reference data."""

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Player
from app.routes import load_query_params, paginate
from app.schemas import PlayerQuerySchema, PlayerSchema

players_bp = Blueprint("players", __name__)

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
player_query_schema = PlayerQuerySchema()


@players_bp.route("/players", methods=["GET"])
def get_players():
    """List players with optional team/position/name-search filters.

    Query params: team, position, search, page, per_page
    """
    params = load_query_params(player_query_schema, request.args)

    query = Player.query
    if "team" in params:
        query = query.filter(Player.team == params["team"].upper())
    if "position" in params:
        query = query.filter(Player.primary_position == params["position"].upper())
    if "search" in params:
        pattern = f"%{params['search']}%"
        query = query.filter(
            or_(Player.first_name.ilike(pattern), Player.last_name.ilike(pattern))
        )
    query = query.order_by(Player.last_name, Player.first_name)

    players, pagination = paginate(query, params["page"], params["per_page"])
    return (
        jsonify({"data": players_schema.dump(players), "pagination": pagination}),
        200,
    )


@players_bp.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id: int):
    """Fetch a single player by id; 404 if not found."""
    player = db.session.get(Player, player_id)
    if player is None:
        return jsonify({"error": f"Player {player_id} not found"}), 404
    return jsonify(player_schema.dump(player)), 200


@players_bp.route("/players/teams", methods=["GET"])
def get_teams():
    """Distinct team codes (drives the frontend filter dropdown)."""
    teams = [
        t for (t,) in db.session.query(Player.team).distinct().order_by(Player.team)
    ]
    return jsonify(teams), 200


@players_bp.route("/players/positions", methods=["GET"])
def get_positions():
    """Distinct position codes (drives the frontend filter dropdown)."""
    positions = [
        p
        for (p,) in db.session.query(Player.primary_position)
        .distinct()
        .order_by(Player.primary_position)
    ]
    return jsonify(positions), 200
