# UniWay Craiova

> An indoor navigation web application for the Faculty of Horticulture in Craiova.

UniWay helps students, staff, and first-time visitors find classrooms and facilities inside a multi-floor university building. Instead of relying on written directions alone, the app calculates a route and draws it directly on the relevant floor plan.

## Why this project

University buildings can be difficult to navigate, especially when rooms are distributed across several floors and corridors are not directly connected. This project explores a practical indoor-routing solution built around real building plans, a graph-based model of the space, and a lightweight web interface.

## Highlights

- Finds routes from a selected entrance or room to a destination.
- Supports multi-floor routing through connected staircases.
- Draws the active route as an SVG overlay on real floor-plan images.
- Lets users navigate a route step by step between floors.
- Supports classroom search and quick navigation to restrooms.
- Includes Romanian and English interface text.
- Uses WebP floor plans and browser caching to reduce page weight and loading time.
- Includes a Google Forms link for reporting map or routing issues.

## How it works

The building is modeled as a weighted graph:

- **Nodes** are corridor landmarks and access points such as `P1`, `P12`, or `P20`.
- **Edges** represent valid corridor connections on the same floor.
- **Vertical edges** connect matching staircases between floors.
- **Room data** maps each room to one or more graph nodes and to a visual coordinate on the floor plan.

The application combines all floors into one graph and uses a Dijkstra-style shortest-path search. Moving along corridors uses geometric distance between points; changing floors has an additional staircase cost. The resulting global route is then split into floor-specific stages and rendered on the corresponding plan.

## Tech stack

- **Python** — application logic and routing engine
- **WSGI / Gunicorn** — web serving locally and on Render
- **HTML and CSS** — responsive user interface
- **SVG** — route overlays and map markers
- **WebP** — optimized floor-plan assets
- **Dijkstra's algorithm** — weighted shortest-path routing
- **Render** — deployment configuration

## Project structure

```text
.
├── app.py                 # WSGI application, graph model, routing, and HTML rendering
├── styles.css             # Responsive visual design and map overlay styles
├── data/
│   ├── rooms.py           # Classroom metadata and map coordinates
│   ├── restrooms.py       # Restroom metadata and categories
│   └── starts.py          # Entrances and other valid starting points
├── *.webp                 # Optimized floor plans
├── requirements.txt       # Production dependency list
└── render.yaml            # Render deployment configuration
```

## Run locally

**Prerequisites:** Python 3.10 or newer.

```powershell
git clone https://github.com/gamanradu16-ui/Uniwaze.git
cd Uniwaze
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser.

## Data model

The project keeps frequently edited map data separate from the routing and UI code:

- Add or update classrooms in `data/rooms.py`.
- Add restrooms in `data/restrooms.py` using `female`, `male`, or `unisex` types.
- Add entrances or starting positions in `data/starts.py`.
- Update graph points, corridor connections, stairs, and floor configuration in `app.py`.

Each room needs an identifier, display name, floor, graph point, and visual coordinates. This separation makes the system easier to maintain as plans and room data evolve.

## Deployment

The repository includes `render.yaml` for deployment on Render. The production server starts with:

```text
gunicorn app:app
```

## Testing

The application has been validated through functional routing scenarios, including same-floor paths, multi-floor paths, stair transitions, and routes to restrooms. Syntax validation can be run with:

```powershell
python -m py_compile app.py
```

## Current limitations and future work

- Floor maps and graph coordinates are maintained manually.
- Route quality depends on the accuracy of corridor and stair connections in the graph.
- Automated routing tests would improve regression coverage.
- A future version could use vector floor plans, a database-backed editing interface, and accessibility-aware route preferences.

## Author

**Gaman Mihnea Radu**

Academic coordinators: **Smaranda Belciug** and **Florin Ispas**
