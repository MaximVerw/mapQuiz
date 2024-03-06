import random
import sys

import time

from shapely import GeometryCollection

from osm.read_osm import *
from osm.slippyTileUtil import latlon_to_tile
from removetext.remove_text import TextRemover


class QuizMaster:
    def __init__(self, waysByName, area_in_scope, zoom_levels):
        self.zoom_levels = zoom_levels
        self.tr = TextRemover()
        self.waysByName = waysByName
        self.guessed_streets = set()
        self.current_street = None  # Initialize current street to None
        self.area_in_scope = area_in_scope
        self.relevant_tiles = self.init_images()
        self.guessed_streets_list = []
        self.guessed_streets_with_hint = set()
        self.guessed_streets_with_hints_2 = set()
        self.start_time = time.time()
        self.end_time = self.start_time


    def guess(self, streetNameGuess, hint):
        if streetNameGuess == self.current_street and streetNameGuess in self.waysByName and streetNameGuess not in self.guessed_streets:
            self.guessed_streets.add(streetNameGuess)
            self.guessed_streets_list.append(self.waysByName[streetNameGuess])
            if hint != '':
                if len(hint) == 1:
                    self.guessed_streets_with_hint.add(streetNameGuess)
                else:
                    self.guessed_streets_with_hints_2.add(streetNameGuess)
            return True
        else:
            return False

    def pollNewStreet(self):
        unguessed_streets = [street for street in self.waysByName if street not in self.guessed_streets]
        random.shuffle(unguessed_streets)
        if unguessed_streets:
            if self.current_street:
                oldGeom = GeometryCollection([way['geometry'] for way in self.waysByName[self.current_street]])
                mindist = float(sys.maxsize)
                for unguessed in unguessed_streets:
                    dis = oldGeom.distance(GeometryCollection([way['geometry'] for way in self.waysByName[unguessed]]))
                    if dis < mindist:
                        mindist = dis
                        self.current_street = unguessed
            else:
                if "holstraat" in unguessed_streets:
                    self.current_street = "holstraat"
                else:
                    self.current_street = unguessed_streets[0]  # Set current street to the new street
            return self.current_street
        else:
            self.finish_quiz()

    def finish_quiz(self):
        # Record the ending time
        self.end_time = time.time()
        message = self.getEndMessage()
        print(message)

    def getEndMessage(self):
        # Calculate the time difference
        time_spent_seconds = self.end_time - self.start_time
        # Convert time spent to hours, minutes, and seconds
        hours = int(time_spent_seconds // 3600)
        minutes = int((time_spent_seconds % 3600) // 60)
        seconds = int(time_spent_seconds % 60)
        # Format the time spent
        formatted_time = ""
        if hours > 0:
            formatted_time += f"{hours} hours, "
        if minutes > 0:
            formatted_time += f"{minutes} minutes, "
        formatted_time += f"{seconds} seconds"
        g = len(self.guessed_streets)
        h = len(self.guessed_streets_with_hint)
        h2 = len(self.guessed_streets_with_hints_2)
        message = f"You won! {int(100. * float(g - h - h2) / g)}% correct, time spent: {formatted_time}"
        return message

    def getGuessedGeometries(self):
        # Create a list to store individual geometries
        geometries_with_hint = []
        geometries_with_hints = []
        geometries_without_hint = []
        for streets in self.guessed_streets_list:
            # Iterate through geometryCollections
            for street in streets:
                if street['name'] in self.guessed_streets_with_hint:
                    geometries_with_hint.append(street['geometry'])
                elif street['name'] in self.guessed_streets_with_hints_2:
                    geometries_with_hints.append(street['geometry'])
                else:
                    geometries_without_hint.append(street['geometry'])

        # Create a GeometryCollection from the geometries
        return GeometryCollection(geometries_with_hints), GeometryCollection(geometries_with_hint), GeometryCollection(geometries_without_hint)

    def getGeometry(self):
        if self.current_street is None:
            return None

        ways = self.waysByName[self.current_street]
        if not ways:
            return None

        # Merge all geometries into a single GeometryCollection
        all_geometries = [way['geometry'] for way in ways]

        merged_geometry = GeometryCollection(all_geometries)

        return merged_geometry

    def build_osm_image(self, x_tile, y_tile, zoom_level):
        path = getImage(x_tile, y_tile, zoom_level)
        if path:
            self.tr.process_image(path)

    def init_images(self):
        margin = 4
        relevant_tiles = []
        for zoom_level in self.zoom_levels:
            min_lon, min_lat, max_lon, max_lat = self.area_in_scope.bounds
            min_x_tile, max_y_tile = latlon_to_tile(min_lat, min_lon, zoom_level)
            max_x_tile, min_y_tile = latlon_to_tile(max_lat, max_lon, zoom_level)

            counter = 0
            for x_tile in range(min_x_tile-margin, max_x_tile+2*margin):
                for y_tile in range(min_y_tile-margin, max_y_tile+2*margin):
                    counter += 1

            for x_tile in range(min_x_tile-margin, max_x_tile+2*margin):
                for y_tile in range(min_y_tile-margin, max_y_tile+2*margin):
                    relevant_tiles.append((x_tile, y_tile, zoom_level))
                    self.build_osm_image(x_tile, y_tile, zoom_level)
        return relevant_tiles
