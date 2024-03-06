import json
from shapely.geometry import LineString

def extract_highway_ways():
    with open("resources/export.json", 'r', encoding="utf-8") as f:
        data = json.load(f)

    highway_ways = []

    for element in data['elements']:
        if element['type'] == 'way' and 'tags' in element:
            tags = element['tags']
            if 'bridge:name' in tags:
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    poly = LineString(coords).buffer(0.0001)
                    exterior_coords = list(poly.exterior.coords)
                    exterior_coords.append(exterior_coords[0])
                    name = element["tags"]["bridge:name"].lower()
                    geometry = LineString(exterior_coords)
                    highway_ways.append({'name':name, 'highway_type': 'bridge', 'geometry': geometry})
            if 'highway' in tags:
                highway_type = tags['highway']
                if 'geometry' in element:
                    if not (element.get("tags") and element["tags"].get("name")):
                        continue
                    name = element["tags"]["name"].lower()
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    geometry = LineString(coords)
                    highway_ways.append({'name':name, 'highway_type': highway_type, 'geometry': geometry})

    return highway_ways
