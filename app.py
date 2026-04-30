from html import escape
from math import atan2, degrees, sqrt
import os
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

MAP_WIDTH = 2048
MAP_HEIGHT = 992
MAP_RATIO = MAP_HEIGHT / MAP_WIDTH


POINTS = {
    "P1": {"x": 6.6, "y": 49.5},
    "P2": {"x": 6.6, "y": 85.7},
    "P3": {"x": 6.6, "y": 11.7},
    "P4": {"x": 49.0, "y": 49.0},
    "P5": {"x": 49.0, "y": 85.7},
    "P6": {"x": 49.0, "y": 11.7},
    "P7": {"x": 61.7, "y": 85.7},
    "P8": {"x": 61.7, "y": 11.7},
    "P9": {"x": 93.9, "y": 11.7},
    "P10": {"x": 93.9, "y": 85.7},
    "P11": {"x": 61.7, "y": 35.9},
    "P12": {"x": 61.7, "y": 49.2},
    "P13": {"x": 93.9, "y": 49.4},
    "P14": {"x": 93.9, "y": 28.4},
}

GRAPH = {
    "P1": ["P2", "P3", "P4"],
    "P2": ["P1", "P5"],
    "P3": ["P1", "P6"],
    "P4": ["P1", "P5", "P6"],
    "P5": ["P2", "P4", "P7"],
    "P6": ["P3", "P4", "P8"],
    "P7": ["P5", "P10", "P12"],
    "P8": ["P6", "P9", "P11"],
    "P9": ["P8", "P14"],
    "P10": ["P7", "P13"],
    "P11": ["P8", "P12"],
    "P12": ["P7", "P11"],
    "P13": ["P10"],
    "P14": ["P9"],
}

START_POINTS = {
    "intrare-principala": {"label": "Intrare Principala", "coords": {"x": 2.8, "y": 49.5}, "point": "P1"},
    "intrare-teatru": {"label": "Intrare Teatru", "coords": {"x": 26.0, "y": 2.4}, "point": "P6"},
    "intrare-parcare": {"label": "Intrare Parcare", "coords": {"x": 22.0, "y": 96.0}, "point": "P2"},
}

ROOMS = [
    {"id": "207", "name": "207", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P3", "coords": {"x": 5.9, "y": 10.0}, "summary": "Sala din zona stanga sus a etajului."},
    {"id": "208", "name": "208", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P3", "coords": {"x": 13.4, "y": 10.0}, "summary": "Sala de pe coridorul superior, in partea stanga."},
    {"id": "209", "name": "209", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P3", "coords": {"x": 20.8, "y": 10.0}, "summary": "Sala de pe coridorul superior, inainte de zona centrala."},
    {"id": "210", "name": "210", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P6", "coords": {"x": 35.2, "y": 10.0}, "summary": "Sala de pe coridorul superior central."},
    {"id": "211", "name": "211", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P6", "coords": {"x": 43.8, "y": 10.0}, "summary": "Sala de pe coridorul superior, langa grupul sanitar."},
    {"id": "219", "name": "219", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P6", "coords": {"x": 47.0, "y": 18.0}, "summary": "Sala langa zona Decanat Stiinte."},
    {"id": "220b", "name": "220B", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P6", "coords": {"x": 53.9, "y": 10.0}, "summary": "Sala de pe coridorul superior, imediat dupa grupul sanitar."},
    {"id": "220", "name": "220", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P6", "coords": {"x": 57.2, "y": 10.0}, "summary": "Sala de pe coridorul superior central-dreapta."},
    {"id": "221", "name": "221", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P8", "coords": {"x": 60.6, "y": 10.0}, "summary": "Sala de pe coridorul superior, inainte de aripa dreapta."},
    {"id": "222", "name": "222", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P11", "coords": {"x": 65.7, "y": 16.8}, "summary": "Sala de pe coridorul vertical din dreapta sus."},
    {"id": "223", "name": "223", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P11", "coords": {"x": 65.7, "y": 24.9}, "summary": "Sala din zona verticala dreapta, sub 222."},
    {"id": "223a", "name": "223A", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P11", "coords": {"x": 65.7, "y": 31.0}, "summary": "Sala mica din coloana 223A."},
    {"id": "224", "name": "224", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P11", "coords": {"x": 65.7, "y": 38.2}, "summary": "Sala din dreptul nodului P11."},
    {"id": "228", "name": "228", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P11", "coords": {"x": 57.8, "y": 36.0}, "summary": "Sala centrala legata de zona scarilor interioare."},
    {"id": "230", "name": "230", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 71.9, "y": 43.6}, "summary": "Sala din retragerea coridorului spre dreapta."},
    {"id": "231", "name": "231", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 69.2, "y": 52.2}, "summary": "Sala de pe nodul central-dreapta."},
    {"id": "233a", "name": "233A", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 66.1, "y": 52.2}, "summary": "Sala mica langa 231, accesibila din acelasi nod."},
    {"id": "233b", "name": "233B", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 66.2, "y": 59.8}, "summary": "Sala de pe coloana verticala din zona centrala dreapta."},
    {"id": "234", "name": "234", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 66.2, "y": 67.6}, "summary": "Sala de sub 233B pe acelasi coridor."},
    {"id": "235", "name": "235", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 66.2, "y": 75.0}, "summary": "Sala de pe coridorul vertical din dreapta jos."},
    {"id": "236", "name": "236", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P7", "coords": {"x": 66.2, "y": 83.4}, "summary": "Sala din partea de jos a coloanei drepte."},
    {"id": "240", "name": "240", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P12", "coords": {"x": 58.4, "y": 52.4}, "summary": "Sala centrala accesibila din nodul P12."},
    {"id": "243", "name": "243", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P5", "coords": {"x": 44.8, "y": 72.7}, "summary": "Sala din zona Decanat Horticultura."},
    {"id": "251", "name": "251", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P5", "coords": {"x": 49.2, "y": 89.2}, "summary": "Sala de pe coridorul inferior central."},
    {"id": "252", "name": "252", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P5", "coords": {"x": 43.8, "y": 89.2}, "summary": "Sala de pe coridorul inferior, langa 251."},
    {"id": "253", "name": "253", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P5", "coords": {"x": 36.9, "y": 89.2}, "summary": "Sala de pe coridorul inferior central-stanga."},
    {"id": "254", "name": "254", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P5", "coords": {"x": 29.8, "y": 89.2}, "summary": "Sala de pe coridorul inferior stanga."},
    {"id": "255", "name": "255", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P2", "coords": {"x": 19.8, "y": 89.2}, "summary": "Sala de pe coridorul inferior, aripa stanga."},
    {"id": "256", "name": "256", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P2", "coords": {"x": 12.9, "y": 89.2}, "summary": "Sala de pe coridorul inferior, spre coltul stanga."},
    {"id": "257", "name": "257", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P2", "coords": {"x": 5.9, "y": 89.2}, "summary": "Sala din coltul stanga jos al etajului."},
    {"id": "258", "name": "258", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P2", "coords": {"x": 8.3, "y": 79.7}, "summary": "Sala de pe coloana stanga inferioara."},
    {"id": "261", "name": "261", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P1", "coords": {"x": 8.3, "y": 72.4}, "summary": "Sala de pe coloana stanga, aproape de zona centrala."},
    {"id": "262", "name": "262", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P1", "coords": {"x": 8.3, "y": 66.6}, "summary": "Sala de pe coloana stanga, intre 261 si 263."},
    {"id": "263", "name": "263", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P1", "coords": {"x": 8.3, "y": 60.7}, "summary": "Sala de pe coloana stanga, inainte de holul central."},
    {"id": "268", "name": "268", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P7", "coords": {"x": 72.0, "y": 89.2}, "summary": "Sala de pe coridorul inferior din aripa dreapta."},
    {"id": "269", "name": "269", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P10", "coords": {"x": 84.4, "y": 89.2}, "summary": "Sala de pe coridorul inferior aproape de coltul dreapta."},
    {"id": "270", "name": "270", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P10", "coords": {"x": 94.2, "y": 79.6}, "summary": "Sala de pe coloana dreapta inferioara."},
    {"id": "271", "name": "271", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P10", "coords": {"x": 94.2, "y": 67.5}, "summary": "Sala de pe coloana dreapta, sub scara 4."},
    {"id": "272", "name": "272", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P13", "coords": {"x": 94.2, "y": 56.0}, "summary": "Sala de pe coloana dreapta, langa scara 4."},
    {"id": "275", "name": "275", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P14", "coords": {"x": 94.2, "y": 23.0}, "summary": "Sala de pe coloana dreapta superioara."},
    {"id": "276", "name": "276", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P14", "coords": {"x": 94.2, "y": 15.0}, "summary": "Sala de pe coloana dreapta, aproape de coltul superior."},
    {"id": "277", "name": "277", "building_label": "Facultatea de Horticultura", "floor": "Etajul 1", "point": "P9", "coords": {"x": 88.9, "y": 10.0}, "summary": "Sala din coltul dreapta sus al etajului."},
]

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
FLOOR_PLAN_PATH = Path(__file__).with_name("etaj-site.png")

TEXT = {
    "ro": {
        "html_lang": "ro",
        "app_title": "UniWay Craiova",
        "eyebrow": "Navigare universitara",
        "hero_title": "Gaseste rapid sala pe etajul hartii tale.",
        "hero_stat_1": "harta reala",
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
        "map_title": "Traseu real pe etaj",
        "live_pill": "Python app",
        "route_tag": "Ghidare",
        "rooms_tag": "Sali populare",
        "rooms_title": "Destinatii rapide",
        "default_summary": "Introdu numele unei sali pentru a vedea traseul recomandat.",
        "default_title": "Alege o sala",
        "not_found_title": "Sala nu a fost gasita",
        "not_found_summary": "Incearca una dintre salile sugerate, de exemplu 207, 231 sau 277.",
        "from_prefix": "Pleci din {start}.",
        "to_prefix": "Mergi catre {building}.",
        "step_move": "Continua spre {point}.",
        "step_arrive": "Intra la sala {room}.",
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
        "hero_title": "Find your classroom on your real floor plan.",
        "hero_stat_1": "real map",
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
        "map_title": "Real route across the floor",
        "live_pill": "Python app",
        "route_tag": "Directions",
        "rooms_tag": "Popular rooms",
        "rooms_title": "Quick destinations",
        "default_summary": "Enter a room name to see the recommended route.",
        "default_title": "Choose a room",
        "not_found_title": "Room not found",
        "not_found_summary": "Try one of the suggested rooms, for example 207, 231 or 277.",
        "from_prefix": "You start from {start}.",
        "to_prefix": "Head towards {building}.",
        "step_move": "Continue towards {point}.",
        "step_arrive": "Enter room {room}.",
        "language_switch": "Change language",
        "landing_title": "Choose the language for the app.",
        "landing_title_secondary": "Alege limba in care vrei sa folosesti aplicatia.",
        "landing_text": "Select Romanian or English so the directions are easier to follow around the faculty.",
        "landing_ro": "Romanian",
        "landing_en": "English",
    },
}

START_POINT_LABELS = {
    "intrare-principala": {"ro": "Intrare Principala", "en": "Main Entrance"},
    "intrare-teatru": {"ro": "Intrare Teatru", "en": "Theatre Entrance"},
    "intrare-parcare": {"ro": "Intrare Parcare", "en": "Parking Entrance"},
}

BUILDING_LABELS = {
    "Facultatea de Horticultura": {"ro": "Facultatea de Horticultura", "en": "Faculty of Horticulture"},
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


def distance(point_a, point_b):
    delta_x = point_b["x"] - point_a["x"]
    delta_y = point_b["y"] - point_a["y"]
    return sqrt(delta_x * delta_x + delta_y * delta_y)


def clamp_coords(coords, padding=3.0):
    return {
        "x": min(max(coords["x"], padding), 100 - padding),
        "y": min(max(coords["y"], padding), 100 - padding),
    }


def build_route_segments(point_ids, final_coords=None):
    segments = []
    for index in range(len(point_ids) - 1):
        start_point = POINTS[point_ids[index]]
        end_point = POINTS[point_ids[index + 1]]
        segments.append(calculate_line(start_point, end_point))

    if point_ids and final_coords:
        segments.append(calculate_line(POINTS[point_ids[-1]], clamp_coords(final_coords)))

    return segments


def find_path(start_point_id, destination_point_id):
    if start_point_id == destination_point_id:
        return [start_point_id]

    frontier = [(0, start_point_id, [start_point_id])]
    best_cost = {start_point_id: 0}

    while frontier:
        frontier.sort(key=lambda item: item[0])
        cost, current, path = frontier.pop(0)
        if current == destination_point_id:
            return path

        for neighbor in GRAPH.get(current, []):
            new_cost = cost + distance(POINTS[current], POINTS[neighbor])
            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                frontier.append((new_cost, neighbor, path + [neighbor]))

    return []


def calculate_line(start, end):
    delta_x = end["x"] - start["x"]
    delta_y = end["y"] - start["y"]
    scaled_delta_y = delta_y * MAP_RATIO
    length = sqrt(delta_x * delta_x + scaled_delta_y * scaled_delta_y)
    inset = 0.45

    if length > inset * 2:
        unit_x = delta_x / length
        unit_y = scaled_delta_y / length
        start = {
            "x": start["x"] + unit_x * inset,
            "y": start["y"] + (unit_y * inset) / MAP_RATIO,
        }
        end = {
            "x": end["x"] - unit_x * inset,
            "y": end["y"] - (unit_y * inset) / MAP_RATIO,
        }
        delta_x = end["x"] - start["x"]
        delta_y = end["y"] - start["y"]
        scaled_delta_y = delta_y * MAP_RATIO
        length = sqrt(delta_x * delta_x + scaled_delta_y * scaled_delta_y)

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


def point_label(point_id, lang):
    return translate_start_label(point_id, lang)


def build_route_step_text(route_point_ids, room, lang):
    text = t(lang)
    if not route_point_ids:
        return [text["step_arrive"].format(room=room["name"])]

    steps = []
    for point_id in route_point_ids[1:]:
        steps.append(text["step_move"].format(point=point_label(point_id, lang)))

    steps.append(text["step_arrive"].format(room=room["name"]))
    return steps


def render_route_debug(route_point_ids):
    if not route_point_ids:
        return ""
    return " -> ".join(route_point_ids)


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
    route_debug = ""

    if room:
        building_label = translate_building_label(room["building_label"], lang)
        floor_label = translate_floor_label(room["floor"], lang)
        full_steps = [
            text["from_prefix"].format(start=start_label),
            text["to_prefix"].format(building=building_label),
        ]
        route_point_ids = find_path(start.get("point", selected_start), room["point"])
        full_steps.extend(build_route_step_text(route_point_ids, room, lang))
        title = room["name"]
        summary = f"{room['name']} - {building_label} - {floor_label}. {room['summary']}"
        steps = render_steps(full_steps)
        route_lines = render_route_lines(build_route_segments(route_point_ids, room["coords"]))
        route_debug = render_route_debug(route_point_ids)
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
          <div><strong>1</strong><span>{text["hero_stat_1"]}</span></div>
          <div><strong>{len(ROOMS)}</strong><span>{text["hero_stat_2"]}</span></div>
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
          <img class="floor-plan" src="/etaj-site.png" alt="Harta etajului 1 pentru site">
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
          <div class="route-debug">{escape(route_debug)}</div>
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

    if path == "/etaj-site.png":
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
