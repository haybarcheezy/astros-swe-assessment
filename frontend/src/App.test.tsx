import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import App from "./App";
import ApiService from "./services/api";

// Mock the API layer so App tests don't need a running backend.
vi.mock("./services/api", () => ({
  default: {
    getPlayers: vi.fn(),
    getTeams: vi.fn(),
    getPositions: vi.fn(),
    getPitchTypes: vi.fn(),
    getPitches: vi.fn(),
  },
}));

const mocked = vi.mocked(ApiService, true);

beforeEach(() => {
  mocked.getTeams.mockResolvedValue(["HOU"]);
  mocked.getPositions.mockResolvedValue(["2B"]);
  mocked.getPitchTypes.mockResolvedValue([{ code: "FF", name: "4-Seam" }]);
  mocked.getPitches.mockResolvedValue({
    data: [],
    pagination: { page: 1, per_page: 50, total: 0, total_pages: 1 },
  });
  mocked.getPlayers.mockResolvedValue({
    data: [
      {
        player_id: 1,
        first_name: "Jose",
        last_name: "Altuve",
        birthdate: "1990-05-06",
        birth_country: "Venezuela",
        birth_state: null,
        height_feet: 5,
        height_inches: 6,
        weight: 166,
        team: "HOU",
        primary_position: "2B",
        throws: "R",
        bats: "R",
      },
    ],
    pagination: { page: 1, per_page: 50, total: 1, total_pages: 1 },
  });
});

describe("App", () => {
  it("renders the header and player data from the API", async () => {
    render(<App />);
    expect(
      screen.getByText(/baseball player statistics/i)
    ).toBeInTheDocument();
    expect(await screen.findByText("Altuve, Jose")).toBeInTheDocument();
  });

  it("shows an error message when the players request fails", async () => {
    mocked.getPlayers.mockRejectedValueOnce(new Error("network"));
    render(<App />);
    expect(
      await screen.findByText(/failed to load players/i)
    ).toBeInTheDocument();
  });
});
