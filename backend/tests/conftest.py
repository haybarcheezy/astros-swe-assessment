"""Shared test fixtures.

Tests run against a seeded in-memory SQLite database rather than the real
baseball.db so they are fast, deterministic, and independent of the shipped
data.
"""

import pytest

from app import create_app
from app.extensions import db
from app.models import Pitch, Player

PLAYERS = [
    dict(
        player_id=1,
        first_name="Jose",
        last_name="Altuve",
        birthdate="1990-05-06",
        birth_country="Venezuela",
        birth_state=None,
        height_feet=5,
        height_inches=6,
        weight=166,
        team="HOU",
        primary_position="2B",
        throws="R",
        bats="R",
    ),
    dict(
        player_id=2,
        first_name="Framber",
        last_name="Valdez",
        birthdate="1993-11-19",
        birth_country="Dominican Republic",
        birth_state=None,
        height_feet=5,
        height_inches=11,
        weight=239,
        team="HOU",
        primary_position="LHS",
        throws="L",
        bats="L",
    ),
    dict(
        player_id=3,
        first_name="Shohei",
        last_name="Ohtani",
        birthdate="1994-07-05",
        birth_country="Japan",
        birth_state=None,
        height_feet=6,
        height_inches=4,
        weight=210,
        team="LAD",
        primary_position="DH",
        throws="R",
        bats="L",
    ),
]

# Numeric pitch values are seeded as strings on purpose — that mirrors the
# real database, where every pitch column is TEXT from the raw CSV ingest.
PITCHES = [
    # Valdez sinkers + a curveball to Ohtani
    dict(
        game_date="2025-10-01",
        pitch_type="SI",
        pitch_name="Sinker",
        player_name="Valdez, Framber",
        pitcher=2,
        batter=3,
        release_speed="94.1",
        release_spin_rate="2100",
        type="S",
        description="called_strike",
        balls="0",
        strikes="0",
        inning="1",
        home_team="HOU",
        away_team="LAD",
        stand="L",
        p_throws="L",
    ),
    dict(
        game_date="2025-10-01",
        pitch_type="SI",
        pitch_name="Sinker",
        player_name="Valdez, Framber",
        pitcher=2,
        batter=3,
        release_speed="95.3",
        release_spin_rate="2150",
        type="B",
        description="ball",
        balls="0",
        strikes="1",
        inning="1",
        home_team="HOU",
        away_team="LAD",
        stand="L",
        p_throws="L",
    ),
    dict(
        game_date="2025-10-02",
        pitch_type="CU",
        pitch_name="Curveball",
        player_name="Valdez, Framber",
        pitcher=2,
        batter=3,
        release_speed="79.8",
        release_spin_rate="2800",
        type="X",
        description="hit_into_play",
        events="single",
        balls="1",
        strikes="1",
        inning="3",
        home_team="LAD",
        away_team="HOU",
        stand="L",
        p_throws="L",
    ),
    # A pitch with no recorded velocity (mirrors real data gaps)
    dict(
        game_date="2025-10-03",
        pitch_type="FF",
        pitch_name="4-Seam Fastball",
        player_name="Valdez, Framber",
        pitcher=2,
        batter=1,
        release_speed="",
        release_spin_rate="",
        type="B",
        description="ball",
        balls="0",
        strikes="0",
        inning="5",
        home_team="HOU",
        away_team="LAD",
        stand="R",
        p_throws="L",
    ),
]


@pytest.fixture
def app():
    """App bound to a seeded in-memory database."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        db.session.add_all([Player(**p) for p in PLAYERS])
        db.session.add_all([Pitch(**p) for p in PITCHES])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
