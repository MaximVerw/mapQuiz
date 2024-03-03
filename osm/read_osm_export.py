import json
from shapely.geometry import LineString

def extract_highway_ways():
    with open("resources/export.json", 'r', encoding="utf-8") as f:
        data = json.load(f)

    highway_ways = []

    for element in data['elements']:
        if element['type'] == 'way' and 'tags' in element:
            tags = element['tags']
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
