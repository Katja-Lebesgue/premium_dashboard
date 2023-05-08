import numpy as np
import pandas as pd

from src.image_analysis.rekognition.utils import *


def get_relevant_text_from_image(image: RekognitionImage) -> str:
    labels = image.detect_text()
    df = pd.DataFrame(
        [(label.text, label.geometry["BoundingBox"]["Height"]) for label in labels if label.kind == "LINE"],
        columns=["text", "height"],
    )
    print(df)
    max_height = df.height.max()
    min_height = min(max_height * 0.8, 0.05)
    df = df[(df.height >= min_height)]
    return " ".join(df.text.tolist())
