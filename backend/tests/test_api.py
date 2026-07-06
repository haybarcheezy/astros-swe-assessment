"""API tests for health and player endpoints."""


class TestHealthCheck:
    """Test the health check endpoint."""

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "healthy"}


class TestPlayerAPI:
    """Test player-related API endpoints."""

    def test_get_all_players(self, client):
        resp = client.get("/api/players")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["pagination"]["total"] == 3
        assert len(body["data"]) == 3
        # Sorted by last name: Altuve, Ohtani, Valdez
        assert [p["last_name"] for p in body["data"]] == ["Altuve", "Ohtani", "Valdez"]

    def test_filter_players_by_team(self, client):
        resp = client.get("/api/players?team=HOU")
        body = resp.get_json()
        assert resp.status_code == 200
        assert body["pagination"]["total"] == 2
        assert all(p["team"] == "HOU" for p in body["data"])

    def test_filter_players_by_team_is_case_insensitive(self, client):
        resp = client.get("/api/players?team=hou")
        assert resp.get_json()["pagination"]["total"] == 2

    def test_filter_players_by_position(self, client):
        resp = client.get("/api/players?position=2B")
        body = resp.get_json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["last_name"] == "Altuve"

    def test_search_players_by_name(self, client):
        resp = client.get("/api/players?search=ohta")
        body = resp.get_json()
        assert body["pagination"]["total"] == 1
        assert body["data"][0]["last_name"] == "Ohtani"

    def test_players_pagination(self, client):
        resp = client.get("/api/players?page=2&per_page=2")
        body = resp.get_json()
        assert len(body["data"]) == 1
        assert body["pagination"] == {
            "page": 2,
            "per_page": 2,
            "total": 3,
            "total_pages": 2,
        }

    def test_invalid_query_param_returns_400(self, client):
        resp = client.get("/api/players?page=0")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_get_player_by_id(self, client):
        resp = client.get("/api/players/1")
        assert resp.status_code == 200
        assert resp.get_json()["last_name"] == "Altuve"

    def test_get_nonexistent_player(self, client):
        resp = client.get("/api/players/999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_get_teams(self, client):
        resp = client.get("/api/players/teams")
        assert resp.status_code == 200
        assert resp.get_json() == ["HOU", "LAD"]

    def test_get_positions(self, client):
        resp = client.get("/api/players/positions")
        assert resp.status_code == 200
        assert resp.get_json() == ["2B", "DH", "LHS"]
