# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QMainWindow, QCheckBox
from shapely import wkt

from osm.read_osm_export import extract_highway_ways
from app import App


class SelectionDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MapQuiz")
        self.layout = QVBoxLayout()

        self.diff1_button = QPushButton("Gent")
        self.diff1_button.setMinimumWidth(200)
        self.diff1_button.clicked.connect(self.diff1_selected)
        self.layout.addWidget(self.diff1_button)

        self.diff2_button = QPushButton("De Ring")
        self.diff2_button.clicked.connect(self.diff2_selected)
        self.layout.addWidget(self.diff2_button)

        self.diff3_button = QPushButton("Centrum")
        self.diff3_button.clicked.connect(self.diff3_selected)
        self.layout.addWidget(self.diff3_button)

        self.diff4_button = QPushButton("Coupure rechts")
        self.diff4_button.clicked.connect(self.diff4_selected)
        self.layout.addWidget(self.diff4_button)

        self.checkbox = QCheckBox("Easy mode")
        self.layout.addWidget(self.checkbox)

        self.setLayout(self.layout)

    def diff1_selected(self):
        self.hide()
        self.launch_app(1)

    def diff2_selected(self):
        self.launch_app(2)

    def diff3_selected(self):
        self.hide()
        self.launch_app(3)

    def diff4_selected(self):
        self.hide()
        self.launch_app(4)


    def launch_app(self, option):
        area_of_interest_wkt = "POLYGON((3.7222950801877976 51.03880203056653,3.7269208910099856 51.03753412626381,3.7384261127985057 51.038056208707985,3.7474405133750768 51.0473781190764,3.7396122181375278 51.05871103490438,3.7334444703746104 51.06929585854803,3.697149647000517 51.066761684528586,3.6905074571019907 51.05990381208136,3.698098531271736 51.051628287521766,3.7139923428146386 51.04379872734566,3.7222950801877976 51.03880203056653))"

        allowed_highway_types = {'bridge',"trunk", "trunk_link", "motorway", "motorway_link", "primary", "primary_link",
                                 "secondary", "tertiary_link", "residential", "tertiary",'tertiary_link', "unclassified", 'living_street', 'pedestrian','service', 'construction'}
        ways = extract_highway_ways()
        # {'rest_area', 'steps', 'pedestrian', 'living_street', 'path', 'tertiary', 'platform', 'trunk', 'footway',
        #  'tertiary_link', 'cycleway', 'secondary', 'residential', 'trunk_link', 'proposed', 'construction', 'track',
        #  'unclassified', 'service', 'motorway', 'primary', 'primary_link', 'motorway_link'}
        if option == 1:
            pass
        elif option == 2:
            allowed_highway_types = {"trunk", "trunk_link", "motorway", "motorway_link", "primary", "primary_link",
                                     "secondary"}
        elif option == 3:
            area_of_interest_wkt = 'POLYGON((3.719966411590576 51.049137486412775,3.7200307846069336 51.05044594403137,3.720717430114746 51.05194320584977,3.720438480377197 51.0547352675035,3.720910549163818 51.05585474252803,3.7226915359497066 51.05678536983842,3.724150657653809 51.057473212785624,3.7248587608337402 51.05820150594522,3.7254810333251958 51.058929787649305,3.725674152374268 51.05976594881227,3.726575374603272 51.06068301143367,3.727219104766846 51.060858330160585,3.727471232414246 51.06077741390757,3.727755546569825 51.060689754473884,3.72813642024994 51.060416660558786,3.7300837039947514 51.05976594881227,3.730952739715576 51.059310782310035,3.7317252159118652 51.058137443580534,3.7323796749114995 51.057156266814644,3.7333506345748906 51.05623913433655,3.73434841632843 51.05488026127631,3.732857108116149 51.05454980969054,3.7317413091659537 51.0541417998875,3.730759620666503 51.05369669418414,3.73010516166687 51.053288676864355,3.729214668273926 51.05239844477916,3.7284690141677856 51.05172738731224,3.7282222509384155 51.05142051859747,3.7280720472335815 51.050324542302974,3.7286889553070073 51.049899633747486,3.7278628349304204 51.049545540306696,3.725818991661072 51.049491582973246,3.7216293811798082 51.04916109293438,3.719966411590576 51.049137486412775))'
        elif option == 4:
            area_of_interest_wkt = 'POLYGON((3.709816932678223 51.05627285276401,3.70913028717041 51.05678536983842,3.7097525596618652 51.05899722056094,3.7119626998901367 51.06038631669102,3.7125420570373535 51.06077741390757,3.714687824249268 51.060062647530515,3.7153530120849614 51.05983338050609,3.717289566993713 51.0594827346257,3.718346357345581 51.059361356586834,3.7187540531158447 51.05920626196297,3.7193495035171504 51.05860610830618,3.7199020385742183 51.0580126903001,3.720127344131469 51.05727090709715,3.720127344131469 51.05684606227422,3.7206208705902095 51.0559896172102,3.7208139896392813 51.05569289239082,3.720470666885376 51.05470154795643,3.720599412918091 51.05357530097706,3.720728158950805 51.05265809757179,3.720685243606567 51.0518150637144,3.7200736999511723 51.05066851304028,3.7199342250823983 51.04977823058704,3.72009515762329 51.04834160235836,3.7205457687377925 51.04729614065846,3.720417022705078 51.04684422410287,3.717488050460815 51.04672955800686,3.7147200107574454 51.04723543570586,3.712702989578246 51.04875303565336,3.7105786800384513 51.05041222136097,3.7100744247436515 51.051835296706685,3.708904981613159 51.05533547133382,3.7084007263183603 51.05662352295411,3.709816932678223 51.05627285276401))'
        area_of_interest = wkt.loads(area_of_interest_wkt)


        waysByName = {}
        highwayTypes = set()
        waysUsed = set()

        for way in ways:
            highwayTypes.add(way.get("highway_type"))
            if way.get("highway_type") in allowed_highway_types:
                if area_of_interest.intersects(way['geometry']):
                    waysUsed.add(way["name"])

        for way in ways:
            if way["name"] in waysUsed:
                if waysByName.get(way["name"]):
                    waysByName[way["name"]].append(way)
                else:
                    waysByName[way["name"]] = [way]

        print(f'Roads in scope: {len(waysByName.keys())}')
        self.main_app = QMainWindow()
        self.app_window = App(waysByName, area_of_interest, self.checkbox.isChecked())
        self.main_app.setGeometry(self.app_window.geometry())
        self.main_app.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.main_app.setCentralWidget(self.app_window)
        self.main_app.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = SelectionDialog()
    dialog.show()
    sys.exit(app.exec())

