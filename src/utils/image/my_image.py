import numpy as np
import cv2
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from collections import Counter


class MyNN(NearestNeighbors):
    def fit(self, X, y=None):
        self.X = X
        super().fit(X, y)


class MyImage:
    def __init__(
        self,
        image_bytes: bytearray | None = None,
        rgb: np.ndarray | None = None,
        name: str | None = None,
        url: str | None = None,
    ):
        if image_bytes is None and rgb is None:
            raise ValueError("Both image_bytes and rgb are None")

        if image_bytes is None:
            bgr = cv2.cvtColor(np.float32(rgb), cv2.COLOR_RGB2BGR).astype(np.uint8)
            success, image_bytes = cv2.imencode(".png", bgr)
            if success:
                image_bytes = bytearray(image_bytes.tobytes())
            else:
                raise ValueError("failed to convert image to bytes!")

        if rgb is None:
            np_bytes = np.asarray(image_bytes, dtype="uint8")
            bgr = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
            rgb = cv2.cvtColor(np.float32(bgr), cv2.COLOR_BGR2RGB).astype(np.uint8)

        self.image_bytes = image_bytes
        self.rgb = rgb
        self.bgr = bgr
        self.name = name
        self.url = url

    def plot(self, *args, **kwargs):
        plt.imshow(self.rgb, *args, **kwargs)
        plt.title(self.name)
        plt.axis("off")
        plt.show()

    def shrink_without_distortion(self, n_pixels: int) -> np.array:
        image = self.rgb
        if image is None:
            return None
        hw_ratio = image.shape[0] / image.shape[1]
        new_h = int(np.sqrt(n_pixels * hw_ratio))
        new_w = int(np.sqrt(n_pixels / hw_ratio))
        return MyImage(rgb=cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA))

    def color_analysis(
        self, n_clusters: int = 5, shrink: bool = True, n_pixels: int = 1000, rescale: bool = True
    ) -> dict:
        image = self.rgb

        image = self.shrink_without_distortion(n_pixels=n_pixels).rgb
        X = image.reshape(-1, 3)
        clf = KMeans(n_clusters=n_clusters, n_init=10)
        color_labels = clf.fit_predict(X)
        center_colors = np.array(clf.cluster_centers_).astype(int)
        counts = Counter(color_labels)
        local_centroids_freq = {tuple(center_colors[idx, :]): count for idx, count in dict(counts).items()}
        if rescale:
            acc_n_pixels = sum(local_centroids_freq.values())
            scale_factor = n_pixels / acc_n_pixels
            local_centroids_freq = {col: freq * scale_factor for col, freq in local_centroids_freq.items()}
        self.basic_colors = center_colors
        return local_centroids_freq

    def project_onto_basic_colors(
        self, nn: MyNN | None = None, shrink: bool = True, n_pixels: int = 1000, plot: bool = True
    ):
        image = self.rgb
        if shrink:
            image = self.shrink_without_distortion(n_pixels=n_pixels).rgb
        x_shape, y_shape = image.shape[:2]

        X = image.reshape(-1, 3)
        if nn is None:
            nn = MyNN(n_neighbors=1, algorithm="brute")
            if not hasattr(self, "basic_colors"):
                self.color_analysis()
            nn.fit(self.basic_colors)
        indices = nn.kneighbors(X, return_distance=False)
        colors = [nn.X[idx[0]] for idx in indices]
        projected_image = np.array(colors).reshape(x_shape, y_shape, 3)

        if plot:
            fig = plt.figure(figsize=(10, 10))
            fig.add_subplot(1, 2, 1)
            plt.imshow(image)
            fig.add_subplot(1, 2, 2)
            plt.imshow(projected_image)
            plt.show()

        return MyImage(rgb=projected_image)
