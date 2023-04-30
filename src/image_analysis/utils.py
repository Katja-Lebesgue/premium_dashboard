import colorsys as cs
from collections import Counter
from itertools import product
from typing import Literal

import cv2
import numpy as np
import requests
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors


class MyNN(NearestNeighbors):
    def fit(self, X, y=None):
        self.X = X
        super().fit(X, y)


def rgb_to_hex(rgb):
    rgb = tuple(map(int, rgb))
    return "#%02x%02x%02x" % rgb


def download_image(img_url: str, convert_to_rgb: bool = False):
    try:
        resp = requests.get(url=img_url, stream=True).raw
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if convert_to_rgb:
            image = cv2.cvtColor(np.float32(image), cv2.COLOR_BGR2RGB).astype(np.uint8)
    except Exception:
        image = None

    return image


def plot_image(img, **kwargs):
    plt.imshow(cv2.cvtColor(np.float32(img), cv2.COLOR_BGR2RGB).astype(np.uint8), **kwargs)


def plot_color_palette(rgbs: np.array):
    rgbs = np.array(list(rgbs)).astype(np.uint8)
    fig = plt.figure(figsize=(20, 10))
    for i, rgb in enumerate(rgbs):
        fig.add_subplot(len(rgbs) // 10 + 1, 10, i + 1)
        plot_image(np.array([[rgb]]), vmin=0, vmax=255)
        plt.axis("off")


def shrink_image_without_distortion(img: np.array, n_pixels: int) -> np.array:
    if img is None:
        return None
    hw_ratio = img.shape[0] / img.shape[1]
    new_h = int(np.sqrt(n_pixels * hw_ratio))
    new_w = int(np.sqrt(n_pixels / hw_ratio))
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def train_nn_on_basic_colors(basic_colors: np.array):
    nn = MyNN(n_neighbors=1, algorithm="brute")
    nn.fit(basic_colors)
    return nn


def project_image_onto_basic_colors(img, nn: MyNN, n_pixels: int = 1000, plot: bool = True):
    img = shrink_image_without_distortion(img=img, n_pixels=n_pixels)
    x_shape, y_shape = img.shape[:2]

    X = img.reshape(-1, 3)
    indices = nn.kneighbors(X, return_distance=False)
    colors = [nn.X[idx[0]] for idx in indices]
    projected_image = np.array(colors).reshape(x_shape, y_shape, 3)

    if plot:
        fig = plt.figure(figsize=(10, 10))
        fig.add_subplot(1, 2, 1)
        plot_image(img)
        fig.add_subplot(1, 2, 2)
        plot_image(projected_image)
        plt.show()

    return projected_image


def color_analysis(img, n_clusters: int = 5, n_pixels: int = 1000, rescale: bool = True):
    if img is None:
        return {}
    img = shrink_image_without_distortion(img=img, n_pixels=n_pixels)
    X = img.reshape(-1, 3)
    clf = KMeans(n_clusters=n_clusters, n_init=10)
    color_labels = clf.fit_predict(X)
    center_colors = clf.cluster_centers_
    counts = Counter(color_labels)
    local_centroids_freq = {tuple(center_colors[idx, :]): count for idx, count in dict(counts).items()}
    if rescale:
        acc_n_pixels = sum(local_centroids_freq.values())
        scale_factor = n_pixels / acc_n_pixels
        local_centroids_freq = {col: freq * scale_factor for col, freq in local_centroids_freq.items()}
    return local_centroids_freq


def project_image_onto_its_basic_colors(img, n_colors: int = 5, n_pixels: int = 1000):
    basic_colors_freq = color_analysis(img, n_clusters=n_colors, n_pixels=n_pixels)
    nn = MyNN()
    print(np.array(list(basic_colors_freq.keys())).shape)
    nn = train_nn_on_basic_colors(basic_colors=np.array(list(basic_colors_freq.keys())))
    return project_image_onto_basic_colors(img=img, nn=nn, n_pixels=n_pixels)
