import sys

from PyQt5.QtWidgets import QApplication
from shapely import Point, LineString, Polygon, wkt

from osm.read_osm_export import extract_highway_ways
from removetext.remove_text import TextRemover
from osm.read_osm import *
from app import App


if __name__ == '__main__':
     #"POLYGON((3.738021415934906 51.05710270160182,3.7382186971692186 51.05613726107964,3.739909679177615 51.056225834443296,3.7397546724935116 51.057155844532275,3.738021415934906 51.05710270160182))"
    area_of_interest_wkt = "POLYGON((3.7222950801877976 51.03880203056653,3.7269208910099856 51.03753412626381,3.7384261127985057 51.038056208707985,3.7474405133750768 51.0473781190764,3.7396122181375278 51.05871103490438,3.7334444703746104 51.06929585854803,3.697149647000517 51.066761684528586,3.6905074571019907 51.05990381208136,3.698098531271736 51.051628287521766,3.7139923428146386 51.04379872734566,3.7222950801877976 51.03880203056653))"
    area_of_interest = wkt.loads(area_of_interest_wkt)

    ways = extract_highway_ways()

    allowed_highway_types = ["primary", "secondary"]
    waysByName = {}

    for way in ways:
        if way.get("highway_type") in allowed_highway_types:
            way_centroid = way['geometry'].centroid
            if area_of_interest.contains(way_centroid):
                if waysByName.get(way["name"]):
                    waysByName[way["name"]].append(way)
                else:
                    waysByName[way["name"]] = [way]

    print(f"quiz size: {waysByName.__sizeof__()} ways")
    app = QApplication(sys.argv)
    window = App(waysByName, list(set([way.get("name") for way in ways if way.get("highway_type") in allowed_highway_types])), area_of_interest)
    window.show()
    sys.exit(app.exec_())