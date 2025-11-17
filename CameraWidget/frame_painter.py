from PySide6.QtGui import QImage, QPixmap

import cv2

def reorient(frame, rotate=0, v_flip=False, h_flip=False):
    if rotate % 360:
        height, width = frame.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D(
            (width // 2, height // 2),
            rotate,
            1.0,
        )
        frame = cv2.warpAffine(
            frame,
            rotation_matrix,
            (width, height),
        )
    if v_flip:
        frame = cv2.flip(frame, 0)
    if h_flip:
        frame = cv2.flip(frame, 1)
    return frame

def get_first_frame(filename, rotate=0, v_flip=False, h_flip=False):
    video = cv2.VideoCapture(filename)
    status, frame = video.read()
    frame = reorient(frame, rotate, v_flip,h_flip)
    return frame

def paint_frame(widget, frame):
    thumbnail_height = 128
    thumbnail_width = frame.shape[1] * thumbnail_height // frame.shape[0]
    frame = cv2.resize(frame, (thumbnail_width, thumbnail_height))
    thumbnail = QImage(
        frame,
        frame.shape[1],
        frame.shape[0],
        QImage.Format.Format_BGR888,
    )
    widget.setPixmap(QPixmap.fromImage(thumbnail))
    widget.setMinimumSize(*frame.shape[:2])
