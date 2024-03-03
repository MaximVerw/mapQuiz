import os

import requests
from PIL import Image
import io

def get_osm_tile_image(x, y, zoom):
    base_url = "https://a.tile.openstreetmap.org/{}/{}/{}.png"
    url = base_url.format(zoom, x, y)

    headers = {'User-Agent': 'MyOSMQuiz/1.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    else:
        print("Failed to fetch tile image. Status code:", response.status_code)
        print("Response message:", response.text)
        return None

def getImage(x_tile, y_tile, zoom_level):
    # x_tile, y_tile = latlon_to_tile(latitude, longitude, zoom_level)
    folder_path = f"resources/images/{zoom_level}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create the directory if it doesn't exist

    image_path = f"{folder_path}/{x_tile}-{y_tile}-base.jpg"

    # Check if the image file already exists
    if os.path.exists(image_path):
        return None

    tile_image = get_osm_tile_image(x_tile, y_tile, zoom_level)
    if tile_image:
        print(f"Image {zoom_level}-{x_tile}-{y_tile} fetched")
        tile_image.save(image_path, "JPEG")
        return image_path
    else:
        print("Failed to fetch tile image")
        raise ValueError("")
