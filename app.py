from html import escape
from math import atan2, degrees, sqrt
import os
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
FLOOR_PLAN_PATH = Path(__file__).with_name("parter incercare.png")

TEXT = {
    "ro": {
        "html_lang": "ro",
        "app_title": "UniWay Craiova",
        "eyebrow": "Navigare universitara",
        "hero_title": "Gaseste rapid sala din Universitatea din Craiova.",
        "hero_stat_1": "cladiri demo",
        "hero_stat_2": "sali incluse",
        "hero_stat_3": "server-side",
        "planner_label": "Planificator traseu",
        "planner_title": "Unde vrei sa ajungi?",
        "start_label": "Punct de plecare",
        "room_label": "Sala dorita",
        "room_placeholder": "Ex: C205 sau Aula Magna",
        "submit": "Arata traseul",
        "quick_rooms": "Sugestii sali",
        "map_tag": "Harta campus",
        "map_title": "Vedere rapida asupra traseului",
        "live_pill": "Python app",
        "route_tag": "Ghidare",
        "rooms_tag": "Sali populare",
        "rooms_title": "Destinatii rapide",
        "default_summary": "Introdu numele unei sali pentru a vedea traseul recomandat.",
        "default_title": "Alege o sala",
        "not_found_title": "Sala nu a fost gasita",
        "not_found_summary": "Incearca una dintre salile sugerate, de exemplu C205, S24 sau Amfiteatrul E1.",
        "from_prefix": "Pleci din {start}.",
        "to_prefix": "Mergi catre {building}.",
        "language_switch": "Schimba limba",
        "landing_title": "Alege limba in care vrei sa folosesti aplicatia.",
        "landing_title_secondary": "Choose the language you want to use for the app.",
        "landing_text": "Selecteaza romana sau english pentru a primi indicatii mai usor de urmarit in facultate.",
        "landing_ro": "Romana",
        "landing_en": "English",
    },
    "en": {
        "html_lang": "en",
        "app_title": "UniWay Craiova",
        "eyebrow": "Campus navigation",
        "hero_title": "Find your classroom at the University of Craiova.",
        "hero_stat_1": "demo buildings",
        "hero_stat_2": "rooms included",
        "hero_stat_3": "server-side",
        "planner_label": "Route planner",
        "planner_title": "Where do you want to go?",
        "start_label": "Starting point",
        "room_label": "Desired room",
        "room_placeholder": "Ex: C205 or Aula Magna",
        "submit": "Show route",
        "quick_rooms": "Suggested rooms",
        "map_tag": "Campus map",
        "map_title": "Quick route overview",
        "live_pill": "Python app",
        "route_tag": "Directions",
        "rooms_tag": "Popular rooms",
        "rooms_title": "Quick destinations",
        "default_summary": "Enter a room name to see the recommended route.",
        "default_title": "Choose a room",
        "not_found_title": "Room not found",
        "not_found_summary": "Try one of the suggested rooms, for example C205, S24 or Amfiteatrul E1.",
        "from_prefix": "You start from {start}.",
        "to_prefix": "Head towards {building}.",
        "language_switch": "Change language",
        "landing_title": "Choose the language for the app.",
        "landing_title_secondary": "Alege limba in care vrei sa folosesti aplicatia.",
        "landing_text": "Select Romanian or English so the directions are easier to follow around the faculty.",
        "landing_ro": "Romanian",
        "landing_en": "English",
    },
}

START_POINT_LABELS = {
    "intrare-principala": {"ro": "Intrare principala", "en": "Main entrance"},
    "parcare-centrala": {"ro": "Parcare centrala", "en": "Central parking"},
    "camin-campus": {"ro": "Camin campus", "en": "Dormitory"},
    "biblioteca": {"ro": "Biblioteca universitatii", "en": "University library"},
}

BUILDING_LABELS = {
    "Corpul Central": {"ro": "Corpul Central", "en": "Central Building"},
    "Facultatea de Stiinte": {"ro": "Facultatea de Stiinte", "en": "Faculty of Science"},
    "Electrotehnica": {"ro": "Electrotehnica", "en": "Electrical Engineering"},
}

FLOOR_LABELS = {
    "Parter": {"ro": "Parter", "en": "Ground floor"},
    "Etajul 1": {"ro": "Etajul 1", "en": "1st floor"},
    "Etajul 2": {"ro": "Etajul 2", "en": "2nd floor"},
}


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


def t(lang):
    return TEXT["en"] if lang == "en" else TEXT["ro"]


def translate_start_label(key, lang):
    return START_POINT_LABELS.get(key, {}).get(lang, key)


def translate_building_label(label, lang):
    return BUILDING_LABELS.get(label, {}).get(lang, label)


def translate_floor_label(label, lang):
    return FLOOR_LABELS.get(label, {}).get(lang, label)


def render_options(selected_start, lang):
    options = []
    for key, value in START_POINTS.items():
        selected = " selected" if key == selected_start else ""
        options.append(
            f'<option value="{escape(key)}"{selected}>{escape(translate_start_label(key, lang))}</option>'
        )
    return "".join(options)


def render_quick_rooms(selected_start, lang):
    chips = []
    for room in ROOMS[:5]:
        chips.append(
            f'<a class="chip" href="/?lang={escape(lang)}&start={escape(selected_start)}&room={escape(room["name"])}">{escape(room["name"])}</a>'
        )
    return "".join(chips)


def render_room_grid(selected_start, lang):
    cards = []
    for room in ROOMS:
        cards.append(
            """
            <a class="room-card" href="/?lang={lang}&start={start}&room={room_name}">
              <strong>{name}</strong>
              <span>{building} - {floor}</span>
            </a>
            """.format(
                lang=escape(lang),
                start=escape(selected_start),
                room_name=escape(room["name"]),
                name=escape(room["name"]),
                building=escape(translate_building_label(room["building_label"], lang)),
                floor=escape(translate_floor_label(room["floor"], lang)),
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


def render_language_page():
    html = f"""<!DOCTYPE html>
<html lang="en">
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
  <main class="language-screen">
    <section class="language-card">
      <p class="eyebrow">UniWay Craiova</p>
      <h1>{TEXT["ro"]["landing_title"]}</h1>
      <p class="language-title-secondary">{TEXT["ro"]["landing_title_secondary"]}</p>
      <p class="language-text">{TEXT["ro"]["landing_text"]}</p>
      <p class="language-text">{TEXT["en"]["landing_text"]}</p>
      <div class="language-actions">
        <a class="language-button" href="/?lang=ro">{TEXT["ro"]["landing_ro"]}</a>
        <a class="language-button language-button--alt" href="/?lang=en">{TEXT["en"]["landing_en"]}</a>
      </div>
    </section>
  </main>
</body>
</html>
"""
    return html.encode("utf-8")


def render_page(selected_start, room_query, lang):
    text = t(lang)
    room = get_room(room_query)
    start = START_POINTS.get(selected_start, START_POINTS["intrare-principala"])
    start_label = translate_start_label(selected_start, lang)
    summary = text["default_summary"]
    steps = ""
    title = text["default_title"]
    route_lines = ""

    if room:
        building_label = translate_building_label(room["building_label"], lang)
        floor_label = translate_floor_label(room["floor"], lang)
        full_steps = [
            text["from_prefix"].format(start=start_label),
            text["to_prefix"].format(building=building_label),
            *room["steps"],
        ]
        title = room["name"]
        summary = f"{room['name']} - {building_label} - {floor_label}. {room['summary']}"
        steps = render_steps(full_steps)
        route_lines = render_route_lines(build_route_segments(start["coords"], room["coords"]))
    elif room_query:
        title = text["not_found_title"]
        summary = text["not_found_summary"]

    html = f"""<!DOCTYPE html>
<html lang="{text["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{text["app_title"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <div class="app-shell">
    <header class="hero">
      <div class="hero__copy">
        <p class="eyebrow">{text["eyebrow"]}</p>
        <h1>{text["hero_title"]}</h1>
        <div class="hero__stats">
          <div><strong>3</strong><span>{text["hero_stat_1"]}</span></div>
          <div><strong>9</strong><span>{text["hero_stat_2"]}</span></div>
          <div><strong>Python</strong><span>{text["hero_stat_3"]}</span></div>
        </div>
        <a class="language-link" href="/">{text["language_switch"]}</a>
      </div>

      <section class="planner-card" aria-labelledby="planner-title">
        <div class="planner-card__top">
          <p class="planner-card__label">{text["planner_label"]}</p>
          <h2 id="planner-title">{text["planner_title"]}</h2>
        </div>

        <form class="route-form" method="get" action="/">
          <input type="hidden" name="lang" value="{escape(lang)}">
          <label class="field">
            <span>{text["start_label"]}</span>
            <select id="start-point" name="start">
              {render_options(selected_start, lang)}
            </select>
          </label>

          <label class="field">
            <span>{text["room_label"]}</span>
            <input
              id="room-search"
              name="room"
              type="text"
              list="rooms-list"
              placeholder="{text["room_placeholder"]}"
              autocomplete="off"
              value="{escape(room_query)}"
            >
            <datalist id="rooms-list">
              {"".join(f'<option value="{escape(room["name"])}"></option>' for room in ROOMS)}
            </datalist>
          </label>

          <button type="submit" class="cta">{text["submit"]}</button>
        </form>

        <div class="quick-rooms" aria-label="{text["quick_rooms"]}">
          {render_quick_rooms(selected_start, lang)}
        </div>
      </section>
    </header>

    <main class="dashboard">
      <section class="map-card">
        <div class="section-head">
          <div>
            <p class="section-tag">{text["map_tag"]}</p>
            <h2>{text["map_title"]}</h2>
          </div>
          <span class="live-pill">{text["live_pill"]}</span>
        </div>

        <div class="campus-map">
          <img class="floor-plan" src="/parter.png" alt="Harta parterului">
          <div class="map-route">{route_lines}</div>
        </div>
      </section>

      <aside class="info-panel">
        <section class="route-panel">
          <div class="section-head section-head--compact">
            <div>
              <p class="section-tag">{text["route_tag"]}</p>
              <h2>{escape(title)}</h2>
            </div>
          </div>

          <div class="route-summary">{escape(summary)}</div>
          <ol class="steps">{steps}</ol>
        </section>

        <section class="rooms-panel">
          <div class="section-head section-head--compact">
            <div>
              <p class="section-tag">{text["rooms_tag"]}</p>
              <h2>{text["rooms_title"]}</h2>
            </div>
          </div>

          <div class="room-grid">
            {render_room_grid(selected_start, lang)}
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

    if path == "/parter.png":
        image = FLOOR_PLAN_PATH.read_bytes()
        start_response("200 OK", [("Content-Type", "image/png")])
        return [image]

    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Pagina nu a fost gasita."]

    params = parse_qs(environ.get("QUERY_STRING", ""))
    lang = params.get("lang", [""])[0]
    selected_start = params.get("start", ["intrare-principala"])[0]
    room_query = params.get("room", [""])[0]

    if lang not in TEXT:
        body = render_language_page()
    else:
        body = render_page(selected_start, room_query, lang)
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [body]


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"UniWay Craiova ruleaza la http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()
