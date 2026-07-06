import React, { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";
import {
  Pagination as PaginationMeta,
  Pitch,
  PitchFilterOptions,
  PitchType,
  Player,
  PlayerFilterOptions,
} from "./types";
import ApiService from "./services/api";
import ArsenalPanel from "./components/ArsenalPanel";
import Pagination from "./components/Pagination";
import PitchFilterControls from "./components/PitchFilterControls";
import PitchTable from "./components/PitchTable";
import PlayerFilterControls from "./components/PlayerFilterControls";
import PlayerTable from "./components/PlayerTable";

type Tab = "players" | "pitches";

const DEBOUNCE_MS = 300;

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>("players");

  // Shared reference data
  const [availableTeams, setAvailableTeams] = useState<string[]>([]);
  const [availablePositions, setAvailablePositions] = useState<string[]>([]);
  const [availablePitchTypes, setAvailablePitchTypes] = useState<PitchType[]>([]);

  // Players state
  const [players, setPlayers] = useState<Player[]>([]);
  const [playerFilters, setPlayerFilters] = useState<PlayerFilterOptions>({});
  const [playerPagination, setPlayerPagination] = useState<PaginationMeta | null>(null);
  const [playersLoading, setPlayersLoading] = useState(false);
  const [playersError, setPlayersError] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  // Pitches state
  const [pitches, setPitches] = useState<Pitch[]>([]);
  const [pitchFilters, setPitchFilters] = useState<PitchFilterOptions>({});
  const [pitchPagination, setPitchPagination] = useState<PaginationMeta | null>(null);
  const [pitchesLoading, setPitchesLoading] = useState(false);
  const [pitchesError, setPitchesError] = useState("");

  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Load dropdown reference data once on mount.
  useEffect(() => {
    ApiService.getTeams().then(setAvailableTeams).catch(() => { });
    ApiService.getPositions().then(setAvailablePositions).catch(() => { });
    ApiService.getPitchTypes().then(setAvailablePitchTypes).catch(() => { });
  }, []);

  // Fetch players when filters change (debounced for the search box).
  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setPlayersLoading(true);
      setPlayersError("");
      ApiService.getPlayers(playerFilters)
        .then((res) => {
          setPlayers(res.data);
          setPlayerPagination(res.pagination);
        })
        .catch(() => setPlayersError("Failed to load players."))
        .finally(() => setPlayersLoading(false));
    }, DEBOUNCE_MS);
    return () => clearTimeout(debounceRef.current);
  }, [playerFilters]);

  // Fetch pitches when filters change.
  useEffect(() => {
    setPitchesLoading(true);
    setPitchesError("");
    ApiService.getPitches(pitchFilters)
      .then((res) => {
        setPitches(res.data);
        setPitchPagination(res.pagination);
      })
      .catch(() => setPitchesError("Failed to load pitches."))
      .finally(() => setPitchesLoading(false));
  }, [pitchFilters]);

  const handlePlayerFilterChange = useCallback((filters: PlayerFilterOptions) => {
    setPlayerFilters({ ...filters, page: 1 });
  }, []);

  const handlePitchFilterChange = useCallback((filters: PitchFilterOptions) => {
    setPitchFilters({ ...filters, page: 1 });
  }, []);

  return (
    <div className="App">
      <header>
        <h1>Baseball Player Statistics</h1>
        <p>Explore 2025 MLB postseason player and pitch data</p>
        <nav className="tabs">
          <button
            className={activeTab === "players" ? "tab active" : "tab"}
            onClick={() => setActiveTab("players")}
          >
            Players
          </button>
          <button
            className={activeTab === "pitches" ? "tab active" : "tab"}
            onClick={() => setActiveTab("pitches")}
          >
            Pitches
          </button>
        </nav>
      </header>

      <main>
        {activeTab === "players" && (
          <>
            <section className="filter-section">
              <PlayerFilterControls
                onFilterChange={handlePlayerFilterChange}
                availableTeams={availableTeams}
                availablePositions={availablePositions}
              />
            </section>

            {selectedPlayer && (
              <section className="arsenal-section">
                <ArsenalPanel
                  playerId={selectedPlayer.player_id}
                  onClose={() => setSelectedPlayer(null)}
                />
              </section>
            )}

            <section className="data-section">
              <PlayerTable
                players={players}
                isLoading={playersLoading}
                error={playersError}
                totalCount={playerPagination?.total}
                onSelectPlayer={setSelectedPlayer}
                selectedPlayerId={selectedPlayer?.player_id}
              />
              {playerPagination && (
                <Pagination
                  pagination={playerPagination}
                  onPageChange={(page) =>
                    setPlayerFilters((f) => ({ ...f, page }))
                  }
                />
              )}
            </section>
          </>
        )}

        {activeTab === "pitches" && (
          <>
            <section className="filter-section">
              <PitchFilterControls
                onFilterChange={handlePitchFilterChange}
                availablePitchTypes={availablePitchTypes}
                availableTeams={availableTeams}
              />
            </section>

            <section className="data-section">
              <PitchTable
                pitches={pitches}
                isLoading={pitchesLoading}
                error={pitchesError}
                totalCount={pitchPagination?.total}
              />
              {pitchPagination && (
                <Pagination
                  pagination={pitchPagination}
                  onPageChange={(page) =>
                    setPitchFilters((f) => ({ ...f, page }))
                  }
                />
              )}
            </section>
          </>
        )}
      </main>

      <footer>
        <p>Houston Astros - Software Engineer Assessment</p>
      </footer>
    </div>
  );
};

export default App;
