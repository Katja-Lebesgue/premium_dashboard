from src.image_analysis.rekognition.utils import *


def get_faces_from_image(image: RekognitionImage):
    faces = image.detect_faces()
    return [face.to_dict() for face in faces]
