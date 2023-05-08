import requests
import numpy as np
from matplotlib import pyplot as plt

from src.utils.image.my_image import MyImage


def download_image_from_url(image_url: str) -> MyImage | None:
    try:
        resp = requests.get(url=image_url, stream=True).raw
        image_bytes = bytearray(resp.read())
        image = MyImage(image_bytes=image_bytes, url=image_url)
    except Exception:
        image = None
    return image


def rgb_to_hex(rgb):
    rgb = tuple(map(int, rgb))
    return "#%02x%02x%02x" % rgb


def plot_color_palette(rgbs: np.array):
    rgbs = np.array(list(rgbs)).astype(np.uint8)
    fig = plt.figure(figsize=(20, 10))
    for i, rgb in enumerate(rgbs):
        fig.add_subplot(len(rgbs) // 10 + 1, 10, i + 1)
        plt.imshow(np.array([[rgb]]), vmin=0, vmax=255)
        plt.axis("off")
    plt.show()


def plot_list_of_images(images: list[MyImage], n_images_per_row: int = 2):
    n = len(images)
    fig = plt.figure(figsize=(15, 10 * len(images)))
    for i, image in enumerate(images):
        fig.add_subplot(n // n_images_per_row + 1, n_images_per_row, i + 1)
        image.plot()
        plt.title(image.name)
        plt.axis("off")
    plt.show()
