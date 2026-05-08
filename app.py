from html import escape
from math import atan2, degrees, sqrt
import os
from pathlib import Path
import ast
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

MAP_WIDTH = 4572
MAP_HEIGHT = 4372
MAP_RATIO = MAP_HEIGHT / MAP_WIDTH
DEFAULT_FLOOR_ID = "etaj-1"
STAIR_TRAVEL_COST = 900.0


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
    "P21": {"x": 640.1, "y": 3064.3},
    "P22": {"x": 3950.2, "y": 3047.3},
    "P23": {"x": 2279.3 , "y": 949},
    "P27" : {"x": 827.5, "y" : 3400},
    "P6-11": {"x":3735.3, "y" :2000}
}

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

GRAPH = {
    "P1": ["P2", "P3", "P4","P1-3"],
    "P2": ["P1", "P7","P27"],
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
    "P14": ["P13", "P15"],
    "P15": ["P14", "P8", "P16"],
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
    "P27" : ["P2","P7"]

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
GRAPH_ETAJ_0 = {
    "P1": ["P2","P9","P1-9"],
    "P2": ["P1", "P3"],
    "P3": ["P2"],
    "P4": [ "P5"],
    "P5": ["P4", "P6"],
    "P6": ["P5","P7","P6-7"],
    "P7": ["P6", "P8","P10","P6-7","P7-10"],
    "P8": ["P7", "P9"],
    "P9": ["P8","P1","P1-9"],
    "P10": ["P7","P11","P7-10"],
    "P11": ["P12","P10"],
    "P12": ["P11","P13","P15"],
    "P13": ["P12", "P14"],
    "P14": ["P13"],
    "P15": ["P12"],
    "P16": ["P17"],
    "P17": ["P16"],
    "P18": [ "P19"],
    "P19": ["P18","P20"],
    "P20": ["P19"],
    "P1-9":["P1","P9"],
    "P6-7":["P6", "P7"],
    "P7-10": ["P7","P10"]
    
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
    "P7-10": {"x":4011 , "y":2000}
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
    "P9": ["P8","P9-15"],
    "P10": ["P8","P11","P10-13"],
    "P11": ["P11-12","P10","P1-11"],
    "P12": ["P11-12","P13"],
    "P13": ["P12", "P14"],
    "P14": ["P13","P15"],
    "P15": ["P14","P16"],
    "P16": ["P15"],
    "P17": ["P18"],
    "P18": [ "P17"],
    "P19": ["P20"],
    "P20": ["P19"],
    "P1-11": ["P1","P11"],
    "P6-7": ["P6","P7"],
    "P10-13":["P10","P13"],
    "P9-15":["P9","P15"],
    "P11-12":["P11","P12"]
    
}

POINTS_ETAJ_3 = {
    "P1": {"x": 625, "y": 3310},
    "P2": {"x": 625, "y": 3835},
    "P3": {"x": 1757, "y": 3835},
    "P4": {"x": 2360, "y": 3810},
    "P5": {"x": 3500, "y": 3810},
    "P6": {"x": 3500, "y": 3290},
    "P7": {"x": 3500, "y": 2450},
    "P8": {"x": 2081, "y": 2450},
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
    
}


GRAPH_ETAJ_4 = {
    "P1" : ["P2"],
    "P2": ["P1","P3"],
    "P3" :["P2"],
    "P4": ["P5"],
    "P5" :["P4"]
}


POINTS_ETAJ_4 = {
    "P1": {"x": 1560, "y": 600},
    "P2": {"x": 689, "y": 600},
    "P3": {"x": 689, "y": 1087},
    "P4": {"x": 2720, "y": 613},
    "P5": {"x": 3400, "y": 613},
    
    
}

START_POINTS = {
    "intrare-principala": {"label": "Intrare Principala", "coords": {"x": 2276.6, "y": 4103.6}, "point": "P1", "floor_id": DEFAULT_FLOOR_ID},
    "intrare-teatru": {"label": "Intrare Teatru", "coords": {"x": 375.5, "y": 3024.3}, "point": "P21", "floor_id": DEFAULT_FLOOR_ID},
    "intrare-parcare": {"label": "Intrare Parcare", "coords": {"x": 4269.1, "y": 3024.3}, "point": "P22", "floor_id": DEFAULT_FLOOR_ID},
}

ROOMS = [
  {
    "id": "101",
    "name": "101",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P3",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1896.0,
      "y": 3708.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "103",
    "name": "103",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P3",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1670.0,
      "y": 3710.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "103",
    "name": "103",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P3",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1558.0,
      "y": 3712.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "106",
    "name": "106",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P2",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1158.0,
      "y": 3784.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "107",
    "name": "107",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P2",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1160.0,
      "y": 3648.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "108",
    "name": "108",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P2",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1162.0,
      "y": 3500.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "109",
    "name": "109",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P1-9",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1149.0,
      "y": 3137.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "110",
    "name": "110",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P1-9",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1159.0,
      "y": 2781.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "111",
    "name": "111",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P1-9",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1158.0,
      "y": 2782.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "113",
    "name": "113",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1271.0,
      "y": 1789.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "114",
    "name": "114",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1401.0,
      "y": 1731.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "114A",
    "name": "114A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1401.0,
      "y": 1731.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "115",
    "name": "115",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1407.0,
      "y": 1721.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "116",
    "name": "116",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1867.0,
      "y": 1739.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "117",
    "name": "117",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2403.0,
      "y": 1647.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118",
    "name": "118",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2399.0,
      "y": 1651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118A",
    "name": "118A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2537.0,
      "y": 1361.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118B",
    "name": "118B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2541.0,
      "y": 1197.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118C",
    "name": "118C",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2545.0,
      "y": 1041.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118D",
    "name": "118D",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2607.0,
      "y": 1011.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118E",
    "name": "118E",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2679.0,
      "y": 1037.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118F",
    "name": "118F",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2681.0,
      "y": 1205.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "118G",
    "name": "118G",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2681.0,
      "y": 1368.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "122",
    "name": "122",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1750.0,
      "y": 2566.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "122A",
    "name": "122A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1522.0,
      "y": 2563.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "123",
    "name": "123",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1878.0,
      "y": 2566.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "124",
    "name": "124",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2011.0,
      "y": 2562.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "125",
    "name": "125",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2965.0,
      "y": 2575.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "126",
    "name": "126",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3350.0,
      "y": 2572.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "127",
    "name": "127",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3092.0,
      "y": 2566.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "128",
    "name": "128",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P8",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3515.0,
      "y": 2574.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "134",
    "name": "134",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P15",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2693.0,
      "y": 1690.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "135",
    "name": "135",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3527.0,
      "y": 1749.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "135",
    "name": "135",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 2883.0,
      "y": 1748.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "137",
    "name": "137",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3701.0,
      "y": 1755.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "138",
    "name": "138",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3899.0,
      "y": 1753.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "139",
    "name": "139",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P12",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4019.0,
      "y": 1751.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "140",
    "name": "140",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P7-10",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4061.0,
      "y": 1825.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "141",
    "name": "141",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P7-10",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4061.0,
      "y": 1825.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "142",
    "name": "142",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P7-10",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4065.0,
      "y": 2257.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "145",
    "name": "145",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P6-7",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4085.0,
      "y": 2599.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "146",
    "name": "146",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P6-7",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4075.0,
      "y": 2791.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "147",
    "name": "147",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P6-7",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4081.0,
      "y": 2973.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "148",
    "name": "148",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P6-7",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4073.0,
      "y": 3145.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "149",
    "name": "149",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P5",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4075.0,
      "y": 3483.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "150",
    "name": "150",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P5",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4074.0,
      "y": 3480.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "151",
    "name": "151",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P5",
    "floor_id": "etaj-0",
    "coords": {
      "x": 4077.0,
      "y": 3800.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "155",
    "name": "155",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P4",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3867.0,
      "y": 3724.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "156",
    "name": "156",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P4",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3424.0,
      "y": 3714.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "163",
    "name": "163",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P17",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3979.0,
      "y": 779.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "164",
    "name": "164",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P17",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3903.0,
      "y": 725.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "165",
    "name": "165",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P17",
    "floor_id": "etaj-0",
    "coords": {
      "x": 3735.0,
      "y": 715.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "167",
    "name": "167",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P19",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1231.0,
      "y": 691.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "170",
    "name": "170",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 0",
    "point": "P19",
    "floor_id": "etaj-0",
    "coords": {
      "x": 1235.0,
      "y": 1281.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "207",
    "name": "207",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P27",
    "coords": {
      "x": 765.0,
      "y": 3761.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "208",
    "name": "208",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P27",
    "coords": {
      "x": 767.0,
      "y": 3640.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "209",
    "name": "209",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P27",
    "coords": {
      "x": 771.0,
      "y": 3501.0
    },
    "summary": "Sala de pe coloana stanga, deasupra lui 208.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "210",
    "name": "210",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P8",
    "coords": {
      "x": 756.0,
      "y": 2900.0
    },
    "summary": "Sala de pe coloana stanga, aproape de intrarea Teatru.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "211",
    "name": "211",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P8",
    "coords": {
      "x": 727.0,
      "y": 2644.0
    },
    "summary": "Sala de pe coloana stanga, deasupra lui 210.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "216",
    "name": "216",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P9",
    "coords": {
      "x": 1154.0,
      "y": 2451.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "217",
    "name": "217",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P9",
    "coords": {
      "x": 1154.0,
      "y": 2452.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "218",
    "name": "218",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P9",
    "coords": {
      "x": 1527.0,
      "y": 2457.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "219",
    "name": "219",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P9",
    "coords": {
      "x": 1683.4,
      "y": 2459.8
    },
    "summary": "Sala din zona centrala-stanga a coridorului median.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "219",
    "name": "219",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P9",
    "coords": {
      "x": 1518.0,
      "y": 2461.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "220",
    "name": "220",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P15",
    "coords": {
      "x": 765.0,
      "y": 1736.0
    },
    "summary": "Sala din zona superioara stanga, pe coridorul lui P15.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "220b",
    "name": "220B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P15",
    "coords": {
      "x": 753.0,
      "y": 1745.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "221",
    "name": "221",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P15",
    "coords": {
      "x": 750.0,
      "y": 1631.0
    },
    "summary": "Sala de pe capatul stang al coridorului superior median.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "222",
    "name": "222",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P14",
    "coords": {
      "x": 1189.0,
      "y": 1548.0
    },
    "summary": "Sala de pe coridorul superior median, partea stanga.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "223",
    "name": "223",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P14",
    "coords": {
      "x": 2035.0,
      "y": 1559.0
    },
    "summary": "Sala de pe coridorul superior median.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "223a",
    "name": "223A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P14",
    "coords": {
      "x": 1300.0,
      "y": 1553.0
    },
    "summary": "Sala mica langa 223.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "224",
    "name": "224",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P14",
    "coords": {
      "x": 2049.0,
      "y": 1550.0
    },
    "summary": "Sala din dreptul nodului P14.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "226",
    "name": "226",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 2614.1,
      "y": 1895.6
    },
    "summary": "Sala din zona centrala, accesibila din coridorul P12.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "228",
    "name": "228",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P14",
    "coords": {
      "x": 1978.6,
      "y": 1903.3
    },
    "summary": "Sala centrala din zona scarii principale.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "230",
    "name": "230",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P13",
    "coords": {
      "x": 2195.8,
      "y": 1578.3
    },
    "summary": "Sala din retragerea coridorului spre dreapta.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231a",
    "name": "231A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2209.0,
      "y": 1069.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231b",
    "name": "231B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2197.0,
      "y": 965.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231c",
    "name": "231C",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2211.0,
      "y": 863.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231d",
    "name": "231D",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2383.0,
      "y": 857.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231e",
    "name": "231E",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2415.0,
      "y": 981.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "231f",
    "name": "231F",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P23",
    "coords": {
      "x": 2379.0,
      "y": 1061.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "232",
    "name": "232",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P17",
    "coords": {
      "x": 2023.0,
      "y": 601.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "232A",
    "name": "232A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P17",
    "coords": {
      "x": 2024.0,
      "y": 589.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "232B",
    "name": "232B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P17",
    "coords": {
      "x": 2625.0,
      "y": 592.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "233a",
    "name": "233A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 2587.0,
      "y": 1559.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "233b",
    "name": "233B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 3091.0,
      "y": 1565.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "234",
    "name": "234",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 3275.0,
      "y": 1568.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "235",
    "name": "235",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 3457.0,
      "y": 1563.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "236",
    "name": "236",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 3637.0,
      "y": 1559.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "238",
    "name": "238",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P11",
    "coords": {
      "x": 3889.1,
      "y": 1600.0
    },
    "summary": "Sala de pe capatul drept al coridorului superior median.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "239",
    "name": "239",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P13",
    "coords": {
      "x": 2436.9,
      "y": 1508.3
    },
    "summary": "Sala de pe coridorul superior median din zona centrala.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "240",
    "name": "240",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P13",
    "coords": {
      "x": 2658.0,
      "y": 1539.0
    },
    "summary": "Sala centrala accesibila din nodul P13.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "240a",
    "name": "240A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P12",
    "coords": {
      "x": 2916.9,
      "y": 1508.3
    },
    "summary": "Sala mica din zona lui 240, accesibila din nodul P12.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "242",
    "name": "242",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P10",
    "coords": {
      "x": 2642.0,
      "y": 2451.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "243",
    "name": "243",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P10",
    "coords": {
      "x": 3064.0,
      "y": 2452.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "245",
    "name": "245",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "points": [
      "P10",
      "P6"
    ],
    "coords": {
      "x": 3412.0,
      "y": 2459.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "248",
    "name": "248",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "points": "P6-11",
    "coords": {
      "x": 3795.0,
      "y": 1983.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "251",
    "name": "251",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P5",
    "coords": {
      "x": 3784.0,
      "y": 2354.0
    },
    "summary": "Sala de pe coloana din dreapta, deasupra zonei de parcare.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "252",
    "name": "252",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P5",
    "coords": {
      "x": 3786.0,
      "y": 2472.0
    },
    "summary": "Sala de pe coloana dreapta, sub 251.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "253",
    "name": "253",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P5",
    "coords": {
      "x": 3795.0,
      "y": 2618.0
    },
    "summary": "Sala de pe coloana dreapta, sub 252.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "254",
    "name": "254",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P5",
    "coords": {
      "x": 3823.0,
      "y": 2881.0
    },
    "summary": "Sala de pe coloana dreapta, sub 253.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "255",
    "name": "255",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3794.0,
      "y": 3431.0
    },
    "summary": "Sala de pe coloana dreapta inferioara, deasupra lui 256.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "256",
    "name": "256",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3792.0,
      "y": 3633.0
    },
    "summary": "Sala de pe coloana dreapta inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "257",
    "name": "257",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3790.0,
      "y": 3754.0
    },
    "summary": "Sala din capatul din dreapta jos al etajului.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "258",
    "name": "258",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3456.4,
      "y": 3322.7
    },
    "summary": "Sala din zona 258, langa nucleul din dreapta jos.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "259",
    "name": "259",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P1-3",
    "coords": {
      "x": 3414.7,
      "y": 3689.7
    },
    "summary": "Sala din zona 259, aproape de P3.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "260",
    "name": "260",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P1-3",
    "coords": {
      "x": 3416.4,
      "y": 3679.0
    },
    "summary": "Sala din zona 260, aproape de 261.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "261",
    "name": "261",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P1-3",
    "coords": {
      "x": 3030.0,
      "y": 3611.0
    },
    "summary": "Sala din zona 261, aproape de coridorul inferior.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "262",
    "name": "262",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3223.3,
      "y": 3252.8
    },
    "summary": "Sala din zona nucleului inferior drept.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "263",
    "name": "263",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P3",
    "coords": {
      "x": 3374.1,
      "y": 3270.3
    },
    "summary": "Sala din zona nucleului inferior drept.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "266a",
    "name": "266A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P11",
    "coords": {
      "x": 3788.0,
      "y": 1189.0
    },
    "summary": "Sala de pe coloana dreapta superioara, langa 267.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "267",
    "name": "267",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P11",
    "coords": {
      "x": 3753.6,
      "y": 1254.8
    },
    "summary": "Sala de pe coloana dreapta superioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "268",
    "name": "268",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P11",
    "coords": {
      "x": 3871.0,
      "y": 1077.0
    },
    "summary": "Sala din zona 268, aproape de scara 4.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "268b",
    "name": "268B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P11",
    "coords": {
      "x": 3793.0,
      "y": 919.0
    },
    "summary": "Sala mica de pe coridorul superior drept, dupa 268.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "269",
    "name": "269",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P20",
    "coords": {
      "x": 3787.0,
      "y": 628.0
    },
    "summary": "Sala de pe coridorul superior drept, aproape de P20.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "270",
    "name": "270",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P19",
    "coords": {
      "x": 3735.0,
      "y": 464.0
    },
    "summary": "Sala de pe coridorul superior din dreapta.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "271",
    "name": "271",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "points": "P19",
    "coords": {
      "x": 3436.0,
      "y": 460.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "272",
    "name": "272",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "points": "P19",
    "coords": {
      "x": 3240.0,
      "y": 459.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "273",
    "name": "273",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P17",
    "coords": {
      "x": 2299.0,
      "y": 493.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "273A",
    "name": "273A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P17",
    "coords": {
      "x": 2305.0,
      "y": 491.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "274",
    "name": "274",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P18",
    "coords": {
      "x": 1970.0,
      "y": 531.0
    },
    "summary": "Sala de pe coridorul superior, sub balconul central.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "275",
    "name": "275",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P18",
    "coords": {
      "x": 1372.0,
      "y": 432.0
    },
    "summary": "Sala de pe coridorul superior, inainte de 274.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "276",
    "name": "276",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P16",
    "coords": {
      "x": 1077.0,
      "y": 437.0
    },
    "summary": "Sala de pe coridorul superior stang.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "277",
    "name": "277",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P16",
    "coords": {
      "x": 726.0,
      "y": 502.0
    },
    "summary": "Sala din coltul stanga sus al etajului.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "278",
    "name": "278",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 1",
    "point": "P15",
    "coords": {
      "x": 749.0,
      "y": 1113.0
    },
    "summary": "Sala din dreptul nodului P14.",
    "stairs": [
      "S1",
      "S2",
      "S3",
      "S4",
      "S5",
      "S6",
      "S7",
      "S8"
    ]
  },
  {
    "id": "301",
    "name": "301",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P1",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1115.0,
      "y": 3697.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "302",
    "name": "302",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P1",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1115.0,
      "y": 3697.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "303",
    "name": "303",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "p1",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1023.0,
      "y": 3645.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "305",
    "name": "305",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P2",
    "coords": {
      "x": 707.0,
      "y": 3730.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "307",
    "name": "307",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P2",
    "coords": {
      "x": 662.0,
      "y": 3681.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "307A",
    "name": "307A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": [
      "P2",
      "P3"
    ],
    "coords": {
      "x": 663.0,
      "y": 3526.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "308",
    "name": "308",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": [
      "P3",
      "P4"
    ],
    "coords": {
      "x": 670.0,
      "y": 3122.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "309",
    "name": "309",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": [
      "P4",
      "P3"
    ],
    "coords": {
      "x": 680.0,
      "y": 2943.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "310",
    "name": "310",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": [
      "P4",
      "P3"
    ],
    "coords": {
      "x": 673.0,
      "y": 2721.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "311",
    "name": "311",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P6",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1331.0,
      "y": 2593.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "312",
    "name": "312",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P6",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1211.0,
      "y": 2629.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "313",
    "name": "313",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P5",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1057.0,
      "y": 2623.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "317",
    "name": "317",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P4",
    "coords": {
      "x": 681.0,
      "y": 2451.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "319",
    "name": "319",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P4",
    "floor_id": "etaj-2",
    "coords": {
      "x": 681.0,
      "y": 2269.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "320",
    "name": "320",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": [
      "P4",
      "P7"
    ],
    "coords": {
      "x": 678.0,
      "y": 2152.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "320",
    "name": "320",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P4",
    "floor_id": "etaj-2",
    "coords": {
      "x": 679.0,
      "y": 2161.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "321",
    "name": "321",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P7",
    "coords": {
      "x": 685.0,
      "y": 1729.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "321",
    "name": "321",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P7",
    "floor_id": "etaj-2",
    "coords": {
      "x": 687.0,
      "y": 1729.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "322",
    "name": "322",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P89",
    "coords": {
      "x": 749.0,
      "y": 1684.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "322",
    "name": "322",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P7",
    "floor_id": "etaj-2",
    "coords": {
      "x": 749.0,
      "y": 1673.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "323",
    "name": "323",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P89",
    "coords": {
      "x": 926.0,
      "y": 1688.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "324",
    "name": "324",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P78",
    "coords": {
      "x": 1059.0,
      "y": 1687.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "324A",
    "name": "324A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P78",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1061.0,
      "y": 1691.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "324B",
    "name": "324B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P78",
    "coords": {
      "x": 1538.0,
      "y": 1692.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "325",
    "name": "325",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P8",
    "coords": {
      "x": 1772.0,
      "y": 1700.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "325A",
    "name": "325A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P89",
    "coords": {
      "x": 1900.0,
      "y": 1695.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "328",
    "name": "328",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "points": "P89",
    "coords": {
      "x": 2167.0,
      "y": 1699.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "329A",
    "name": "329A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P11",
    "floor_id": "etaj-2",
    "coords": {
      "x": 1991.0,
      "y": 649.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "329B",
    "name": "329B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P11",
    "floor_id": "etaj-2",
    "coords": {
      "x": 2243.0,
      "y": 611.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "329C",
    "name": "329C",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P11",
    "floor_id": "etaj-2",
    "coords": {
      "x": 2357.0,
      "y": 613.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "334B",
    "name": "334B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 2777.0,
      "y": 1699.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "334D",
    "name": "334D",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 2779.0,
      "y": 1701.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "335",
    "name": "335",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3095.0,
      "y": 1699.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "335",
    "name": "335",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3095.0,
      "y": 1699.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "336",
    "name": "336",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3433.0,
      "y": 1697.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "337",
    "name": "337",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3547.0,
      "y": 1705.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "338",
    "name": "338",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P10",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3599.0,
      "y": 1777.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "340",
    "name": "340",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3609.0,
      "y": 2763.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "341",
    "name": "341",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3603.0,
      "y": 2947.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "342",
    "name": "342",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3605.0,
      "y": 3151.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "343",
    "name": "343",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3465.0,
      "y": 2601.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "344",
    "name": "344",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3465.0,
      "y": 2601.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "345",
    "name": "345",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P17",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3465.0,
      "y": 2601.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "347",
    "name": "347",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3593.0,
      "y": 3505.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "348",
    "name": "348",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3599.0,
      "y": 3687.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "349",
    "name": "349",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3533.0,
      "y": 3753.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "352",
    "name": "352",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3475.0,
      "y": 3693.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "353",
    "name": "353",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3475.0,
      "y": 3693.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "354",
    "name": "354",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P19",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3475.0,
      "y": 3693.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "363",
    "name": "363",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P14",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3573.0,
      "y": 917.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "364",
    "name": "364",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P14",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3637.0,
      "y": 891.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "365",
    "name": "365",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P12-13",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3439.0,
      "y": 651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "366",
    "name": "366",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P12-13",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3257.0,
      "y": 651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "367",
    "name": "367",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "floor_id": "etaj-2",
    "point": "P12-13",
    "coords": {
      "x": 3077.0,
      "y": 649.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": [
      "S5"
    ]
  },
  {
    "id": "367",
    "name": "367",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P12-13",
    "floor_id": "etaj-2",
    "coords": {
      "x": 3081.0,
      "y": 651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "367B",
    "name": "367B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 2",
    "point": "P16",
    "floor_id": "etaj-2",
    "coords": {
      "x": 803.0,
      "y": 693.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "401",
    "name": "401",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P4",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2681.0,
      "y": 3757.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "402",
    "name": "402",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P4",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2835.0,
      "y": 3751.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "403",
    "name": "403",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P4",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3207.0,
      "y": 3737.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "404",
    "name": "404",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P4",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3207.0,
      "y": 3737.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "406",
    "name": "406",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P5",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3587.0,
      "y": 3805.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "407",
    "name": "407",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P5",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3581.0,
      "y": 3675.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "408",
    "name": "408",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P5",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3595.0,
      "y": 3489.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "409",
    "name": "409",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P6-7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3573.0,
      "y": 3115.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "410",
    "name": "410",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P6-7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3579.0,
      "y": 2911.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "411",
    "name": "411",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P6-7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3583.0,
      "y": 2677.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "412",
    "name": "412",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P6-7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3581.0,
      "y": 2537.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "413",
    "name": "413",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P6-7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3587.0,
      "y": 2413.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "414",
    "name": "414",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P7",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3509.0,
      "y": 2299.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "416",
    "name": "416",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P9",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2845.0,
      "y": 2531.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "418",
    "name": "418",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P9",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2423.0,
      "y": 2517.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "419",
    "name": "419",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P10",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2839.0,
      "y": 2527.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "420",
    "name": "420",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P10",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1469.0,
      "y": 2531.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "421",
    "name": "421",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P8",
    "floor_id": "etaj-3",
    "coords": {
      "x": 947.0,
      "y": 2527.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "421",
    "name": "421",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P10",
    "floor_id": "etaj-3",
    "coords": {
      "x": 947.0,
      "y": 2527.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "424",
    "name": "424",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P1-11",
    "floor_id": "etaj-3",
    "coords": {
      "x": 535.0,
      "y": 2475.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "425",
    "name": "425",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P1-11",
    "floor_id": "etaj-3",
    "coords": {
      "x": 535.0,
      "y": 2585.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "426",
    "name": "426",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P1-11",
    "floor_id": "etaj-3",
    "coords": {
      "x": 533.0,
      "y": 2733.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "427",
    "name": "427",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P1-11",
    "floor_id": "etaj-3",
    "coords": {
      "x": 535.0,
      "y": 2963.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "428",
    "name": "428",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P1-11",
    "floor_id": "etaj-3",
    "coords": {
      "x": 537.0,
      "y": 3159.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "429",
    "name": "429",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P2",
    "floor_id": "etaj-3",
    "coords": {
      "x": 549.0,
      "y": 3557.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "430",
    "name": "430",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P2",
    "floor_id": "etaj-3",
    "coords": {
      "x": 545.0,
      "y": 3707.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "431",
    "name": "431",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P2",
    "floor_id": "etaj-3",
    "coords": {
      "x": 549.0,
      "y": 3829.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "433",
    "name": "433",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P3",
    "floor_id": "etaj-3",
    "coords": {
      "x": 947.0,
      "y": 3753.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "434",
    "name": "434",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P3",
    "floor_id": "etaj-3",
    "coords": {
      "x": 947.0,
      "y": 3753.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "435",
    "name": "435",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P3",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1303.0,
      "y": 3757.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "436",
    "name": "436",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P3",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1735.0,
      "y": 3763.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "437",
    "name": "437",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P9-15",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2427.0,
      "y": 2259.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "438",
    "name": "438",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P9-15",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2423.0,
      "y": 2069.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "439",
    "name": "439",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P10-13",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1707.0,
      "y": 2265.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "440",
    "name": "440",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P10-13",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1687.0,
      "y": 2075.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "443A",
    "name": "443A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2491.0,
      "y": 1667.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "443B",
    "name": "443B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2977.0,
      "y": 1651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "443C",
    "name": "443C",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3135.0,
      "y": 1655.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "443D",
    "name": "443D",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3425.0,
      "y": 1719.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "444",
    "name": "444",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2079.0,
      "y": 1661.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "445",
    "name": "445",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1925.0,
      "y": 1663.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "446",
    "name": "446",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1791.0,
      "y": 1657.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "447",
    "name": "447",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1667.0,
      "y": 1661.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "448",
    "name": "448",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1477.0,
      "y": 1657.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "449",
    "name": "449",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1319.0,
      "y": 1671.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "450",
    "name": "450",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1155.0,
      "y": 1659.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "451",
    "name": "451",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 969.0,
      "y": 1663.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "452",
    "name": "452",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 801.0,
      "y": 1667.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "453",
    "name": "453",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P14",
    "floor_id": "etaj-3",
    "coords": {
      "x": 641.0,
      "y": 1665.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "454",
    "name": "454",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P11-12",
    "floor_id": "etaj-3",
    "coords": {
      "x": 543.0,
      "y": 1743.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "455",
    "name": "455",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P11-12",
    "floor_id": "etaj-3",
    "coords": {
      "x": 555.0,
      "y": 1821.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "456",
    "name": "456",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P11-12",
    "floor_id": "etaj-3",
    "coords": {
      "x": 557.0,
      "y": 1975.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "457",
    "name": "457",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P11-12",
    "floor_id": "etaj-3",
    "coords": {
      "x": 553.0,
      "y": 2155.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "463",
    "name": "463",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3479.0,
      "y": 701.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "463A",
    "name": "463A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3537.0,
      "y": 625.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "463B",
    "name": "463B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3537.0,
      "y": 625.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "464A",
    "name": "464A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3453.0,
      "y": 581.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "464B",
    "name": "464B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 3347.0,
      "y": 587.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "465",
    "name": "465",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P18",
    "floor_id": "etaj-3",
    "coords": {
      "x": 2823.0,
      "y": 577.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "467A",
    "name": "467A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P20",
    "floor_id": "etaj-3",
    "coords": {
      "x": 1273.0,
      "y": 593.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "467B",
    "name": "467B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P20",
    "floor_id": "etaj-3",
    "coords": {
      "x": 677.0,
      "y": 651.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "467C",
    "name": "467C",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P20",
    "floor_id": "etaj-3",
    "coords": {
      "x": 675.0,
      "y": 653.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "467D",
    "name": "467D",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 3",
    "point": "P20",
    "floor_id": "etaj-3",
    "coords": {
      "x": 685.0,
      "y": 647.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "502",
    "name": "502",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P5",
    "floor_id": "etaj-4",
    "coords": {
      "x": 3501.0,
      "y": 615.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "503",
    "name": "503",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P5",
    "floor_id": "etaj-4",
    "coords": {
      "x": 3403.0,
      "y": 561.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "504",
    "name": "504",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P5",
    "floor_id": "etaj-4",
    "coords": {
      "x": 3215.0,
      "y": 559.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "505",
    "name": "505",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P5",
    "floor_id": "etaj-4",
    "coords": {
      "x": 3033.0,
      "y": 565.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "506",
    "name": "506",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P5",
    "floor_id": "etaj-4",
    "coords": {
      "x": 2879.0,
      "y": 565.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "507",
    "name": "507",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P2",
    "floor_id": "etaj-4",
    "coords": {
      "x": 1413.0,
      "y": 547.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "508A",
    "name": "508A",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P2",
    "floor_id": "etaj-4",
    "coords": {
      "x": 1051.0,
      "y": 537.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "508B",
    "name": "508B",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P2",
    "floor_id": "etaj-4",
    "coords": {
      "x": 729.0,
      "y": 529.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "511",
    "name": "511",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P3",
    "floor_id": "etaj-4",
    "coords": {
      "x": 641.0,
      "y": 653.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "CM4",
    "name": "CM4",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P2",
    "floor_id": "etaj-4",
    "coords": {
      "x": 571.0,
      "y": 527.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "CM6",
    "name": "CM6",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P3",
    "floor_id": "etaj-4",
    "coords": {
      "x": 655.0,
      "y": 839.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  },
  {
    "id": "CM7",
    "name": "CM7",
    "building_label": "Facultatea de Horticultura",
    "floor": "Etajul 4",
    "point": "P3",
    "floor_id": "etaj-4",
    "coords": {
      "x": 679.0,
      "y": 1133.0
    },
    "summary": "Sala de pe coloana stanga inferioara.",
    "stairs": []
  }
]

def normalize_point_list(raw_points):
    point_aliases = {
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
        "P1213": "P12-13",
        "P12-P13": "P12-13",
    }

    def normalize_point_id(point_id):
        cleaned_point = str(point_id).strip()
        if not cleaned_point:
            return ""
        return point_aliases.get(cleaned_point, cleaned_point)

    if raw_points is None:
        return []

    if isinstance(raw_points, list):
        return [normalize_point_id(point_id) for point_id in raw_points if normalize_point_id(point_id)]

    if isinstance(raw_points, str):
        cleaned = raw_points.strip()
        if not cleaned:
            return []

        try:
            parsed = ast.literal_eval(cleaned)
        except (ValueError, SyntaxError):
            parsed = None

        if isinstance(parsed, list):
            return [normalize_point_id(point_id) for point_id in parsed if normalize_point_id(point_id)]

        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1]

        return [
            normalize_point_id(token.strip().strip("'\""))
            for token in cleaned.split(",")
            if normalize_point_id(token.strip().strip("'\""))
        ]

    normalized_point = normalize_point_id(raw_points)
    return [normalized_point] if normalized_point else []


def normalize_stair_list(raw_stairs):
    return normalize_point_list(raw_stairs)


def deduplicate_rooms(rooms):
    merged = {}
    ordered_keys = []

    for room in rooms:
        floor_id = room.get("floor_id", DEFAULT_FLOOR_ID)
        key = (room["id"].lower(), floor_id)
        if key not in merged:
            merged[key] = dict(room)
            ordered_keys.append(key)
            continue

        previous = merged[key]
        replacement = dict(room)
        previous_stairs = normalize_stair_list(previous.get("stairs"))
        replacement_stairs = normalize_stair_list(replacement.get("stairs"))
        if previous_stairs and not replacement_stairs:
            replacement["stairs"] = previous_stairs
        merged[key] = replacement

    return [merged[key] for key in ordered_keys]


ROOMS = deduplicate_rooms(ROOMS)


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
        "stairs": normalize_stair_list(room.get("stairs")),
    }
    NORMALIZED_ROOMS.append(cleaned_room)

ETAJE = {
    DEFAULT_FLOOR_ID: {
        "id": DEFAULT_FLOOR_ID,
        "level": 1,
        "label_ro": "Etajul 1",
        "label_en": "1st floor",
        "image_path": Path(__file__).with_name("etaj-0-bun.png"),
        "image_url": "/etaj-0-bun.png",
        "width": MAP_WIDTH,
        "height": MAP_HEIGHT,
        "points": POINTS,
        "graph": GRAPH,
        "stairs": {
            "S1": {"points": ["P21"], "coords": {"x": 701.0, "y": 3241.0}},
            "S2": {"points": ["P22"], "coords": {"x": 3974.0, "y": 3130.0}},
            "S3": {"points": ["P4"], "coords": {"x": 2297.0, "y": 2240.0}},
            "S4": {"points": ["P20"], "coords": {"x": 3600.0, "y": 570.0}},
            "S5": {"points": ["P19"], "coords": {"x": 2893.0, "y": 430.0}},
            "S6": {"points": ["P18"], "coords": {"x": 1650.0, "y": 430.0}},
            "S7": {"points": ["P14"], "coords": {"x": 1900.0, "y": 1700.0}},
            "S8": {"points": ["P12"], "coords": {"x": 2600.0, "y": 1700.0}},
        },
    },
    
    "etaj-2": {
        "id": "etaj-2",
        "level": 2,
        "label_ro": "Etajul 2",
        "label_en": "2nd floor",
        "image_path": Path(__file__).with_name("etaj-2-clean.png"),
        "image_url": "/etaj-2-clean.png",
        "width": 4409,
        "height": 4416,
        "points": POINTS_ETAJ_2,
        "graph": GRAPH_ETAJ_2,
        "stairs": {
            "S1": {"points": ["P3"], "coords": {"x": 585.0, "y": 3301.0}},
            "S2": {"points": ["P18"], "coords": {"x": 3664.0, "y": 3320.0}},
            "S4": {"points": ["P13"], "coords": {"x": 3420.0, "y": 835.0}},
            "S5": {"points": ["P12"], "coords": {"x": 2893.0, "y": 430.0}},
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
        "image_path": Path(__file__).with_name("etaj 0- original.png"),
        "image_url": "/etaj 0- original.png",
        "width": 4754,
        "height": 4480,
        "points": POINTS_ETAJ_0,
        "graph": GRAPH_ETAJ_0,
        "stairs": {
            "S1": {"points": ["P1"], "coords": {"x": 1075.0, "y": 3301.0}},
            "S2": {"points": ["P6"], "coords": {"x": 4134.0, "y": 3320.0}},
            "S4": {"points": ["P17"], "coords": {"x": 3900.0, "y": 872.0}},
            "S5": {"points": ["P16"], "coords": {"x": 3223.0, "y": 710.0}},
            "S6": {"points": ["P18"], "coords": {"x": 2020.0, "y": 668.0}},
            "S7": {"points": ["P13"], "coords": {"x": 2300.0, "y": 1920.0}},
            "S8": {"points": ["P11"], "coords": {"x": 2920.0, "y": 1920.0}},
        },
    },
    "etaj-3": {
        "id": "etaj-3",
        "level": 3,
        "label_ro": "Etajul 3",
        "label_en": "Third floor",
        "image_path": Path(__file__).with_name("etaj 3 bun.png"),
        "image_url": "/etaj 3 bun.png",
        "width": 4306,
        "height": 4412,
        "points": POINTS_ETAJ_3,
        "graph": GRAPH_ETAJ_3,
        "stairs": {
            "S1": {"points": ["P1"], "coords": {"x": 463, "y": 3321}},
            "S2": {"points": ["P6"], "coords": {"x": 3690.0, "y": 3330.0}},
            "S3": {"points" : ["P8"], "coords" : {"x" :2060, "y":1920}},
            "S4": {"points": ["P18"], "coords": {"x": 3450.0, "y": 641.0}},
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
        "image_path": Path(__file__).with_name("etaj final.png"),
        "image_url": "/etaj final.png",
        "width": 4409,
        "height": 4304,
        "points": POINTS_ETAJ_4,
        "graph": GRAPH_ETAJ_4,
        "stairs": {
            "S5": {"points": ["P4"], "coords": {"x": 2710.0, "y": 559.0}},
            "S6": {"points": ["P1"], "coords": {"x": 1560.0, "y": 523.0}},
            
        },
    }
}

FLOOR_CONFIGS = ETAJE


def build_stair_shafts(etaje):
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

ROOM_POINT_OVERRIDES = {

}


def choose_primary_room_point(room, candidate_points):
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
        "NORMALIZED_ROOMS": "C101, C205, Aula Magna",
        "class_name": "building building--central",
    },
    {
        "id": "facultatea-de-stiinte",
        "name": "Facultatea de Stiinte",
        "NORMALIZED_ROOMS": "S12, S24, Laborator Info 2",
        "class_name": "building building--stiinte",
    },
    {
        "id": "electrotehnica",
        "name": "Electrotehnica",
        "NORMALIZED_ROOMS": "E08, E14, Amfiteatrul E1",
        "class_name": "building building--electro",
    },
]

STYLES_PATH = Path(__file__).with_name("styles.css")
FLOOR_PLAN_PATH = Path(__file__).with_name("etaj-0-bun.png")

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
        "target_label": "Destinatie",
        "submit": "Arata traseul",
        "quick_rooms": "Sugestii sali",
        "map_tag": "Harta campus",
        "map_title": "Traseu real pe etaj",
        "live_pill": "Python app",
        "route_tag": "Ghidare",
        "trace_tag": "Traseu complet",
        "rooms_tag": "Sali populare",
        "rooms_title": "Destinatii rapide",
        "next_floor": "Urca un etaj",
        "previous_floor": "Coboara un etaj",
        "level_tag": "Nivel",
        "level_summary": "Pleci de la nivelul {start} si ajungi la nivelul {target}.",
        "shown_floor": "Afisezi acum: {floor}",
        "default_summary": "Introdu numele unei sali pentru a vedea traseul recomandat.",
        "default_title": "Alege o sala",
        "not_found_title": "Sala nu a fost gasita",
        "not_found_summary": "Incearca una dintre salile sugerate, de exemplu 207, 231 sau 277.",
        "from_prefix": "Pleci din {start}.",
        "to_prefix": "Mergi catre {building}.",
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
        "hero_stat_2": "NORMALIZED_ROOMS included",
        "hero_stat_3": "server-side",
        "planner_label": "Route planner",
        "planner_title": "Where do you want to go?",
        "start_label": "Starting point",
        "target_label": "Destination",
        "submit": "Show route",
        "quick_rooms": "Suggested NORMALIZED_ROOMS",
        "map_tag": "Campus map",
        "map_title": "Real route across the floor",
        "live_pill": "Python app",
        "route_tag": "Directions",
        "trace_tag": "Full route",
        "rooms_tag": "Popular NORMALIZED_ROOMS",
        "rooms_title": "Quick destinations",
        "next_floor": "Go up one floor",
        "previous_floor": "Go down one floor",
        "level_tag": "Level",
        "level_summary": "You start from level {start} and arrive at level {target}.",
        "shown_floor": "Currently showing: {floor}",
        "default_summary": "Enter a room name to see the recommended route.",
        "default_title": "Choose a room",
        "not_found_title": "Room not found",
        "not_found_summary": "Try one of the suggested NORMALIZED_ROOMS, for example 207, 231 or 277.",
        "from_prefix": "You start from {start}.",
        "to_prefix": "Head towards {building}.",
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

START_POINT_LABELS = {
    "intrare-principala": {"ro": "Intrare Principala", "en": "Main Entrance"},
    "intrare-teatru": {"ro": "Intrare Teatru", "en": "Theatre Entrance"},
    "intrare-parcare": {"ro": "Intrare Parcare", "en": "Parking Entrance"},
}

BUILDING_LABELS = {
    "Facultatea de Horticultura": {"ro": "Facultatea de Horticultura", "en": "Faculty of Horticulture"},
}

DEFAULT_BUILDING_LABEL = "Facultatea de Horticultura"

FLOOR_LABELS = {
    "Parter": {"ro": "Parter", "en": "Ground floor"},
    "Etajul 0": {"ro": "Etajul 0", "en": "Ground floor"},
    "Etajul 1": {"ro": "Etajul 1", "en": "1st floor"},
    "Etajul 2": {"ro": "Etajul 2", "en": "2nd floor"},
}


def get_room(query: str):
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


def resolve_target_option(selected_target, lang):
    selected_target = (selected_target or "").strip()
    if not selected_target:
        return None

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
            "building_label": room_building_label(room, lang),
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
                "building_label": room_building_label(room, lang),
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


def node_distance(node_a, node_b, combined_points):
    floor_a, _ = split_node_key(node_a)
    floor_b, _ = split_node_key(node_b)
    if floor_a != floor_b:
        return STAIR_TRAVEL_COST
    return distance(combined_points[node_a], combined_points[node_b])


def find_transition_stair(node_a, node_b):
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


def room_has_point(room, point_id):
    return point_id in room_target_points(room)


def resolve_start_option(selected_start, lang):
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
    floor_width = get_floor_width(floor_id)
    floor_height = get_floor_height(floor_id)
    return {
        "x": min(max(coords["x"], padding), floor_width - padding),
        "y": min(max(coords["y"], padding), floor_height - padding),
    }


def build_route_segments(point_ids, floor_id, final_coords=None, start_coords=None):
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


def find_path(start_point_id, destination_point_id, floor_id=DEFAULT_FLOOR_ID):
    floor_points = get_floor_points(floor_id)
    floor_graph = get_floor_graph(floor_id)
    if start_point_id == destination_point_id:
        return [start_point_id]

    frontier = [(0, start_point_id, [start_point_id])]
    best_cost = {start_point_id: 0}

    while frontier:
        frontier.sort(key=lambda item: item[0])
        cost, current, path = frontier.pop(0)
        if current == destination_point_id:
            return path

        for neighbor in floor_graph.get(current, []):
            new_cost = cost + distance(floor_points[current], floor_points[neighbor])
            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                frontier.append((new_cost, neighbor, path + [neighbor]))

    return []


def find_best_target_path(start_point_ids, target_point_ids, start_floor_id=DEFAULT_FLOOR_ID, target_floor_id=DEFAULT_FLOOR_ID):
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


def find_best_room_path(start_point_ids, room, start_floor_id=DEFAULT_FLOOR_ID):
    return find_best_target_path(
        start_point_ids,
        room_target_points(room),
        start_floor_id,
        room_floor_id(room),
    )


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


def translate_building_label(label, lang):
    return BUILDING_LABELS.get(label, {}).get(lang, label)


def room_building_label(room, lang):
    return translate_building_label(room.get("building_label", DEFAULT_BUILDING_LABEL), lang)


def room_summary_text(room, lang):
    stairs = room.get("stairs", [])
    if not stairs:
        return ""
    if lang == "ro":
        return f"Scari recomandate: {', '.join(stairs)}."
    return f"Recommended stairs: {', '.join(stairs)}."


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


def route_floor_sequence(route_node_ids):
    sequence = []
    for node_id in route_node_ids:
        floor_id, _ = split_node_key(node_id)
        if not sequence or sequence[-1] != floor_id:
            sequence.append(floor_id)
    return sequence


def route_floor_stages(route_node_ids):
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


def route_segment_for_floor(route_node_ids, floor_id):
    segment = []
    entry_stair_coords = None
    exit_stair_coords = None
    in_segment = False
    for index, node_id in enumerate(route_node_ids):
        node_floor_id, point_id = split_node_key(node_id)
        if node_floor_id == floor_id:
            if not in_segment and index > 0:
                stair_id = find_transition_stair(route_node_ids[index - 1], node_id)
                if stair_id:
                    entry_stair_coords = get_stair_coords(stair_id, floor_id)
            segment.append(point_id)
            in_segment = True
        elif in_segment:
            stair_id = find_transition_stair(route_node_ids[index - 1], node_id)
            if stair_id:
                exit_stair_coords = get_stair_coords(stair_id, floor_id)
            break
    return segment, entry_stair_coords, exit_stair_coords


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


def render_route_debug(route_point_ids, target_point_id=None):
    if not route_point_ids:
        return ""
    debug = " -> ".join(route_point_ids)
    if target_point_id:
        debug += f" | target: {target_point_id}"
    return debug


def describe_route_nodes_and_stairs(route_node_ids, lang="ro"):
    if not route_node_ids:
        return []

    descriptions = []
    previous_node = None

    for node_id in route_node_ids:
        floor_id, point_id = split_node_key(node_id)
        floor_label = translate_floor_label(get_floor_config(floor_id)["label_ro"], lang)

        if previous_node is not None:
            stair_id = find_transition_stair(previous_node, node_id)
            if stair_id:
                if lang == "en":
                    descriptions.append(f"Stair {stair_id}: {point_label(previous_node, lang)} -> {point_label(node_id, lang)}")
                else:
                    descriptions.append(f"Scara {stair_id}: {point_label(previous_node, lang)} -> {point_label(node_id, lang)}")

        descriptions.append(f"{floor_label}: {point_id}")
        previous_node = node_id

    return descriptions


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
    chips = []
    for room in NORMALIZED_ROOMS[:5]:
        chips.append(
            f'<a class="chip" href="/?lang={escape(lang)}&start={escape(selected_start)}&target={escape(room["name"])}">{escape(room["name"])}</a>'
        )
    return "".join(chips)


def render_room_grid(selected_start, lang):
    cards = []
    for room in NORMALIZED_ROOMS:
        cards.append(
            """
            <a class="room-card" href="/?lang={lang}&start={start}&target={room_name}">
              <strong>{name}</strong>
              <span>{building} - {floor}</span>
            </a>
            """.format(
                lang=escape(lang),
                start=escape(selected_start),
                room_name=escape(room["name"]),
                name=escape(room["name"]),
                building=escape(room_building_label(room, lang)),
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
            f'<article class="{building["class_name"]}{active}"><span>{escape(building["name"])}</span><small>{escape(building["NORMALIZED_ROOMS"])}</small></article>'
        )
    return "".join(blocks)


def render_route_lines(segments, floor_id=DEFAULT_FLOOR_ID):
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
    floor_points = get_floor_points(floor_id)
    if point_id not in floor_points:
        return ""

    coords = floor_points[point_id]
    label = "Te afli aici / You are here"
    return """
    <div class="you-are-here" style="left: {x}px; top: {y}px;">
      <div class="you-are-here__arrow"></div>
      <div class="you-are-here__label">{label}</div>
    </div>
    """.format(
        x=round(coords["x"], 1),
        y=round(coords["y"], 1),
        label=escape(label),
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
    text = t(lang)
    target_option = resolve_target_option(target_query, lang)
    room = target_option.get("room") if target_option and target_option["type"] == "room" else None
    start_option = resolve_start_option(selected_start, lang)
    active_floor_id = target_option["floor_id"] if target_option else start_option.get("floor_id", DEFAULT_FLOOR_ID)
    floor_config = get_floor_config(active_floor_id)
    selected_start = start_option["id"]
    start_label = start_option["label"]
    summary = text["default_summary"]
    steps = ""
    title = text["default_title"]
    route_lines = ""
    floor_nav = ""
    level_summary = ""
    route_trace = ""
    route_debug = ""
    floor_nav = ""
    start_marker_point_id = start_option["points"][0] if start_option["points"] else None

    if target_option:
        floor_label = translate_floor_label(target_option.get("floor", get_floor_config(target_option["floor_id"])["label_ro"]), lang)
        full_steps = [
            text["from_prefix"].format(start=start_label),
            text["to_prefix"].format(building=target_option["building_label"]) if target_option["type"] == "room"
            else text["to_entrance_prefix"].format(target=target_option["label"]),
        ]
        route_node_ids, target_node_id = find_best_target_path(
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
        if target_option["type"] == "room":
            room_summary = room_summary_text(room, lang)
            summary = f"{room['name']} - {target_option['building_label']} - {floor_label}."
            if room_summary:
                summary = f"{summary} {room_summary}"
        else:
            summary = f"{target_option['label']} - {floor_label}."
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
        route_debug = render_route_debug(route_node_ids, target_node_id)
        route_descriptions = describe_route_nodes_and_stairs(route_node_ids, lang)
        route_trace = render_steps(route_descriptions)
        shown_floor_label = translate_floor_label(floor_config["label_ro"], lang)
        summary = f'{summary} {text["shown_floor"].format(floor=shown_floor_label)}'
        start_level = get_floor_level(start_option.get("floor_id", DEFAULT_FLOOR_ID))
        target_level = get_floor_level(target_option["floor_id"])
        level_summary = text["level_summary"].format(start=start_level, target=target_level)
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
        summary = text["not_found_summary"]

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

          <button type="submit" class="cta">{text["submit"]}</button>
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
          <img class="floor-plan" src="{escape(floor_config['image_url'])}" alt="Harta {escape(floor_config['label_ro'])}">
          <div class="map-route">{route_lines}</div>
          {start_marker}
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
          <div class="level-summary"><strong>{text["level_tag"]}:</strong> {escape(level_summary)}</div>
          <ol class="steps">{steps}</ol>
          <div class="trace-block">
            <p class="section-tag">{text["trace_tag"]}</p>
            <ol class="steps steps--trace">{route_trace}</ol>
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

    for floor_config in FLOOR_CONFIGS.values():
        if path == floor_config["image_url"]:
            image = floor_config["image_path"].read_bytes()
            content_type = "image/tiff" if floor_config["image_path"].suffix.lower() in {".tif", ".tiff"} else "image/png"
            start_response("200 OK", [("Content-Type", content_type)])
            return [image]

    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Pagina nu a fost gasita."]

    params = parse_qs(environ.get("QUERY_STRING", ""))
    lang = params.get("lang", [""])[0]
    selected_start = params.get("start", ["intrare-principala"])[0]
    target_query = params.get("target", [""])[0] or params.get("room", [""])[0]
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
