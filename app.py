from html import escape
from math import atan2, degrees, sqrt
import os
from pathlib import Path
import ast
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server

from data.restrooms import RESTROOMS
from data.rooms import ROOMS
from data.starts import START_POINTS

# Dimensiunile de bază folosite de harta implicită și de overlay-ul SVG.
MAP_WIDTH = 4572
MAP_HEIGHT = 4372
MAP_RATIO = MAP_HEIGHT / MAP_WIDTH
DEFAULT_FLOOR_ID = "etaj-1"
STAIR_TRAVEL_COST = 900.0


# Punctele de navigație pentru etajul implicit. Fiecare punct devine un nod în graf.
POINTS = {
    "P1": {"x": 2276.9, "y": 3745.6},
    "P2": {"x": 827.5, "y": 3745.6},
    "P3": {"x": 3735.3, "y": 3745.6},
    "P1-3":{"x": 2900,"y": 3745.6},
    "P4": {"x": 2276.9, "y": 2392.1},
    "P5": {"x": 3735.3, "y": 3047.3},
    "P6": {"x": 3735.3, "y": 2392.1},
    "P7": {"x": 827.5, "y": 3064.3},
    "P8": {"x": 827.5, "y": 2392.1},
    "P9": {"x": 1508.8, "y": 2392.1},
    "P10": {"x": 3072.4, "y": 2392.1},
    "P11": {"x": 3735.3, "y": 1620},
    "P12": {"x": 2614.5, "y": 1620},
    "P13": {"x": 2279.3, "y": 1620},
    "P14": {"x": 1979.7, "y": 1620},
    "P15": {"x": 827.5, "y": 1620},
    "P16": {"x": 827.5, "y": 513.0},
    "P17": {"x": 2279.3, "y": 599.0},
    "P18": {"x": 1728.4, "y": 513.0},
    "P19": {"x": 2933.5, "y": 540.0},
    "P20": {"x": 3735.3, "y": 540.0},
    "P21": {"x": 701.0, "y": 3064.3},
    "P22": {"x": 3950.2, "y": 3047.3},
    "P23": {"x": 2279.3 , "y": 949},
    "P27" : {"x": 827.5, "y" : 3400},
    "P6-11": {"x":3735.3, "y" :2000},
    "P14-15": {"x": 1300, "y": 1620},
    "P1-2" : {"x" : 1200, "y" :3745.6}
}
# Muchiile de navigație pentru etajul implicit. Aceste legături descriu coridoarele reale.
GRAPH = {
    "P1": ["P2", "P3", "P4","P1-3", "P1-2"],
    "P2": ["P1", "P7","P27","P1-2"],
    "P3": ["P1", "P5","P1-3"],
    "P4": ["P1", "P9", "P10"],
    "P5": ["P3", "P6", "P22"],
    "P6": ["P5", "P10", "P11","P6-11"],
    "P7": ["P2", "P8", "P21","P27"],
    "P8": ["P7", "P9", "P15"],
    "P9": ["P8", "P4"],
    "P10": ["P4", "P6"],
    "P11": ["P6", "P12", "P20","P6-11"],
    "P12": ["P11", "P13"],
    "P13": ["P12", "P14", "P17","P23"],
    "P14": ["P13", "P15","P14-15"],
    "P15": ["P14", "P8", "P16","P14-15"],
    "P16": ["P15", "P18"],
    "P17": ["P13","P23"],
    "P18": ["P16"],
    "P19": ["P20"],
    "P20": ["P19", "P11"],
    "P21": ["P7"],
    "P22": ["P5"],
    "P23" : ["P13", "P17"],
    "P1-3": ["P1","P3"],
    "P6-11": ["P11","P6"],
    "P27" : ["P2","P7"],
    "P14-15":["P14","P15"],
    "P1-2": ["P1", "P2"]

}

# Punctele și muchiile pentru etajele suplimentare. Numele nodurilor trebuie să rămână
# compatibile cu sălile, scările și punctele compuse folosite în rutare.
POINTS_ETAJ_2 = {
    "P1": {"x": 1018, "y": 3684},
    "P2": {"x": 739, "y": 3684},
    "P3": {"x": 739, "y": 3305},
    "P4": {"x": 739, "y": 2592},
    "P5": {"x": 1047, "y": 2592},
    "P6": {"x": 1233, "y": 2592},
    "P7": {"x": 739, "y": 1749},
    "P8": {"x": 1847, "y": 1749},
    "P9": {"x": 2451, "y": 1749},
    "P10": {"x": 3539, "y": 1749},
    "P11": {"x": 2451, "y": 647},
    "P12": {"x": 2747, "y": 725},
    "P13": {"x": 3447, "y": 725},
    "P14": {"x": 3560.0, "y": 725},
    "P15": {"x": 1590, "y": 670},
    "P16": {"x": 903, "y": 670},
    "P17": {"x": 3535, "y": 2592},
    "P18": {"x": 3535, "y": 3312},
    "P19": {"x": 3535, "y": 3708},
    "P89" :{"x":2107 , "y":1749},
    "P12-13": {"x":3090, "y": 711},
    "P78" :{"x" : 1000,"y": 1749}
  
   
}
GRAPH_ETAJ_2 = {
    "P1": ["P2"],
    "P2": ["P1", "P3"],
    "P3": ["P2", "P4"],
    "P4": ["P3", "P5", "P7"],
    "P5": ["P4", "P6"],
    "P6": ["P5"],
    "P7": ["P4", "P8","P78"],
    "P8": ["P7", "P9","P89","P78"],
    "P9": ["P8", "P10", "P11","P89"],
    "P10": ["P9"],
    "P11": ["P9"],
    "P12": ["P13","P12-13"],
    "P13": ["P12", "P14","P12-13"],
    "P14": ["P13"],
    "P15": ["P16"],
    "P16": ["P15"],
    "P17": ["P18"],
    "P18": ["P17", "P19"],
    "P19": ["P18"],
    "P89": ["P8","P9"],
    "P12-13":["P12","P13"],
    "P78" : ["P7","P8"]
    
}
GRAPH_ETAJ_SUBSOL = {
    
    "P1": ["P2","P4"],
    "P2": ["P1","P3"],
    "P3": ["P2"],
    "P4": ["P1","P5"],
    "P5": ["P4","P6","P7"],
    "P6" :["P5","P8"],
    "P7": ["P5"],
    "P8":["P6"],
    "P9":["P10"],
    "P10": ["P9","P11"],
    "P11": ["P10"],
    "P12" :["P13"],
    "P13":["P12"],
    "P67" : ["P420"],
    "P420" : ["P67","P69"],
    "P69": ["P420"]

}

POINTS_ETAJ_SUBSOL = {
    "P1" : {"x": 1690, "y":1730},
    "P2": {"x": 571,"y": 1730},
    "P3": {"x": 571, "y" :2170},
    "P4" :{"x" :1690, "y":1570},
    "P5": {"x":1979, "y": 1570},
    "P6": {"x": 2000,"y" :1570},
    "P7": {"x":1979,"y": 1797 },
    "P8" :{"x":2000,"y":1131},
    "P9": {"x": 2651, "y":661},
    "P10":{"x":3445 ,"y": 661},
    "P11": {"x" :3445, "y": 1083},
    "P12": {"x": 2327, "y": 1663},
    "P13": {"x": 2491, "y": 1663},
    "P67" :{"x" : 1290 , "y": 3870},
    "P420" : {"x" : 1560, "y" : 3870},
    "P69" : {"x": 1560 , "y" : 3870}
}


GRAPH_ETAJ_0 = {
    "P1": ["P2","P9","P1-9"],
    "P2": ["P1", "P3","P2-3"],
    "P3": ["P2","P2-3"],
    "P4": [ "P5"],
    "P5": ["P4", "P6"],
    "P6": ["P5","P7","P6-7"],
    "P7": ["P6", "P8","P10","P6-7","P7-10"],
    "P8": ["P7", "P9"],
    "P9": ["P8","P1","P1-9"],
    "P10": ["P7","P11","P7-10","P10-11"],
    "P11": ["P12","P10","P10-11"],
    "P12": ["P11","P13","P15"],
    "P13": ["P12", "P14"],
    "P14": ["P13"],
    "P15": ["P12"],
    "P16": ["P17","P16-17"],
    "P17": ["P16","P16-17"],
    "P18": [ "P19","P18-19"],
    "P19": ["P18","P20","P18-19"],
    "P20": ["P19"],
    "P1-9":["P1","P9"],
    "P6-7":["P6", "P7"],
    "P7-10": ["P7","P10"],
    "P10-11":["P10","P11"],
    "P16-17":["P16","P17"],
    "P18-19":["P18","P19"],
    "P2-3":["P2", "P3"]
    
}

POINTS_ETAJ_0 = {
    "P1": {"x": 1220, "y": 3304},
    "P2": {"x": 1220, "y": 3784},
    "P3": {"x": 2147, "y": 3784},
    "P4": {"x": 3190, "y": 3780},
    "P5": {"x": 4011, "y": 3780},
    "P6": {"x": 4011, "y": 3302},
    "P7": {"x": 4011, "y": 2500},
    "P8": {"x": 2607, "y": 2500},
    "P9": {"x": 1220, "y": 2500},
    "P10": {"x": 4011, "y": 1808},
    "P11": {"x": 2933, "y": 1808},
    "P12": {"x": 2617, "y": 1808},
    "P13": {"x": 2317, "y": 1808},
    "P14": {"x": 1363, "y": 1808},
    "P15": {"x": 2617, "y": 1060},
    "P16": {"x": 3230, "y": 774},
    "P17": {"x": 3900, "y": 774},
    "P18": {"x": 2020, "y": 752},
    "P19": {"x": 1242, "y": 752},
    "P20" :{"x":1242, "y": 1234 },
    "P1-9": {"x": 1220, "y": 2700},
    "P6-7":{ "x": 4011, "y": 2900},
    "P7-10": {"x":4011 , "y":2000},
    "P10-11":{"x": 4350, "y": 1808},
    "P16-17": {"x":3640,"y" :774},
    "P18-19":{"x":1560 ,"y": 752},
    "P2-3":{ "x" :1880, "y": 3784}
}

GRAPH_ETAJ_3 = {
    "P1": ["P2","P1-11","P11"],
    "P2": ["P1", "P3"],
    "P3": ["P2"],
    "P4": [ "P5"],
    "P5": ["P4", "P6"],
    "P6": ["P5","P7","P6-7"],
    "P7": ["P6","P9","P6-7"],
    "P8": ["P10", "P9"],
    "P9": ["P8","P9-15","P15"],
    "P10": ["P8","P11","P10-13"],
    "P11": ["P11-12","P10","P1-11"],
    "P12": ["P11-12","P13"],
    "P13": ["P12", "P14"],
    "P14": ["P13","P15"],
    "P15": ["P14","P16"],
    "P16": ["P15"],
    "P17": ["P18","P17-18"],
    "P18": [ "P17","P17-18"],
    "P19": ["P20"],
    "P20": ["P19"],
    "P1-11": ["P1","P11"],
    "P6-7": ["P6","P7"],
    "P10-13":["P10","P13"],
    "P9-15":["P9","P15"],
    "P11-12":["P11","P12"],
    "P82" : ["P8"],
    "P17-18": ["P17","P18"]
    
}

POINTS_ETAJ_3 = {
    "P1": {"x": 625, "y": 3310},
    "P2": {"x": 625, "y": 3835},
    "P3": {"x": 1757, "y": 3835},
    "P4": {"x": 2360, "y": 3810},
    "P5": {"x": 3500, "y": 3810},
    "P6": {"x": 3500, "y": 3290},
    "P7": {"x": 3500, "y": 2450},
    "P8": {"x": 2100, "y": 2450},
    "P9": {"x": 2399, "y": 2450},
    "P10": {"x": 1751, "y": 2450},
    "P11": {"x": 625, "y": 2450},
    "P12": {"x": 625, "y": 1729},
    "P13": {"x": 1751, "y": 1729},
    "P14": {"x": 2047, "y": 1729},
    "P15": {"x": 2399, "y": 1729},
    "P16": {"x": 3309, "y": 1729},
    "P17": {"x": 2620, "y": 641},
    "P18": {"x": 3450, "y": 641},
    "P19": {"x": 1460, "y": 640},
    "P20" :{"x":747, "y": 640 },
    "P1-11": {"x": 625, "y" : 2700},
    "P6-7":{"x":3500,"y":2600},
    "P10-13":{"x":1751, "y": 2000},
    "P9-15": {"x":2399, "y": 2000},
    "P11-12":{"x":625,"y":2000},
    "P82": {"x": 1000, "y": 2450},
    "P17-18":{"x" :3000 , "y" :641}
}


GRAPH_ETAJ_4 = {
    "P1" : ["P2","P1-2"],
    "P2": ["P1","P3","P1-2"],
    "P3" :["P2"],
    "P4": ["P5","P4-5"],
    "P5" :["P4","P4-5"],
    "P1-2": ["P1","P2"],
    "P4-5": ["P4","P5"]
}


POINTS_ETAJ_4 = {
    "P1": {"x": 1560, "y": 600},
    "P2": {"x": 689, "y": 600},
    "P3": {"x": 689, "y": 1087},
    "P4": {"x": 2720, "y": 613},
    "P5": {"x": 3400, "y": 613},
    "P1-2":{"x": 1015,"y": 600},
    "P4-5":{"x":3160, "y":613}
    
}

def normalize_point_value(point_id):
    # Normalizează aliasurile și diferențele minore de scriere din datele introduse manual.
    if point_id is None:
        return None
    value = str(point_id).strip()
    if not value:
        return None

    aliases = {
        "p1": "P1",
        "p2": "P2",
        "p3": "P3",
        "p4": "P4",
        "p5": "P5",
        "p6": "P6",
        "p7": "P7",
        "p8": "P8",
        "p9": "P9",
        "p10": "P10",
        "p11": "P11",
        "p12": "P12",
        "p13": "P13",
        "p14": "P14",
        "p15": "P15",
        "p16": "P16",
        "p17": "P17",
        "p18": "P18",
        "p19": "P19",
        "p20": "P20",
        "p21": "P21",
        "p22": "P22",
        "p23": "P23",
        "p27": "P27",
        "P1213": "P12-13",
        "P12-P13": "P12-13",
    }
    return aliases.get(value, value)


def normalize_point_list(raw_points):
    # Transformă orice formă de intrare într-o listă de ids curate.
    if raw_points is None:
        return []
    if isinstance(raw_points, (list, tuple, set)):
        return [
            normalized
            for normalized in (normalize_point_value(point_id) for point_id in raw_points)
            if normalized
        ]

    normalized = normalize_point_value(raw_points)
    return [normalized] if normalized else []


def deduplicate_rooms(rooms):
    # Păstrează ultima definiție a unei săli pe etaj, dar nu pierde lista de scări deja completată.
    merged = {}
    ordered_keys = []

    for room in rooms:
        floor_id = room.get("floor_id", DEFAULT_FLOOR_ID)
        key = (room["id"].lower(), floor_id)
        if key not in merged:
            merged[key] = dict(room)
            ordered_keys.append(key)
            continue

        merged[key] = dict(room)

    return [merged[key] for key in ordered_keys]


ROOMS = deduplicate_rooms(ROOMS)


# Lista folosită efectiv de aplicație după normalizarea punctelor și a metadatelor.
NORMALIZED_ROOMS = []
for room in ROOMS:
    floor_id = room.get("floor_id", DEFAULT_FLOOR_ID)
    raw_points = room.get("points", room.get("point"))
    cleaned_room = {
        "id": room["id"],
        "name": room["name"],
        "floor": room["floor"],
        "floor_id": floor_id,
        "points": normalize_point_list(raw_points),
        "coords": room["coords"],
    }
    NORMALIZED_ROOMS.append(cleaned_room)

# Configurația pe etaje: imagine, dimensiuni, puncte, graf și scări disponibile.
ETAJE = {
    DEFAULT_FLOOR_ID: {
        "id": DEFAULT_FLOOR_ID,
        "level": 1,
        "label_ro": "Etajul 1",
        "label_en": "1st floor",
        "image_path": Path(__file__).with_name("etaj-0-bun.webp"),
        "image_url": "/etaj-0-bun.webp",
        "width": MAP_WIDTH,
        "height": MAP_HEIGHT,
        "points": POINTS,
        "graph": GRAPH,
        "stairs": {
            "S1": {"points": ["P21"], "coords": {"x": 701.0, "y": 3241.0}},
            "S2": {"points": ["P22"], "coords": {"x": 3954.0, "y": 3130.0}},
            "S3": {"points": ["P4"], "coords": {"x": 2297.0, "y": 2240.0}},
           
            "S5": {"points": ["P19"], "coords": {"x": 2893.0, "y": 430.0}},
            "S6": {"points": ["P18"], "coords": {"x": 1650.0, "y": 430.0}},
            "S7": {"points": ["P14"], "coords": {"x": 1950.0, "y": 1700.0}},
            "S8": {"points": ["P12"], "coords": {"x": 2600.0, "y": 1700.0}},
        },
    },
    
    "etaj-2": {
        "id": "etaj-2",
        "level": 2,
        "label_ro": "Etajul 2",
        "label_en": "2nd floor",
        "image_path": Path(__file__).with_name("etaj-2-clean.webp"),
        "image_url": "/etaj-2-clean.webp",
        "width": 4409,
        "height": 4416,
        "points": POINTS_ETAJ_2,
        "graph": GRAPH_ETAJ_2,
        "stairs": {
            "S1": {"points": ["P3"], "coords": {"x": 585.0, "y": 3301.0}},
            "S2": {"points": ["P18"], "coords": {"x": 3664.0, "y": 3320.0}},
            
            "S5": {"points": ["P12"], "coords": {"x": 2793.0, "y": 616.0}},
            "S6": {"points": ["P15"], "coords": {"x": 1650.0, "y": 430.0}},
            "S7": {"points": ["P8"], "coords": {"x": 1830.0, "y": 1870.0}},
            "S8": {"points": ["P9"], "coords": {"x": 2460.0, "y": 1860.0}},
        },
    },
    "etaj-0": {
        "id": "etaj-0",
        "level": 0,
        "label_ro": "Etajul 0",
        "label_en": "Ground floor",
        "image_path": Path(__file__).with_name("etaj 0- original.webp"),
        "image_url": "/etaj 0- original.webp",
        "image_version": "20260517",
        "width": 4754,
        "height": 4480,
        "points": POINTS_ETAJ_0,
        "graph": GRAPH_ETAJ_0,
        "stairs": {
            "S1": {"points": ["P1"], "coords": {"x": 1075.0, "y": 3301.0}},
            "S2": {"points": ["P6"], "coords": {"x": 4134.0, "y": 3320.0}},
            
            "S5": {"points": ["P16"], "coords": {"x": 3223.0, "y": 710.0}},
            "S6": {"points": ["P18"], "coords": {"x": 2020.0, "y": 668.0}},
            "S7": {"points": ["P13"], "coords": {"x": 2300.0, "y": 1920.0}},
            "S8": {"points": ["P11"], "coords": {"x": 2920.0, "y": 1920.0}},
            "S9" : {"points" : ["P2-3"], "coords" : { "x" :1880, "y": 3630}},
        },
    },
    "etaj-3": {
        "id": "etaj-3",
        "level": 3,
        "label_ro": "Etajul 3",
        "label_en": "Third floor",
        "image_path": Path(__file__).with_name("etaj 3 bun.webp"),
        "image_url": "/etaj 3 bun.webp",
        "width": 4306,
        "height": 4412,
        "points": POINTS_ETAJ_3,
        "graph": GRAPH_ETAJ_3,
        "stairs": {
            "S1": {"points": ["P1"], "coords": {"x": 463, "y": 3321}},
            "S2": {"points": ["P6"], "coords": {"x": 3690.0, "y": 3330.0}},
            "S3": {"points" : ["P8"], "coords" : {"x" :2060, "y":1920}},
          
            "S5": {"points": ["P17"], "coords": {"x": 2630.0, "y": 573.0}},
            "S6": {"points": ["P19"], "coords": {"x": 1450.0, "y": 583.0}},
            "S7": {"points": ["P13"], "coords": {"x": 1750.0, "y": 1870.0}},
            "S8": {"points": ["P15"], "coords": {"x": 2370.0, "y": 1880.0}},
        },
    },
    "etaj-4": {
        "id": "etaj-4",
        "level": 4,
        "label_ro": "Etajul 4",
        "label_en": "Fourth floor",
        "image_path": Path(__file__).with_name("etaj final.webp"),
        "image_url": "/etaj final.webp",
        "width": 4409,
        "height": 4304,
        "points": POINTS_ETAJ_4,
        "graph": GRAPH_ETAJ_4,
        "stairs": {
            "S5": {"points": ["P4"], "coords": {"x": 2710.0, "y": 559.0}},
            "S6": {"points": ["P1"], "coords": {"x": 1560.0, "y": 523.0}},
            
        },
        
    },
    "subsol": {
        "id": "subsol",
        "level": -1,
        "label_ro": "Subsol",
        "label_en": "Basement",
        "image_path": Path(__file__).with_name("etaj -1.webp"),
        "image_url": "/etaj -1.webp",
        "width": 4205,
        "height": 4396,
        "points": POINTS_ETAJ_SUBSOL,
        "graph": GRAPH_ETAJ_SUBSOL,
        "stairs": {
            "S5": {"points": ["P9"], "coords": {"x": 2600.0, "y": 519.0}},
            "S7": {"points": ["P1"], "coords": {"x": 1690.0, "y": 1790.0}},
            "S8": {"points": ["P12"], "coords": {"x": 2320.0, "y": 1790.0}},
            "S9" :{"points" : ["P67"],"coords" : {"x" : 1270, "y" :3740 }}
        },
        
    }
    
}

FLOOR_CONFIGS = ETAJE


def build_stair_shafts(etaje):
    # Grupează aceeași scară de pe mai multe etaje într-o structură comună pentru legăturile verticale.
    shafts = {}
    for floor_id, floor_config in etaje.items():
        for stair_id, stair_info in floor_config.get("stairs", {}).items():
            points = [
                point_id
                for point_id in stair_info.get("points", [])
                if point_id in floor_config["points"]
            ]
            if points:
                shafts.setdefault(stair_id, {})[floor_id] = points
    return shafts


STAIR_SHAFTS = build_stair_shafts(ETAJE)

# Excepții locale pentru săli care au mai multe puncte candidate, dar trebuie forțat unul anume.
ROOM_POINT_OVERRIDES = {

}


def choose_primary_room_point(room, candidate_points):
    # Dacă o sală atinge mai multe noduri, alege punctul cel mai apropiat de coordonata ei vizuală.
    floor_id = room.get("floor_id", DEFAULT_FLOOR_ID)
    floor_points = FLOOR_CONFIGS.get(floor_id, FLOOR_CONFIGS[DEFAULT_FLOOR_ID])["points"]
    valid_points = [point_id for point_id in candidate_points if point_id in floor_points]
    if not valid_points:
        return None
    if len(valid_points) == 1:
        return valid_points[0]
    return min(
        valid_points,
        key=lambda point_id: sqrt(
            (floor_points[point_id]["x"] - room["coords"]["x"]) ** 2
            + (floor_points[point_id]["y"] - room["coords"]["y"]) ** 2
        ),
    )


for room in NORMALIZED_ROOMS:
    override_points = ROOM_POINT_OVERRIDES.get(room["id"].lower())
    candidate_points = override_points if override_points else room.get("points", [])
    primary_point = choose_primary_room_point(room, candidate_points)
    room["point"] = primary_point
    room["points"] = [primary_point] if primary_point else []

STYLES_PATH = Path(__file__).with_name("styles.css")
FLOOR_PLAN_PATH = Path(__file__).with_name("etaj-0-bun.png")
CREATOR_NAME = "Gaman Mihnea Radu"
COORDINATING_TEACHERS = [
    "Smaranda Belciug",
    "Florin Ispas",
]
REPORT_ISSUE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeJdTD1_xouC4_0FIWj9AR9RAaTYN1Vehtrb1hBIN71FotYag/viewform?usp=publish-editor"

# Textele UI sunt ținute separat pentru a simplifica schimbările de limbă și etichete.
TEXT = {
    "ro": {
        "html_lang": "ro",
        "app_title": "UniWay Craiova",
        "eyebrow": "Navigare universitara",
        "hero_title": "Gaseste-ti rapid sala",
        "hero_stat_1": "harta reala",
        "hero_stat_2": "sali incluse",
        "hero_stat_3": "server-side",
        "creator_label": "Creator",
        "coordinators_label": "Profesori coordonatori",
        "planner_label": "Planificator traseu",
        "planner_title": "Unde vrei sa ajungi?",
        "start_label": "Punct de plecare",
        "target_label": "Destinatie",
        "submit": "Arata traseul",
        "restroom_female": "Baie fete",
        "restroom_male": "Baie baieti",
        "quick_rooms": "Sugestii sali",
        "map_tag": "Harta campus",
        "map_title": "Traseu real pe etaj",
        "legend_title": "Legenda",
        "legend_route": "Linia portocalie arata traseul pe etajul curent.",
        "legend_start": "Markerul rosu arata punctul de plecare.",
        "legend_floor": "Butonul din dreapta sus te muta la urmatorul etaj din traseu.",
        "report_issue": "Raporteaza o problema",
        "report_issue_text": "Daca observi o eroare in traseu sau in datele salilor, trimite un mesaj aici.",
        "report_issue_cta": "Deschide formularul",
        "next_floor": "Urca un etaj",
        "default_title": "Alege o sala",
        "not_found_title": "Sala nu a fost gasita",
        "from_prefix": "Pleci din {start}.",
        "to_room_prefix": "Mergi spre sala {target}.",
        "to_entrance_prefix": "Mergi catre {target}.",
        "step_move": "Continua spre {point}.",
        "step_arrive": "Intra la sala {room}.",
        "step_arrive_target": "Ajungi la {target}.",
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
        "hero_stat_2": "Rooms included",
        "hero_stat_3": "server-side",
        "creator_label": "Creator",
        "coordinators_label": "Coordinating teachers",
        "planner_label": "Route planner",
        "planner_title": "Where do you want to go?",
        "start_label": "Starting point",
        "target_label": "Destination",
        "submit": "Show route",
        "restroom_female": "Women's restroom",
        "restroom_male": "Men's restroom",
        "quick_rooms": "Suggested NORMALIZED_ROOMS",
        "map_tag": "Campus map",
        "map_title": "Real route across the floor",
        "legend_title": "Legend",
        "legend_route": "The orange line shows the route on the current floor.",
        "legend_start": "The red marker shows the starting point.",
        "legend_floor": "The top-right button moves you to the next floor in the route.",
        "report_issue": "Report an issue",
        "report_issue_text": "If you notice a route or room data error, send a message here.",
        "report_issue_cta": "Open form",
        "next_floor": "Go up one floor",
        "default_title": "Choose a room",
        "not_found_title": "Room not found",
        "from_prefix": "You start from {start}.",
        "to_room_prefix": "Head towards room {target}.",
        "to_entrance_prefix": "Head towards {target}.",
        "step_move": "Continue towards {point}.",
        "step_arrive": "Enter room {room}.",
        "step_arrive_target": "You arrive at {target}.",
        "language_switch": "Change language",
        "landing_title": "Choose the language for the app.",
        "landing_title_secondary": "Alege limba in care vrei sa folosesti aplicatia.",
        "landing_text": "Select Romanian or English so the directions are easier to follow around the faculty.",
        "landing_ro": "Romanian",
        "landing_en": "English",
    },
}

# Etichete suplimentare pentru elemente afișate în interfață.
START_POINT_LABELS = {
    "intrare-principala": {"ro": "Intrare Principala", "en": "Main Entrance"},
    "intrare-teatru": {"ro": "Intrare Teatru", "en": "Theatre Entrance"},
    "intrare-parcare": {"ro": "Intrare Parcare", "en": "Parking Entrance"},
}

FLOOR_LABELS = {
    "Parter": {"ro": "Parter", "en": "Ground floor"},
    "Etajul 0": {"ro": "Etajul 0", "en": "Ground floor"},
    "Etajul 1": {"ro": "Etajul 1", "en": "1st floor"},
    "Etajul 2": {"ro": "Etajul 2", "en": "2nd floor"},
}


def get_room(query: str):
    # Caută o sală după id sau nume, ignorând diferențele de litere mari/mici.
    normalized = (query or "").strip().lower()
    for room in NORMALIZED_ROOMS:
        if room["name"].lower() == normalized or room["id"].lower() == normalized:
            return room
    return None


def get_start_point_option(key, lang):
    if key not in START_POINTS:
        return None
    config = START_POINTS[key]
    return {
        "id": key,
        "type": "entrance",
        "label": translate_start_label(key, lang),
        "name": translate_start_label(key, lang),
        "floor_id": config.get("floor_id", DEFAULT_FLOOR_ID),
        "points": [config["point"]],
        "coords": config["coords"],
        "point": config["point"],
    }


def restroom_target_points(restroom):
    # Băile sunt tratate similar cu sălile: destinația este unul sau mai multe puncte din graf.
    floor_points = get_floor_points(restroom["floor_id"])
    return [point_id for point_id in normalize_point_list(restroom.get("point")) if point_id in floor_points]


def restroom_matches(restroom, requested_type):
    if requested_type == "female":
        return restroom["type"] in {"female", "unisex"}
    if requested_type == "male":
        return restroom["type"] in {"male", "unisex"}
    return restroom["type"] == requested_type


def route_cost(route_node_ids):
    # Costul traseului este suma distanțelor din graful combinat, inclusiv penalizarea pentru scări.
    if len(route_node_ids) < 2:
        return 0.0
    combined_points, _ = build_combined_graph()
    total = 0.0
    for index in range(len(route_node_ids) - 1):
        total += node_distance(route_node_ids[index], route_node_ids[index + 1], combined_points)
    return total


def find_best_restroom(start_option, restroom_type, lang):
    # Selectează cea mai apropiată baie compatibilă cu tipul cerut, pornind din punctul ales.
    best_option = None
    best_route = None
    best_cost = None

    for index, restroom in enumerate(RESTROOMS):
        if not restroom_matches(restroom, restroom_type):
            continue
        points = restroom_target_points(restroom)
        if not points:
            continue

        route_node_ids, _ = find_best_target_path(
            start_option["points"],
            points,
            start_option.get("floor_id", DEFAULT_FLOOR_ID),
            restroom["floor_id"],
        )
        if not route_node_ids:
            continue

        cost = route_cost(route_node_ids)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_route = route_node_ids
            best_option = {
                "id": f'{restroom["id"]}-{index}',
                "type": "restroom",
                "label": restroom["label"],
                "name": restroom["label"],
                "floor": restroom["floor"],
                "floor_id": restroom["floor_id"],
                "points": points,
                "coords": restroom["coords"],
                "restroom": restroom,
                "route": best_route,
            }

    return best_option


def resolve_target_option(selected_target, lang, start_option=None):
    # Transformă selecția din UI într-o destinație concretă: sală, intrare sau baie.
    selected_target = (selected_target or "").strip()
    if not selected_target:
        return None

    if selected_target.startswith("restroom:") and start_option:
        restroom_type = selected_target.split(":", 1)[1]
        return find_best_restroom(start_option, restroom_type, lang)

    room = get_room(selected_target)
    if room:
        return {
            "id": room["id"],
            "type": "room",
            "label": room["name"],
            "name": room["name"],
            "floor": room["floor"],
            "floor_id": room_floor_id(room),
            "points": room_target_points(room),
            "coords": room["coords"],
            "room": room,
        }

    if selected_target.startswith("room:"):
        room = get_room(selected_target[5:])
        if room:
            return {
                "id": room["id"],
                "type": "room",
                "label": room["name"],
                "name": room["name"],
                "floor": room["floor"],
                "floor_id": room_floor_id(room),
                "points": room_target_points(room),
                "coords": room["coords"],
                "room": room,
            }

    return get_start_point_option(selected_target, lang)


def get_floor_config(floor_id=None):
    return FLOOR_CONFIGS.get(floor_id or DEFAULT_FLOOR_ID, FLOOR_CONFIGS[DEFAULT_FLOOR_ID])


def get_floor_level(floor_id=None):
    return get_floor_config(floor_id).get("level", 0)


def get_floor_points(floor_id=None):
    return get_floor_config(floor_id)["points"]


def get_floor_graph(floor_id=None):
    return get_floor_config(floor_id)["graph"]


def get_floor_width(floor_id=None):
    return get_floor_config(floor_id)["width"]


def get_floor_height(floor_id=None):
    return get_floor_config(floor_id)["height"]


def get_floor_stairs(floor_id=None):
    return get_floor_config(floor_id).get("stairs", {})


def get_stair_coords(stair_id, floor_id):
    stair_info = get_floor_stairs(floor_id).get(stair_id, {})
    return stair_info.get("coords")


def room_floor_id(room):
    return room.get("floor_id", DEFAULT_FLOOR_ID)


def node_key(floor_id, point_id):
    return f"{floor_id}:{point_id}"


def split_node_key(node_id):
    floor_id, point_id = node_id.split(":", 1)
    return floor_id, point_id


def build_combined_graph():
    # Combină toate etajele într-un singur graf și adaugă muchii verticale între etaje adiacente.
    combined_points = {}
    combined_graph = {}

    for floor_id, floor_config in FLOOR_CONFIGS.items():
        for point_id, coords in floor_config["points"].items():
            current_key = node_key(floor_id, point_id)
            combined_points[current_key] = coords
            combined_graph.setdefault(current_key, [])

        for point_id, neighbors in floor_config["graph"].items():
            current_key = node_key(floor_id, point_id)
            combined_graph.setdefault(current_key, [])
            for neighbor in neighbors:
                neighbor_key = node_key(floor_id, neighbor)
                combined_graph[current_key].append(neighbor_key)

    for floor_map in STAIR_SHAFTS.values():
        floor_entries = [
            (floor_id, [node_key(floor_id, point_id) for point_id in point_ids if point_id in get_floor_points(floor_id)])
            for floor_id, point_ids in floor_map.items()
        ]
        floor_entries = [(floor_id, nodes) for floor_id, nodes in floor_entries if nodes]
        floor_entries.sort(key=lambda item: get_floor_level(item[0]))

        for index in range(len(floor_entries) - 1):
            _, source_nodes = floor_entries[index]
            _, destination_nodes = floor_entries[index + 1]
            for source_node in source_nodes:
                combined_graph.setdefault(source_node, [])
                for destination_node in destination_nodes:
                    combined_graph.setdefault(destination_node, [])
                    if destination_node not in combined_graph[source_node]:
                        combined_graph[source_node].append(destination_node)
                    if source_node not in combined_graph[destination_node]:
                        combined_graph[destination_node].append(source_node)

    return combined_points, combined_graph

FLOOR_CHANGE_PENALTY = 1200.0
def node_distance(node_a, node_b, combined_points):
    floor_a, _ = split_node_key(node_a)
    floor_b, _ = split_node_key(node_b)

    if floor_a != floor_b:
        level_a = get_floor_level(floor_a)
        level_b = get_floor_level(floor_b)
        level_difference = abs(level_b - level_a)
        return FLOOR_CHANGE_PENALTY + STAIR_TRAVEL_COST * level_difference

    return distance(combined_points[node_a], combined_points[node_b])


def find_transition_stair(node_a, node_b):
    # Detectează dacă două noduri de pe etaje diferite aparțin aceleiași scări.
    floor_a, point_a = split_node_key(node_a)
    floor_b, point_b = split_node_key(node_b)
    if floor_a == floor_b:
        return None

    for stair_id, floors in STAIR_SHAFTS.items():
        floor_a_points = floors.get(floor_a, [])
        floor_b_points = floors.get(floor_b, [])
        if point_a in floor_a_points and point_b in floor_b_points:
            return stair_id
    return None


def distance(point_a, point_b):
    delta_x = point_b["x"] - point_a["x"]
    delta_y = point_b["y"] - point_a["y"]
    return sqrt(delta_x * delta_x + delta_y * delta_y)


def room_target_points(room):
    floor_points = get_floor_points(room_floor_id(room))
    points = room.get("points", [])
    return [point_id for point_id in points if point_id in floor_points]


def resolve_start_option(selected_start, lang):
    # Punctul de plecare poate fi fie o intrare, fie o sală folosită ca start.
    start = START_POINTS.get(selected_start)
    if start:
        return {
            "kind": "start-point",
            "id": selected_start,
            "label": translate_start_label(selected_start, lang),
            "floor_id": start.get("floor_id", DEFAULT_FLOOR_ID),
            "points": [start["point"]] if start.get("point") in get_floor_points(start.get("floor_id")) else [],
            "coords": start.get("coords"),
        }

    if selected_start.startswith("room:"):
        room_id = selected_start.split(":", 1)[1].lower()
        room = next((item for item in NORMALIZED_ROOMS if item["id"].lower() == room_id), None)
        if room:
            return {
                "kind": "room",
                "id": selected_start,
                "label": room["name"],
                "floor_id": room_floor_id(room),
                "points": room_target_points(room),
                "coords": room.get("coords"),
            }

    fallback = START_POINTS["intrare-principala"]
    return {
        "kind": "start-point",
        "id": "intrare-principala",
        "label": translate_start_label("intrare-principala", lang),
        "floor_id": fallback.get("floor_id", DEFAULT_FLOOR_ID),
        "points": [fallback["point"]] if fallback.get("point") in get_floor_points(fallback.get("floor_id")) else [],
        "coords": fallback.get("coords"),
    }


def clamp_coords(coords, floor_id=None, padding=24.0):
    # Ține marker-ele și bulele în interiorul imaginii etajului.
    floor_width = get_floor_width(floor_id)
    floor_height = get_floor_height(floor_id)
    return {
        "x": min(max(coords["x"], padding), floor_width - padding),
        "y": min(max(coords["y"], padding), floor_height - padding),
    }


def floor_image_src(floor_config):
    version = floor_config.get("image_version")
    if version:
        return f'{floor_config["image_url"]}?v={version}'
    return floor_config["image_url"]


def build_route_segments(point_ids, floor_id, final_coords=None, start_coords=None):
    # Transformă o secvență de noduri într-o listă de segmente SVG desenabile pe un etaj.
    floor_points = get_floor_points(floor_id)
    segments = []
    if point_ids and start_coords:
        clamped_start = clamp_coords(start_coords, floor_id)
        first_point = floor_points[point_ids[0]]
        if distance(clamped_start, first_point) > 1:
            start_segment = calculate_line(clamped_start, first_point, trim=False)
            start_segment["class_name"] = "route-line route-line--start"
            segments.append(start_segment)

    for index in range(len(point_ids) - 1):
        start_point = floor_points[point_ids[index]]
        end_point = floor_points[point_ids[index + 1]]
        segment = calculate_line(start_point, end_point)
        segment["class_name"] = "route-line"
        segments.append(segment)


    """if point_ids and len(point_ids) == 1:
        destination = clamp_coords(final_coords, floor_id)
        segment = calculate_line(clamped_start,destination)
        segment["class_name"] = "route-line"
        segments.pop()
        segments.append(segment)
        return segments"""
    print(point_ids)
    if point_ids and final_coords:
        destination = clamp_coords(final_coords, floor_id)
        last_point = floor_points[point_ids[-1]]
        if len(point_ids) == 2:
            


            f_point = floor_points[point_ids[0]]
            s_point = floor_points[point_ids[1]]
            previous_point = floor_points[point_ids[-2]]
            last_point = floor_points[point_ids[-1]]
            if f_point["x"] == s_point["x"]:
                segments.pop(0)
                m_point ={
                    "x" : f_point["x"],
                    "y" : clamped_start["y"]
                }
                seg = calculate_line(clamped_start,m_point,trim = False)
                seg["class_name"] = "route-line route-line--start"
                segments.pop(0)
                seg1 = calculate_line(m_point,s_point,trim = False)
                seg1["class_name"] = "route-line"
                segments.insert(0,seg1)
                segments.insert(0,seg)
                middle_point = {
                    "x": last_point["x"],
                    "y": destination["y"],
                }

                
                segments.pop()
                first_final_segment = calculate_line(m_point, middle_point, trim=False)
                first_final_segment["class_name"] = "route-line"
                segments.append(first_final_segment)

                second_final_segment = calculate_line(middle_point, destination, trim=False)
                second_final_segment["class_name"] = "route-line"
                segments.append(second_final_segment)
                return segments
                
            else:
                segments.pop(0)
                m_point ={
                    "x" : clamped_start["x"],
                    "y" : f_point["y"]
                }
                seg = calculate_line(clamped_start,m_point,trim = False)
                seg["class_name"] = "route-line route-line--start"
                segments.pop(0)
                seg1 = calculate_line(m_point,s_point,trim= False)
                seg1["class_name"] = "route-line"
                segments.insert(0,seg1)
                segments.insert(0,seg)
                middle_point = {
                    "x": destination["x"],
                    "y": last_point["y"],
                }
                if segments:
                    segments.pop()
                first_final_segment = calculate_line(m_point, middle_point, trim=False)
                first_final_segment["class_name"] = "route-line"
                segments.append(first_final_segment)

                second_final_segment = calculate_line(middle_point, destination, trim=False)
                second_final_segment["class_name"] = "route-line"
                segments.append(second_final_segment)
                return segments
            
            



        if len(point_ids) > 2:

            f_point = floor_points[point_ids[0]]
            s_point = floor_points[point_ids[1]]
            if f_point["x"] == s_point["x"]:
                segments.pop(0)
                m_point ={
                    "x" : f_point["x"],
                    "y" : clamped_start["y"]
                }
                seg = calculate_line(clamped_start,m_point,trim = False)
                seg["class_name"] = "route-line route-line--start"
                segments.pop(0)
                seg1 = calculate_line(m_point,s_point,trim = False)
                seg1["class_name"] = "route-line"
                segments.insert(0,seg1)
                segments.insert(0,seg)
                
            else:
                
                segments.pop(0)
                m_point ={
                    "x" : clamped_start["x"],
                    "y" : f_point["y"]
                }
                seg = calculate_line(clamped_start,m_point,trim = False)
                seg["class_name"] = "route-line route-line--start"
                segments.pop(0)
                seg1 = calculate_line(m_point,s_point,trim= False)
                seg1["class_name"] = "route-line"
                segments.insert(0,seg1)
                segments.insert(0,seg)







            previous_point = floor_points[point_ids[-2]]
            
            segments.pop()
            if previous_point["x"] == last_point["x"]:
                middle_point = {
                    "x": last_point["x"],
                    "y": destination["y"],
                }

                
                first_final_segment = calculate_line(previous_point, middle_point, trim=False)
                first_final_segment["class_name"] = "route-line"
                segments.append(first_final_segment)

                
                second_final_segment = calculate_line(middle_point, destination, trim=False)
                second_final_segment["class_name"] = "route-line"
                segments.append(second_final_segment)
                return segments
            
            elif previous_point["y"] == last_point["y"]:
                middle_point = {
                    "x": destination["x"],
                    "y": last_point["y"],
                }

                first_final_segment = calculate_line(previous_point, middle_point, trim=False)
                first_final_segment["class_name"] = "route-line"
                segments.append(first_final_segment)

                second_final_segment = calculate_line(middle_point, destination, trim=False)
                second_final_segment["class_name"] = "route-line"
                segments.append(second_final_segment)
              
                return segments
        
 
        final_segment = calculate_line(last_point, destination, trim=False)
        final_segment["class_name"] = "route-line"
        segments.append(final_segment)
    return segments


def find_best_target_path(start_point_ids, target_point_ids, start_floor_id=DEFAULT_FLOOR_ID, target_floor_id=DEFAULT_FLOOR_ID):
    # Varianta principală de Dijkstra pe întreaga clădire, inclusiv muchiile verticale dintre etaje.
    target_nodes = {node_key(target_floor_id, point_id) for point_id in target_point_ids}
    valid_starts = [
        node_key(start_floor_id, point_id)
        for point_id in start_point_ids
        if point_id in get_floor_points(start_floor_id)
    ]
    combined_points, combined_graph = build_combined_graph()

    if not target_nodes or not valid_starts:
        return [], None

    frontier = [(0, start_point_id, [start_point_id]) for start_point_id in valid_starts]
    best_cost = {start_point_id: 0 for start_point_id in valid_starts}

    while frontier:
        frontier.sort(key=lambda item: item[0])
        cost, current, path = frontier.pop(0)

        if current in target_nodes:
            return path, current

        for neighbor in combined_graph.get(current, []):
            new_cost = cost + node_distance(current, neighbor, combined_points)
            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                frontier.append((new_cost, neighbor, path + [neighbor]))

    return [], None


def calculate_line(start, end, trim=True):
    delta_x = end["x"] - start["x"]
    delta_y = end["y"] - start["y"]
    length = sqrt(delta_x * delta_x + delta_y * delta_y)
    inset = 20.0

    if trim and length > inset * 2:
        unit_x = delta_x / length
        unit_y = delta_y / length
        start = {
            "x": start["x"] + unit_x * inset,
            "y": start["y"] + unit_y * inset,
        }
        end = {
            "x": end["x"] - unit_x * inset,
            "y": end["y"] - unit_y * inset,
        }
        delta_x = end["x"] - start["x"]
        delta_y = end["y"] - start["y"]
        length = sqrt(delta_x * delta_x + delta_y * delta_y)

    return {
        "x1": round(start["x"], 1),
        "y1": round(start["y"], 1),
        "x2": round(end["x"], 1),
        "y2": round(end["y"], 1),
    }


def t(lang):
    return TEXT["en"] if lang == "en" else TEXT["ro"]


def translate_start_label(key, lang):
    return START_POINT_LABELS.get(key, {}).get(lang, key)


def translate_floor_label(label, lang):
    return FLOOR_LABELS.get(label, {}).get(lang, label)


def format_floor_move(level_from, level_to, lang):
    difference = level_to - level_from
    count = abs(difference)
    if count == 0:
        return ""

    if lang == "en":
        direction = "Go up" if difference > 0 else "Go down"
        noun = "floor" if count == 1 else "floors"
        return f"{direction} {count} {noun}"

    direction = "Urca" if difference > 0 else "Coboara"
    if count == 1:
        return f"{direction} un etaj"
    return f"{direction} {count} etaje"


def point_label(point_id, lang):
    if ":" in point_id:
        _, point_id = split_node_key(point_id)
    return translate_start_label(point_id, lang)


def route_floor_stages(route_node_ids):
    # Împarte traseul complet în etape consecutive pe etaje, inclusiv revenirile pe același etaj.
    if not route_node_ids:
        return []

    stages = []
    current_floor_id, _ = split_node_key(route_node_ids[0])
    start_index = 0

    for index in range(1, len(route_node_ids)):
        floor_id, _ = split_node_key(route_node_ids[index])
        if floor_id != current_floor_id:
            stages.append(
                {
                    "floor_id": current_floor_id,
                    "start_index": start_index,
                    "end_index": index - 1,
                }
            )
            current_floor_id = floor_id
            start_index = index

    stages.append(
        {
            "floor_id": current_floor_id,
            "start_index": start_index,
            "end_index": len(route_node_ids) - 1,
        }
    )
    return stages


def route_segment_for_stage(route_node_ids, stage_index):
    stages = route_floor_stages(route_node_ids)
    if stage_index < 0 or stage_index >= len(stages):
        return None, [], None, None

    stage = stages[stage_index]
    floor_id = stage["floor_id"]
    point_ids = [split_node_key(node_id)[1] for node_id in route_node_ids[stage["start_index"]:stage["end_index"] + 1]]

    entry_stair_coords = None
    if stage["start_index"] > 0:
        stair_id = find_transition_stair(route_node_ids[stage["start_index"] - 1], route_node_ids[stage["start_index"]])
        if stair_id:
            entry_stair_coords = get_stair_coords(stair_id, floor_id)

    exit_stair_coords = None
    if stage["end_index"] + 1 < len(route_node_ids):
        stair_id = find_transition_stair(route_node_ids[stage["end_index"]], route_node_ids[stage["end_index"] + 1])
        if stair_id:
            exit_stair_coords = get_stair_coords(stair_id, floor_id)

    return floor_id, point_ids, entry_stair_coords, exit_stair_coords


def is_pass_through_stage(route_node_ids, stage_index):
    # Detectează etapele care sunt doar o aterizare pe aceeași scară, fără traseu util pe etaj.
    stages = route_floor_stages(route_node_ids)
    if stage_index <= 0 or stage_index >= len(stages) - 1:
        return False

    stage = stages[stage_index]
    if stage["end_index"] - stage["start_index"] != 0:
        return False

    entry_stair = find_transition_stair(route_node_ids[stage["start_index"] - 1], route_node_ids[stage["start_index"]])
    exit_stair = find_transition_stair(route_node_ids[stage["end_index"]], route_node_ids[stage["end_index"] + 1])
    return bool(entry_stair and entry_stair == exit_stair)


def next_display_stage_index(route_node_ids, active_stage_index):
    stages = route_floor_stages(route_node_ids)
    next_index = active_stage_index + 1
    while next_index < len(stages) - 1 and is_pass_through_stage(route_node_ids, next_index):
        next_index += 1
    return next_index if next_index < len(stages) else None


def build_route_step_text(route_point_ids, target_option, lang):
    # Convertește nodurile brute din traseu în pași textuali scurți pentru interfață.
    text = t(lang)
    if not route_point_ids:
        if target_option["type"] == "room":
            return [text["step_arrive"].format(room=target_option["name"])]
        return [text["step_arrive_target"].format(target=target_option["label"])]

    steps = []
    for point_id in route_point_ids[1:]:
        steps.append(text["step_move"].format(point=point_label(point_id, lang)))

    if target_option["type"] == "room":
        steps.append(text["step_arrive"].format(room=target_option["name"]))
    else:
        steps.append(text["step_arrive_target"].format(target=target_option["label"]))
    return steps


def get_floor_transition_info(route_node_ids, current_floor_id):
    entry_transition = None
    exit_transition = None

    for index in range(1, len(route_node_ids)):
        previous_node = route_node_ids[index - 1]
        current_node = route_node_ids[index]
        previous_floor_id, _ = split_node_key(previous_node)
        current_floor_id_value, _ = split_node_key(current_node)

        if previous_floor_id == current_floor_id_value:
            continue

        stair_id = find_transition_stair(previous_node, current_node)
        transition = {
            "from_floor_id": previous_floor_id,
            "to_floor_id": current_floor_id_value,
            "stair_id": stair_id,
        }

        if current_floor_id_value == current_floor_id and entry_transition is None:
            entry_transition = transition
        if previous_floor_id == current_floor_id and exit_transition is None:
            exit_transition = transition

    return entry_transition, exit_transition


def stage_transition_move(route_node_ids, active_stage_index):
    # Calculează tranziția reală dintre două etape consecutive, inclusiv etajele traversate pe aceeași scară.
    stages = route_floor_stages(route_node_ids)
    if active_stage_index < 0 or active_stage_index >= len(stages) - 1:
        return None

    current_stage = stages[active_stage_index]
    transition_index = current_stage["end_index"] + 1
    if transition_index >= len(route_node_ids):
        return None

    from_floor_id, _ = split_node_key(route_node_ids[transition_index - 1])
    to_floor_id, _ = split_node_key(route_node_ids[transition_index])
    stair_id = find_transition_stair(route_node_ids[transition_index - 1], route_node_ids[transition_index])
    if not stair_id:
        return None

    start_level = get_floor_level(from_floor_id)
    end_level = get_floor_level(to_floor_id)

    next_index = active_stage_index + 1
    while next_index < len(stages) - 1 and is_pass_through_stage(route_node_ids, next_index):
        stage = stages[next_index]
        pass_through_transition_index = stage["end_index"] + 1
        if pass_through_transition_index >= len(route_node_ids):
            break

        next_stair_id = find_transition_stair(
            route_node_ids[pass_through_transition_index - 1],
            route_node_ids[pass_through_transition_index],
        )
        if next_stair_id != stair_id:
            break

        to_floor_id, _ = split_node_key(route_node_ids[pass_through_transition_index])
        end_level = get_floor_level(to_floor_id)
        next_index += 1

    return {
        "from_floor_id": from_floor_id,
        "to_floor_id": to_floor_id,
        "from_level": start_level,
        "to_level": end_level,
        "stair_id": stair_id,
    }


def stair_button_label(route_node_ids, active_stage_index, lang):
    # Eticheta butonului de schimbare etaj este calculată din tranziția reală a traseului.
    move = stage_transition_move(route_node_ids, active_stage_index)
    if not move:
        return ""
    return format_floor_move(move["from_level"], move["to_level"], lang)


def render_options(selected_start, lang):
    entry_options = []
    room_options = []
    for key in START_POINTS:
        selected = " selected" if key == selected_start else ""
        entry_options.append(
            f'<option value="{escape(key)}"{selected}>{escape(translate_start_label(key, lang))}</option>'
        )
    for room in NORMALIZED_ROOMS:
        value = f"room:{room['id']}"
        selected = " selected" if value == selected_start else ""
        room_options.append(
            f'<option value="{escape(value)}"{selected}>{escape(room["name"])}</option>'
        )
    return (
        f'<optgroup label="{escape("Intrari" if lang == "ro" else "Entrances")}">{"".join(entry_options)}</optgroup>'
        f'<optgroup label="{escape("Sali" if lang == "ro" else "NORMALIZED_ROOMS")}">{"".join(room_options)}</optgroup>'
    )


def render_target_options(selected_target, lang):
    # Construiește lista de destinații pentru formular, combinând intrările și sălile normalizate.
    entry_options = []
    room_options = []
    for key in START_POINTS:
        selected = " selected" if key == selected_target else ""
        entry_options.append(
            f'<option value="{escape(key)}"{selected}>{escape(translate_start_label(key, lang))}</option>'
        )
    for room in NORMALIZED_ROOMS:
        value = room["name"]
        selected = " selected" if value == selected_target or f"room:{room['id']}" == selected_target else ""
        room_options.append(
            f'<option value="{escape(value)}"{selected}>{escape(room["name"])}</option>'
        )
    return (
        f'<optgroup label="{escape("Intrari" if lang == "ro" else "Entrances")}">{"".join(entry_options)}</optgroup>'
        f'<optgroup label="{escape("Sali" if lang == "ro" else "Rooms")}">{"".join(room_options)}</optgroup>'
    )


def render_quick_rooms(selected_start, lang):
    # Listează câteva destinații rapide pentru acces direct din interfață.
    chips = []
    for room in NORMALIZED_ROOMS[:5]:
        chips.append(
            f'<a class="chip" href="/?lang={escape(lang)}&start={escape(selected_start)}&target={escape(room["name"])}">{escape(room["name"])}</a>'
        )
    return "".join(chips)


def render_route_lines(segments, floor_id=DEFAULT_FLOOR_ID):
    # Randarea finală a traseului în SVG; segmentele au deja geometria calculată înainte.
    if not segments:
        return ""
    lines = []
    for segment in segments:
        lines.append(
            '<line class="{class_name}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"></line>'.format(
                class_name=segment.get("class_name", "route-line"),
                x1=segment["x1"],
                y1=segment["y1"],
                x2=segment["x2"],
                y2=segment["y2"],
            )
        )
    return '<svg class="map-route" viewBox="0 0 {width} {height}" preserveAspectRatio="none">{lines}</svg>'.format(
        width=get_floor_width(floor_id),
        height=get_floor_height(floor_id),
        lines="".join(lines),
    )


def render_you_are_here_marker(point_id, floor_id=DEFAULT_FLOOR_ID):
    # Marker-ul vizual pentru poziția curentă bazat pe un nod din graf.
    floor_points = get_floor_points(floor_id)
    if point_id not in floor_points:
        return ""

    return render_you_are_here_marker_coords(floor_points[point_id], floor_id)


def render_you_are_here_marker_coords(coords, floor_id=DEFAULT_FLOOR_ID):
    # Variantă pentru marker-ul de start atunci când poziția vizuală diferă de nodul logic.
    coords = clamp_coords(coords, floor_id)
    floor_width = get_floor_width(floor_id)
    floor_height = get_floor_height(floor_id)
    return """
    <div class="you-are-here" style="left: {x:.3f}%; top: {y:.3f}%;">
      <div class="you-are-here__dot"></div>
      <div class="you-are-here__arrow"></div>
    </div>
    """.format(
        x=(coords["x"] / floor_width) * 100 if floor_width else 0,
        y=(coords["y"] / floor_height) * 100 if floor_height else 0,
    )


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


def render_page(selected_start, target_query, lang, view_floor_id=None, view_stage=None):
    # Funcția principală de compunere a paginii: rezolvă startul, ținta, traseul și etajul afișat.
    text = t(lang)
    start_option = resolve_start_option(selected_start, lang)
    target_option = resolve_target_option(target_query, lang, start_option)
    active_floor_id = target_option["floor_id"] if target_option else start_option.get("floor_id", DEFAULT_FLOOR_ID)
    floor_config = get_floor_config(active_floor_id)
    selected_start = start_option["id"]
    start_label = start_option["label"]
    steps = ""
    title = text["default_title"]
    route_lines = ""
    floor_nav = ""
    floor_nav = ""
    start_marker_point_id = start_option["points"][0] if start_option["points"] else None

    if target_option:
        floor_label = translate_floor_label(target_option.get("floor", get_floor_config(target_option["floor_id"])["label_ro"]), lang)
        full_steps = [
            text["from_prefix"].format(start=start_label),
            text["to_room_prefix"].format(target=target_option["name"]) if target_option["type"] == "room"
            else text["to_entrance_prefix"].format(target=target_option["label"]),
        ]
        if target_option["type"] == "restroom" and target_option.get("route"):
            route_node_ids = target_option["route"]
        else:
            route_node_ids, _ = find_best_target_path(
                start_option["points"],
                target_option["points"],
                start_option.get("floor_id", DEFAULT_FLOOR_ID),
                target_option["floor_id"],
            )
        floor_stages = route_floor_stages(route_node_ids)
        active_stage_index = 0
        if floor_stages:
            default_view_floor = start_option.get("floor_id", DEFAULT_FLOOR_ID)
            if view_stage is not None and 0 <= view_stage < len(floor_stages):
                active_stage_index = view_stage
            elif view_floor_id:
                for index, stage in enumerate(floor_stages):
                    if stage["floor_id"] == view_floor_id:
                        active_stage_index = index
                        break
            else:
                for index, stage in enumerate(floor_stages):
                    if stage["floor_id"] == default_view_floor:
                        active_stage_index = index
                        break

            active_floor_id, route_point_ids, entry_stair_coords, exit_stair_coords = route_segment_for_stage(route_node_ids, active_stage_index)
            floor_config = get_floor_config(active_floor_id)
        else:
            active_stage_index = 0
            route_point_ids, entry_stair_coords, exit_stair_coords = [], None, None

        if route_point_ids:
            start_marker_point_id = route_point_ids[0]
        full_steps.extend(build_route_step_text(route_point_ids, target_option, lang))
        title = target_option["name"]
        steps = render_steps(full_steps)
        route_lines = render_route_lines(
            build_route_segments(
                route_point_ids,
                active_floor_id,
                target_option["coords"] if floor_stages and active_stage_index == len(floor_stages) - 1 else exit_stair_coords,
                start_option.get("coords") if active_stage_index == 0 and start_option.get("floor_id", DEFAULT_FLOOR_ID) == active_floor_id else entry_stair_coords,
            ),
            active_floor_id,
        )
        if route_node_ids and floor_stages and active_stage_index < len(floor_stages) - 1:
            _, exit_transition = get_floor_transition_info(route_node_ids, active_floor_id)
            floor_nav_links = []
            if exit_transition:
                next_stage_index = next_display_stage_index(route_node_ids, active_stage_index)
                next_floor_id = floor_stages[next_stage_index]["floor_id"] if next_stage_index is not None else exit_transition["to_floor_id"]
                next_label = stair_button_label(route_node_ids, active_stage_index, lang)
                floor_nav_links.append(
                    f'<a class="cta floor-cta" href="/?lang={escape(lang)}&start={escape(selected_start)}&target={escape(target_query)}&view_floor={escape(next_floor_id)}&view_stage={next_stage_index if next_stage_index is not None else active_stage_index + 1}">'
                        f'{escape(next_label or text["next_floor"])}'
                        f'</a>'
                )
            if floor_nav_links:
                floor_nav = '<div class="floor-nav">' + "".join(floor_nav_links) + '</div>'
    elif target_query:
        title = text["not_found_title"]

    if target_option and active_stage_index == 0 and start_option.get("floor_id", DEFAULT_FLOOR_ID) == active_floor_id:
        start_marker = render_you_are_here_marker_coords(start_option["coords"], active_floor_id)
    else:
        start_marker = render_you_are_here_marker(start_marker_point_id, active_floor_id)

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
          <div><strong>{len(NORMALIZED_ROOMS)}</strong><span>{text["hero_stat_2"]}</span></div>
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
            <span>{text["target_label"]}</span>
            <select id="target-point" name="target">
              {render_target_options(target_query, lang)}
            </select>
          </label>

          <div class="route-actions">
            <button type="submit" class="cta">{text["submit"]}</button>
            <button type="submit" class="cta cta--secondary" name="restroom" value="female">{text["restroom_female"]}</button>
            <button type="submit" class="cta cta--secondary" name="restroom" value="male">{text["restroom_male"]}</button>
          </div>
        </form>

        <div class="quick-NORMALIZED_ROOMS" aria-label="{text["quick_rooms"]}">
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
          {floor_nav}
        </div>

        <div class="campus-map">
          <img class="floor-plan" src="{escape(floor_image_src(floor_config))}" alt="Harta {escape(floor_config['label_ro'])}">
          <div class="map-route">{route_lines}</div>
          {start_marker}
        </div>
        <div class="map-legend" aria-label="{text["legend_title"]}">
          <p class="section-tag">{text["legend_title"]}</p>
          <div class="map-legend__items">
            <div class="map-legend__item">
              <span class="map-legend__swatch map-legend__swatch--route"></span>
              <span>{text["legend_route"]}</span>
            </div>
            <div class="map-legend__item">
              <span class="map-legend__swatch map-legend__swatch--start"></span>
              <span>{text["legend_start"]}</span>
            </div>
            <div class="map-legend__item">
              <span class="map-legend__swatch map-legend__swatch--floor"></span>
              <span>{text["legend_floor"]}</span>
            </div>
          </div>
        </div>
      </section>

    </main>
    <footer class="site-footer">
      <div class="site-footer__content">
        <div class="site-footer__section">
          <p class="section-tag">{text["report_issue"]}</p>
          <p class="site-footer__text">{text["report_issue_text"]}</p>
        </div>
        <a class="cta site-footer__cta" href="{escape(REPORT_ISSUE_URL)}" target="_blank" rel="noopener noreferrer">{text["report_issue_cta"]}</a>
      </div>
      <div class="project-meta project-meta--footer">
        <div class="project-meta__block">
          <span class="project-meta__label">{text["creator_label"]}</span>
          <strong>{escape(CREATOR_NAME)}</strong>
        </div>
        <div class="project-meta__block">
          <span class="project-meta__label">{text["coordinators_label"]}</span>
          <strong>{escape(", ".join(COORDINATING_TEACHERS))}</strong>
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
"""
    return html.encode("utf-8")


def app(environ, start_response):
    # Entry-point WSGI: servește fișierele statice simple și randează pagina principală.
    path = unquote(environ.get("PATH_INFO", "/"))
    if path == "/styles.css":
        css = STYLES_PATH.read_bytes()
        start_response("200 OK", [("Content-Type", "text/css; charset=utf-8")])
        return [css]

    for floor_config in FLOOR_CONFIGS.values():
        if path == floor_config["image_url"]:
            image = floor_config["image_path"].read_bytes()
            suffix = floor_config["image_path"].suffix.lower()
            if suffix in {".tif", ".tiff"}:
                content_type = "image/tiff"
            elif suffix == ".webp":
                content_type = "image/webp"
            else:
                content_type = "image/png"
            start_response(
                "200 OK",
                [
                    ("Content-Type", content_type),
                    ("Cache-Control", "public, max-age=31536000"),
                ],
            )
            return [image]

    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Pagina nu a fost gasita."]

    params = parse_qs(environ.get("QUERY_STRING", ""))
    lang = params.get("lang", [""])[0]
    selected_start = params.get("start", ["intrare-principala"])[0]
    restroom_query = params.get("restroom", [""])[0]
    target_query = f"restroom:{restroom_query}" if restroom_query else (params.get("target", [""])[0] or params.get("room", [""])[0])
    view_floor_id = params.get("view_floor", [""])[0] or None
    view_stage_raw = params.get("view_stage", [""])[0]
    view_stage = int(view_stage_raw) if view_stage_raw.isdigit() else None

    if lang not in TEXT:
        body = render_language_page()
    else:
        body = render_page(selected_start, target_query, lang, view_floor_id, view_stage)
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [body]


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"UniWay Craiova ruleaza la http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()
