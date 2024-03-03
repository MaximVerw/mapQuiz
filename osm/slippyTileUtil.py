import math

def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def tile_to_latlon(x, y, zoom):
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def coordToPixel(latitude, longitude, bbox, screen_width, screen_height, offset_x, offset_y):
    minx, miny, maxx, maxy = bbox

    # Calculate the range of longitude and latitude in the bbox
    lon_range = maxx - minx
    lat_range = maxy - miny

    # Calculate the ratio of screen width and height to the longitude and latitude range
    lon_to_pixel = screen_width / lon_range
    lat_to_pixel = screen_height / lat_range

    # Convert latitude and longitude to pixel coordinates
    pixel_x = round((longitude - minx) * lon_to_pixel)
    pixel_y = round(screen_height-((latitude - miny) * lat_to_pixel))  # Invert y-axis for screen coordinates

    return pixel_x+offset_x, pixel_y+offset_y
