from html import escape
from math import atan2, degrees, sqrt
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server


ROOMS = [
    {
        "id": "c101",
        "name": "C101",
        "building": "corpul-central",
        "building_label": "Corpul Central",
        "floor": "Parter",
        "coords": {"x": 49, "y": 25},
        "summary": "Sala de curs la parter, aproape de intrarea principala din Corpul Central.",
        "steps": [
            "Intra in Corpul Central pe usa principala.",
            "Mergi inainte pe holul principal aproximativ 20 de metri.",
            "Sala C101 este pe partea stanga, inainte de casa scarii.",
        ],
    },
    {
        "id": "c205",
        "name": "C205",
        "building": "corpul-central",
        "building_label": "Corpul Central",
        "floor": "Etajul 2",
        "coords": {"x": 53, "y": 22},
        "summary": "Sala de seminar la etajul 2 in Corpul Central.",
        "steps": [
            "Intra in Corpul Central si mergi spre casa scarii principala.",
            "Urca pana la etajul 2.",
            "La iesirea de pe scara, vireaza dreapta si continua pe coridor.",
            "C205 este pe partea dreapta, dupa al doilea colt.",
        ],
    },
    {
        "id": "aula-magna",
        "name": "Aula Magna",
        "building": "corpul-central",
        "building_label": "Corpul Central",
        "floor": "Etajul 1",
        "coords": {"x": 44, "y": 19},
        "summary": "Aula pentru evenimente mari, accesibila din Corpul Central.",
        "steps": [
            "Intra in Corpul Central si urca la etajul 1.",
            "Urmeaza indicatoarele pentru zona de evenimente.",
            "Aula Magna este la capatul coridorului principal.",
        ],
    },
    {
        "id": "s12",
        "name": "S12",
        "building": "facultatea-de-stiinte",
        "building_label": "Facultatea de Stiinte",
        "floor": "Parter",
        "coords": {"x": 30, "y": 61},
        "summary": "Sala de seminar in aripa de sud a Facultatii de Stiinte.",
        "steps": [
            "Intra in cladirea Facultatii de Stiinte.",
            "Tine stanga la receptie si intra pe coridorul sudic.",
            "S12 este a doua usa pe dreapta.",
        ],
    },
    {
        "id": "s24",
        "name": "S24",
        "building": "facultatea-de-stiinte",
        "building_label": "Facultatea de Stiinte",
        "floor": "Etajul 2",
        "coords": {"x": 27, "y": 55},
        "summary": "Sala de curs la etajul 2, in zona centrala a cladirii.",
        "steps": [
            "Intra in Facultatea de Stiinte si mergi spre scara centrala.",
            "Urca la etajul 2.",
            "Dupa scara, mergi inainte pana la panoul digital.",
            "Sala S24 se afla pe stanga.",
        ],
    },
    {
        "id": "lab-info-2",
        "name": "Laborator Info 2",
        "building": "facultatea-de-stiinte",
        "building_label": "Facultatea de Stiinte",
        "floor": "Etajul 1",
        "coords": {"x": 22, "y": 66},
        "summary": "Laborator de informatica in aripa vestica.",
        "steps": [
            "Intra in cladire si urca la etajul 1.",
            "Mergi spre aripa vestica, indicata cu panourile albastre.",
            "Laborator Info 2 este la capatul holului.",
        ],
    },
    {
        "id": "e08",
        "name": "E08",
        "building": "electrotehnica",
        "building_label": "Electrotehnica",
        "floor": "Parter",
        "coords": {"x": 73, "y": 55},
        "summary": "Sala de curs la parter, aproape de intrarea laterala.",
        "steps": [
            "Intra in cladirea de Electrotehnica pe accesul principal.",
            "Continua pe holul din dreapta.",
            "E08 este marcata imediat dupa laboratorul de masuratori.",
        ],
    },
    {
        "id": "e14",
        "name": "E14",
        "building": "electrotehnica",
        "building_label": "Electrotehnica",
        "floor": "Etajul 1",
        "coords": {"x": 76, "y": 48},
        "summary": "Sala de seminar la etajul 1, aproape de zona profesorala.",
        "steps": [
            "Intra in Electrotehnica si urca la etajul 1.",
            "Urmeaza coridorul principal pana la intersectia in T.",
            "Vireaza stanga si continua inca 15 metri.",
            "E14 este pe dreapta.",
        ],
    },
    {
        "id": "amfiteatrul-e1",
        "name": "Amfiteatrul E1",
        "building": "electrotehnica",
        "building_label": "Electrotehnica",
        "floor": "Parter",
        "coords": {"x": 69, "y": 62},
        "summary": "Amfiteatru mare pentru cursuri si prezentari.",
        "steps": [
            "Intra in cladire si pastreaza directia spre holul central.",
            "Treci de zona de afisaj si cauta intrarea larga din stanga.",
            "Amfiteatrul E1 este semnalizat deasupra accesului.",
        ],
    },
]

START_POINTS = {
    "intrare-principala": {
        "label": "Intrare principala",
        "coords": {"x": 14, "y": 76},
    },
    "parcare-centrala": {
        "label": "Parcare centrala",
        "coords": {"x": 26, "y": 55},
    },
    "camin-campus": {
        "label": "Camin campus",
        "coords": {"x": 81, "y": 84},
    },
    "biblioteca": {
        "label": "Biblioteca universitatii",
        "coords": {"x": 20, "y": 24},
    },
}

MAP_POINTS = [
    {"id": "intrare-principala", "label": "Intrare", "top": "72%", "left": "12%", "modifier": " map-point--start"},
    {"id": "parcare-centrala", "label": "Parcare", "top": "52%", "left": "24%", "modifier": ""},
    {"id": "biblioteca", "label": "Biblioteca", "top": "20%", "left": "18%", "modifier": ""},
    {"id": "camin-campus", "label": "Camin", "top": "82%", "left": "78%", "modifier": ""},
]

BUILDINGS = [
    {
        "id": "corpul-central",
        "name": "Corpul Central",
        "rooms": "C101, C205, Aula Magna",
        "class_name": "building building--central",
    },
    {
        "id": "facultatea-de-stiinte",
        "name": "Facultatea de Stiinte",
        "rooms": "S12, S24, Laborator Info 2",
        "class_name": "building building--stiinte",
    },
    {
        "id": "electrotehnica",
        "name": "Electrotehnica",
        "rooms": "E08, E14, Amfiteatrul E1",
        "class_name": "building building--electro",
    },
]

STYLES_PATH = Path(__file__).with_name("styles.css")


def get_room(query: str):
    normalized = (query or "").strip().lower()
    for room in ROOMS:
        if room["name"].lower() == normalized or room["id"].lower() == normalized:
            return room
    return None


def build_route_segments(start_coords, destination_coords):
    middle = {
        "x": (start_coords["x"] + destination_coords["x"]) / 2 + 3,
        "y": (start_coords["y"] + destination_coords["y"]) / 2 - 4,
    }
    return [
        calculate_line(start_coords, middle),
        calculate_line(middle, destination_coords),
    ]


def calculate_line(start, end):
    delta_x = end["x"] - start["x"]
    delta_y = end["y"] - start["y"]
    length = sqrt(delta_x * delta_x + delta_y * delta_y)
    angle = degrees(atan2(delta_y, delta_x))
    return {
        "left": f"{start['x']}%",
        "top": f"{start['y']}%",
        "width": f"{length}%",
        "angle": f"{angle}deg",
    }


def render_options(selected_start):
    options = []
    for key, value in START_POINTS.items():
        selected = " selected" if key == selected_start else ""
        options.append(
            f'<option value="{escape(key)}"{selected}>{escape(value["label"])}</option>'
        )
    return "".join(options)


def render_quick_rooms(selected_start):
    chips = []
    for room in ROOMS[:5]:
        chips.append(
            f'<a class="chip" href="/?start={escape(selected_start)}&room={escape(room["name"])}">{escape(room["name"])}</a>'
        )
    return "".join(chips)


def render_room_grid(selected_start):
    cards = []
    for room in ROOMS:
        cards.append(
            """
            <a class="room-card" href="/?start={start}&room={room_name}">
              <strong>{name}</strong>
              <span>{building} - {floor}</span>
            </a>
            """.format(
                start=escape(selected_start),
                room_name=escape(room["name"]),
                name=escape(room["name"]),
                building=escape(room["building_label"]),
                floor=escape(room["floor"]),
            )
        )
    return "".join(cards)


def render_map_points(selected_start):
    points = []
    for point in MAP_POINTS:
        active = " active" if point["id"] == selected_start else ""
        points.append(
            """
            <a class="map-point{modifier}{active}" href="/?start={start_id}" style="top: {top}; left: {left};">
              {label}
            </a>
            """.format(
                modifier=point["modifier"],
                active=active,
                start_id=escape(point["id"]),
                top=point["top"],
                left=point["left"],
                label=escape(point["label"]),
            )
        )
    return "".join(points)


def render_buildings(active_building):
    blocks = []
    for building in BUILDINGS:
        active = " active" if building["id"] == active_building else ""
        blocks.append(
            f'<article class="{building["class_name"]}{active}"><span>{escape(building["name"])}</span><small>{escape(building["rooms"])}</small></article>'
        )
    return "".join(blocks)


def render_route_lines(segments):
    if not segments:
        return ""

    lines = []
    for segment in segments:
        lines.append(
            '<div class="route-line" style="left: {left}; top: {top}; width: {width}; transform: rotate({angle});"></div>'.format(
                left=segment["left"],
                top=segment["top"],
                width=segment["width"],
                angle=segment["angle"],
            )
        )
    return "".join(lines)


def render_steps(steps):
    return "".join(f"<li>{escape(step)}</li>" for step in steps)


def render_page(selected_start, room_query):
    room = get_room(room_query)
    start = START_POINTS.get(selected_start, START_POINTS["intrare-principala"])
    summary = "Introdu numele unei sali pentru a vedea traseul recomandat."
    steps = ""
    title = "Alege o sala"
    active_building = ""
    route_lines = ""

    if room:
        full_steps = [
            f"Pleci din {start['label']}.",
            f"Mergi catre {room['building_label']}.",
            *room["steps"],
        ]
        title = room["name"]
        summary = f"{room['name']} - {room['building_label']} - {room['floor']}. {room['summary']}"
        steps = render_steps(full_steps)
        active_building = room["building"]
        route_lines = render_route_lines(build_route_segments(start["coords"], room["coords"]))
    elif room_query:
        title = "Sala nu a fost gasita"
        summary = "Incearca una dintre salile sugerate, de exemplu C205, S24 sau Amfiteatrul E1."

    html = f"""<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UniWay Craiova</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <div class="app-shell">
    <header class="hero">
      <div class="hero__copy">
        <p class="eyebrow">Navigare universitara</p>
        <h1>Gaseste rapid sala din Universitatea din Craiova.</h1>
        <p class="hero__text">
          Un prototip de tip Waze pentru campus: alegi de unde pleci, cauti sala,
          iar aplicatia iti arata traseul si pasii de urmat.
        </p>
        <div class="hero__stats">
          <div><strong>3</strong><span>cladiri demo</span></div>
          <div><strong>9</strong><span>sali incluse</span></div>
          <div><strong>Python</strong><span>server-side</span></div>
        </div>
      </div>

      <section class="planner-card" aria-labelledby="planner-title">
        <div class="planner-card__top">
          <p class="planner-card__label">Planificator traseu</p>
          <h2 id="planner-title">Unde vrei sa ajungi?</h2>
        </div>

        <form class="route-form" method="get" action="/">
          <label class="field">
            <span>Punct de plecare</span>
            <select id="start-point" name="start">
              {render_options(selected_start)}
            </select>
          </label>

          <label class="field">
            <span>Sala dorita</span>
            <input
              id="room-search"
              name="room"
              type="text"
              list="rooms-list"
              placeholder="Ex: C205 sau Aula Magna"
              autocomplete="off"
              value="{escape(room_query)}"
            >
            <datalist id="rooms-list">
              {"".join(f'<option value="{escape(room["name"])}"></option>' for room in ROOMS)}
            </datalist>
          </label>

          <button type="submit" class="cta">Arata traseul</button>
        </form>

        <div class="quick-rooms" aria-label="Sugestii sali">
          {render_quick_rooms(selected_start)}
        </div>
      </section>
    </header>

    <main class="dashboard">
      <section class="map-card">
        <div class="section-head">
          <div>
            <p class="section-tag">Harta campus</p>
            <h2>Vedere rapida asupra traseului</h2>
          </div>
          <span class="live-pill">Python app</span>
        </div>

        <div class="campus-map">
          <div class="map-route">{route_lines}</div>
          {render_map_points(selected_start)}
          {render_buildings(active_building)}
        </div>
      </section>

      <aside class="info-panel">
        <section class="route-panel">
          <div class="section-head section-head--compact">
            <div>
              <p class="section-tag">Ghidare</p>
              <h2>{escape(title)}</h2>
            </div>
          </div>

          <div class="route-summary">{escape(summary)}</div>
          <ol class="steps">{steps}</ol>
        </section>

        <section class="rooms-panel">
          <div class="section-head section-head--compact">
            <div>
              <p class="section-tag">Sali populare</p>
              <h2>Destinatii rapide</h2>
            </div>
          </div>

          <div class="room-grid">
            {render_room_grid(selected_start)}
          </div>
        </section>
      </aside>
    </main>
  </div>
</body>
</html>
"""
    return html.encode("utf-8")


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/styles.css":
        css = STYLES_PATH.read_bytes()
        start_response("200 OK", [("Content-Type", "text/css; charset=utf-8")])
        return [css]

    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Pagina nu a fost gasita."]

    params = parse_qs(environ.get("QUERY_STRING", ""))
    selected_start = params.get("start", ["intrare-principala"])[0]
    room_query = params.get("room", [""])[0]

    body = render_page(selected_start, room_query)
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [body]


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print(f"UniWay Craiova ruleaza la http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()
