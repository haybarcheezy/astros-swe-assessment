# Baseball Player Statistics Dashboard

A full-stack web application for exploring and visualizing baseball player statistics. Built with Flask (Python) backend and React (TypeScript) frontend.

## Project Structure

```
├── backend/                 # Python Flask API
│   ├── main.py              # Entry point (creates the app via factory)
│   ├── app/
│   │   ├── __init__.py      # App factory, blueprint registration, error handlers
│   │   ├── extensions.py    # Shared Flask extensions (SQLAlchemy)
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Marshmallow response + query-validation schemas
│   │   └── routes/
│   │       ├── __init__.py  # Shared helpers (query validation, pagination)
│   │       ├── players.py   # /api/players endpoints + arsenal summary
│   │       └── pitches.py   # /api/pitches endpoints
│   ├── data/
│   │   ├── baseball.db      # SQLite Database with players and pitches table
│   │   ├── players.csv      # Player data that is already ingested into the players table
│   │   ├── pitches.csv      # Pitch data sample from the 2025 MLB postseason that is already ingested into the pitches table
│   ├── tests/
│   │   ├── conftest.py      # Seeded in-memory DB fixtures
│   │   ├── test_api.py      # API tests
│   │   └── __init__.py
│   ├── requirements.txt     # Python dependencies
│   └── pytest.ini           # Test configuration
├── frontend/                # React TypeScript application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── ArsenalPanel.tsx
│   │   │   ├── Pagination.tsx
│   │   │   ├── PitchFilterControls.tsx
│   │   │   ├── PitchTable.tsx
│   │   │   ├── PlayerFilterControls.tsx
│   │   │   ├── PlayerTable.tsx
│   │   │   └── __tests__/   # Component tests
│   │   ├── services/        # API service layer
│   │   │   └── api.ts
│   │   ├── types/           # TypeScript type definitions
│   │   │   └── index.ts
│   │   ├── App.tsx          # Main App component (Players/Pitches tabs)
│   │   ├── App.css          # Styles
│   │   ├── index.css        # Global styles
│   │   ├── index.tsx        # Entry point
│   │   └── App.test.tsx     # Component tests
│   ├── package.json
│   ├── tsconfig.json
├── .github/workflows/ci.yml # CI: pytest, tsc, vitest on push/PR
├── QUESTIONS.md             # Development practices questions
├── .gitignore               # Git ignore patterns
├── START_HERE.md            # Assessment introduction
└── README.md                # This file
```

## Quick Start

### Prerequisites

**Option 1: VS Code Dev Containers (Recommended)**

- Docker or Docker Desktop
- VS Code with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

**Option 2: Traditional Local Setup**

- Python 3.11+
- Node.js 18+
- npm, yarn, or bun

### Development with VS Code Dev Containers (Recommended)

**Setup Steps:**

1. **Install Prerequisites:**
   - Install [Docker](https://docs.docker.com/engine/install/) or [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Install [VS Code](https://code.visualstudio.com/)
   - Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open the Project:**
   Open the project folder in vscode or through the terminal:

   ```bash
   # Clone your forked repository
   git clone <your-repo-url>
   cd tech-assessment-staff-swe

   # Open the project in VS Code
   code .
   ```

3. **Start Dev Containers:**
   - VS Code will detect the dev container configuration
   - Click "Reopen in Container" when prompted (or use `Ctrl+Shift+P` → "Dev Containers: Reopen in Container")
   - VS Code will build and start both backend and frontend containers
   - Dependencies will be automatically installed
   - This may take a few minutes on first run

4. **Start Development:**
   - Backend will be available at: http://localhost:5001
   - Frontend will be available at: http://localhost:3000
   - Code changes will automatically be reflected in the frontend and backend via hot-reload.

**Working with Dev Containers:**

- All VS Code extensions (Python, Pylance, ESLint, etc.) are automatically installed
- To rebuild containers: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"
- To view logs of the frontend or backend, first open a terminal outsides of the devcontainer and then you can run `docker logs baseball-stats-frontend -f` or `docker logs baseball-stats-backend -f`
- When done working with the containers, they should automatically stop running once the vscode editor is closed.
  - To manually kill the containers first run `docker ps` to check if they are still running and then use `docker kill <name of container>` to stop them.

**Troubleshooting:**

- **Container won't start:** Ensure Docker is running
- **Dependencies not installed:** Rebuild the container (`Ctrl+Shift+P` → "Rebuild Container")
- **Port conflicts:** Stop any local services running on ports 5001 or 3000

### Traditional Local Development Setup

**Fork and navigate to the project:**

```bash
git clone <your-repo-url>
cd tech-assessment-staff-swe
```

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv\Scripts\activate # On Windows
source venv/bin/activate     # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the backend server
flask --app main run --host=0.0.0.0 --port=5001 --debug
```

Backend will be available at: http://localhost:5001

**Frontend Setup (in a new terminal):**

```bash
cd frontend

# Install dependencies using npm/yarn/bun/etc.
npm install

# Start the development server
npm start
```

Frontend will be available at: http://localhost:3000

## Running Tests

### Backend Tests

```bash
cd backend
# in dev container make sure to activate the virtual environment in the backend directory via: source .venv/bin/activate
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test # if using the dev container this will be 'bun test' instead
```

## Features

### Completed

- [x] REST API for player and pitch data access
  - `GET /api/players` — team, position, and name-search filters with pagination
  - `GET /api/players/<id>` — single player with 404 handling
  - `GET /api/players/teams` and `/api/players/positions` — filter dropdown data
  - `GET /api/players/<id>/arsenal` — pitch mix summary: usage %, avg/max velocity, avg spin per pitch type
  - `GET /api/pitches` — filters for pitcher, batter, player (thrown *or* seen), pitch type, team, velocity range, and date range, with pagination
  - `GET /api/pitches/types` — pitch type codes and display names
  - Query-parameter validation via marshmallow (bad input → 400 with field-level messages)
  - Consistent response envelope: `{ data: [...], pagination: { page, per_page, total, total_pages } }`
- [x] Player and pitch data tables with filtering
  - Tabbed UI (Players / Pitches) with debounced name search and pagination controls
  - Loading, error, and empty states on both tables
  - Click a player row to open their pitch arsenal panel
- [x] Unit/integration tests
  - Backend: 29 pytest tests against a seeded in-memory SQLite DB (fixtures deliberately store numerics as strings to mirror the real TEXT columns, including a blank-velocity row)
  - Frontend: 11 vitest/Testing Library tests with a mocked API layer
- [x] CI: GitHub Actions workflow running pytest, tsc, and vitest on every push/PR

### Answering the assessment's example questions

| Question | How |
|---|---|
| What pitches did player X throw? | `/api/pitches?pitcher=<id>` or the arsenal panel |
| What pitches did player X see? | `/api/pitches?batter=<id>` |
| How many pitches did X throw or see? | `pagination.total` on `/api/pitches?player_id=<id>` |
| What pitches were thrown at ≥95 mph? | `/api/pitches?min_velocity=95` (4,418 in this dataset) |
| What players were on team X? | `/api/players?team=<code>` |

### Notes, findings, and trade-offs

- **TEXT columns in the pitches table.** Every column in the shipped `pitches` table is TEXT (raw CSV ingest). SQLite orders any TEXT above any number, so a naive `release_speed >= 95` filter silently returns wrong rows. Velocity filters and arsenal aggregates `CAST(... AS REAL)` at query time, and the serialization layer coerces values so the API emits real JSON numbers (blank values become `null`). The long-term fix is re-ingesting with typed columns plus indexes on `pitcher`, `batter`, and `game_date` — done as expand-and-contract, that's a zero-downtime migration.
- **Proxy configuration.** The starter's Vite proxy targeted `http://backend:5001` (only resolvable inside the compose network) while `VITE_API_URL` had the browser call Flask directly and rely on CORS. Standardized on same-origin `/api` requests through the dev-server proxy with a configurable `BACKEND_URL` target, so local dev and the devcontainer share one code path.
- **Python 3.13 compatibility.** SQLAlchemy 2.0.23 fails to import on Python 3.13 and pandas 2.1.4 has no 3.13 wheels; both bumped. The devcontainer (3.12) was unaffected.
- **Starter contained a file named `NUL`** in `backend/`, which is a reserved device name on Windows and breaks `git add`; removed before the baseline commit.
- **Pagination is offset-based** for simplicity at this scale; I'd switch to cursor-based pagination before the pitch table grows meaningfully.
- **Fun data note:** the dataset is 2025 postseason only — so `/api/players?team=HOU` comes back empty. Condolences to the reviewers.

### With more time

- Sortable table columns and CSV export of filtered results
- SVG strike-zone overlay plotting pitch locations from `plate_x`/`plate_z`, filterable by pitch type and count. For hitters, a heat map over the zone: green where they do the most damage, red for their cold zones (e.g. up-and-in on fastballs), built from `launch_speed`/`events` by zone. This is the view I'd want as a player, and probably the feature I was most tempted to build anyway
- Whiff/chase rates by zone in the arsenal view
- Re-ingest with typed columns + indexes; cursor pagination
- Structured JSON logging with request IDs; error tracking
- Terraform-managed deploy to AWS (ECS Fargate behind an ALB; RDS Postgres replacing SQLite) — build once in CI, promote the same image through environments.

## Database

The application includes a pre-populated SQLite database (`backend/data/baseball.db`) which contains 2025 postseason MLB data with with two tables:

### Players Table (297 records)

Player data from 2025 postseason MLB games:

| Column           | Type    | Description                                  |
| ---------------- | ------- | -------------------------------------------- |
| player_id        | INTEGER | Unique player identifier                     |
| first_name       | TEXT    | Player's first name                          |
| last_name        | TEXT    | Player's last name                           |
| birthdate        | TEXT    | Birth date (YYYY-MM-DD)                      |
| birth_country    | TEXT    | Country of birth                             |
| birth_state      | TEXT    | State/province of birth (nullable)           |
| height_feet      | INTEGER | Height in feet                               |
| height_inches    | INTEGER | Additional inches                            |
| weight           | INTEGER | Weight in pounds                             |
| team             | TEXT    | Current team (3-letter code: LAD, NYY, etc.) |
| primary_position | TEXT    | Position code (SS, RHS, LHR, CF, etc.)       |
| throws           | TEXT    | Throwing hand (R/L)                          |
| bats             | TEXT    | Batting hand (R/L/S for switch)              |

### Pitches Table (14,059 records)

Pitch data from 2025 postseason MLB games. Key fields include:

| Column            | Type    | Description                                             |
| ----------------- | ------- | ------------------------------------------------------- |
| pitch_type        | TEXT    | Pitch classification (FF, SL, CU, CH, etc.)             |
| game_date         | TEXT    | Date of game (YYYY-MM-DD)                               |
| release_speed     | REAL    | Pitch velocity in mph                                   |
| player_name       | TEXT    | Pitcher name ("Last, First" format)                     |
| pitcher           | INTEGER | Pitcher's player_id (foreign key)                       |
| batter            | INTEGER | Batter's player_id (foreign key)                        |
| events            | TEXT    | At-bat outcome (single, strikeout, home_run, etc.)      |
| description       | TEXT    | Pitch result (called_strike, ball, hit_into_play, etc.) |
| zone              | INTEGER | Strike zone location (1-14, null if outside)            |
| type              | TEXT    | Pitch result type (S=strike, B=ball, X=in play)         |
| balls             | INTEGER | Balls in count before pitch                             |
| strikes           | INTEGER | Strikes in count before pitch                           |
| plate_x           | REAL    | Horizontal pitch location (feet)                        |
| plate_z           | REAL    | Vertical pitch location (feet)                          |
| launch_speed      | REAL    | Exit velocity in mph (when ball is hit)                 |
| launch_angle      | REAL    | Launch angle in degrees (when ball is hit)              |
| release_spin_rate | REAL    | Spin rate in RPM                                        |
| inning            | INTEGER | Inning number                                           |
| home_team         | TEXT    | Home team code                                          |
| away_team         | TEXT    | Away team code                                          |
| stand             | TEXT    | Batter handedness (L/R)                                 |
| p_throws          | TEXT    | Pitcher handedness (L/R)                                |

**Note:** For complete field documentation, see the [Baseball Savant CSV Documentation](https://baseballsavant.mlb.com/csv-docs).

In the backend, the db models and schemas are already implemented for you. You may edit them as you see fit.
The pitches model and schema only include a subset of all the fields from the pitches table, you are free to add more if wanted.

**Schemas:** Marshmallow schemas for both tables are already implemented in `backend/app/schemas.py`.

**Models:** SqlAlchemy models are defined in `backend/app/models.py`.

## Frontend

A starting point has been created to implement a player table and its filters. Feel free to restructure the code as you see fit and create any other components that will be needed.

## Next Steps for Implementation

1. Finish the React components and API integration
2. Add comprehensive error handling and validation
3. Complete the test suites
4. Add styling and improve user experience

## Bonus Features (Optional)

If you finish the core requirements early or want to demonstrate additional skills, consider implementing:

- Advanced filtering and sorting in the UI
- Data export functionality
- Enhanced error handling and user feedback
- Input validation improvements
- Performance optimizations
- Additional test coverage
- Set up logging and monitoring

## Time Management Notes

This assessment is designed to take 2-3 hours. Focus on:

- Core functionality (upload, store, display)
- Code quality and structure
- Basic testing
- Clear documentation

Don't worry about:

- Production-ready security
- Advanced UI/UX features
- Comprehensive error scenarios
- Performance optimization

## Questions or Issues

If you encounter any setup issues or have questions about the requirements, please include them in your submission documentation.
