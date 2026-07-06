"""Shared test fixtures.

Tests run against a seeded in-memory SQLite database rather than the real
baseball.db so they are fast, deterministic, and independent of the shipped
data.
"""

import pytest

from app import create_app
from app.extensions import db
from app.models import Player

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
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
