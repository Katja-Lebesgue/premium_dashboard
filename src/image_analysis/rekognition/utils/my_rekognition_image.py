import numpy as np
import pandas as pd
from loguru import logger
from src.image_analysis.rekognition.utils.rekognition_image import RekognitionImage


class MyRekognitionImage(RekognitionImage):
    def get_text(self) -> dict:
        texts = self.detect_text(convert_to_dict=True)
        if not len(texts):
            return {}
        df = pd.DataFrame(texts)
        df["geometrical_features"] = df["geometry"].apply(geometrical_analysis)
        geometrical_features = df.geometrical_features.apply(pd.Series)
        geometrical_columns = geometrical_features.columns.tolist()
        df = df.join(geometrical_features)

        # remove words and blurs
        df = df[(df.kind == "LINE") & (df.confidence > 90) & (df.height >= 0.02)]

        # remove tilted text
        df = df[df.tg.apply(lambda x: abs(x) < 0.02)]

        if len(df) == 0:
            return {}

        # remove small text
        main_text_height = df.loc[df.area.idxmax(), "height"]
        df = df[df.height >= main_text_height * 0.5]

        # remove text that is not aligned with main text
        main_text = df[df.height.between(main_text_height * 0.7, main_text_height * 1.3)]
        n, w = main_text[["n", "w"]].min()
        s, e = main_text[["s", "e"]].max()
        df = df[((df.s < s + 0.1) & (df.n > n - 0.1)) | ((df.w > w - 0.1) & (df.e < e + 0.1))]
        if not len(df):
            return {}
        df = df[["text"] + geometrical_columns]

        # calculate total height, width and center
        height = df.s.max() - df.n.min()
        width = df.e.max() - df.w.min()
        center = df.center.mean()
        text = "\n".join(df.text.tolist())
        result = {"text": text, "height": height, "width": width, "center": center}
        return result

    def get_labels(self, max_labels: int = 5, min_confidence: float = 90) -> list[dict]:
        labels = self.detect_labels(max_labels=max_labels, convert_to_dict=True)
        if not len(labels):
            return []
        df = pd.DataFrame(labels)
        df = df[df.confidence > min_confidence]
        return df[["name", "parents"]].to_dict("records")

    def get_faces(self) -> list[dict]:
        faces = self.detect_faces(convert_to_dict=True)
        faces = [face for face in faces if face["confidence"] > 90]
        if not len(faces):
            return []
        series_of_dicts = pd.Series(faces)
        df = pd.DataFrame(faces)
        geometrical_features = series_of_dicts.apply(geometrical_analysis).apply(pd.Series)
        df = df.join(geometrical_features)
        df = df[
            list(
                set(["age", "gender", "emotions", "has", "center", "height", "width"]).intersection(
                    df.columns
                )
            )
        ]
        return df.to_dict("records")


def geometrical_analysis(geometry: dict) -> dict:
    polygon = geometry.get("Polygon")
    bounding_box = geometry.get("BoundingBox")
    if bounding_box is None:
        bounding_box = geometry.get("bounding_box")
    result = {}
    result = result | {k.lower(): v for k, v in bounding_box.items()}
    result["center"] = np.array((result["left"] + result["width"] / 2, result["top"] + result["height"] / 2))
    result["area"] = result["width"] * result["height"]
    if polygon is not None:
        nw, ne, se, sw = (np.array((coord["X"], coord["Y"])) for coord in polygon)
        diff = ne - nw
        tg = diff[1] / diff[0]
        result["tg"] = tg
        corners = np.array([nw, ne, se, sw])
        result["center"] = np.mean(corners, axis=0)
        extremes = {
            "w": np.min(corners[:, 0]),
            "e": np.max(corners[:, 0]),
            "s": np.max(corners[:, 1]),
            "n": np.min(corners[:, 1]),
        }
        result = result | extremes
    return result
