import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal

class CameraCalibration(QThread):
    progress = Signal(int)
    def __init__(self, video_filename, nx, ny, rotate, v_flip, h_flip):
        super().__init__()
        self.video_filename = video_filename
        self.nx = nx
        self.ny = ny
        self.rotate = rotate
        self.v_flip = v_flip
        self.h_flip = h_flip
        self.sample_rate = 200

    def reorient(self, frame):
        if self.rotate % 360 != 0:
            height, width = frame.shape[:2]
            rotation_matrix = cv2.getRotationMatrix2D(
                (width // 2, height // 2),
                self.rotate,
                1.0,
            )
            frame = cv2.warpAffine(
                frame,
                rotation_matrix,
                (width, height),
            )
        if self.v_flip:
            frame = cv2.flip(frame, 0)
        if self.h_flip:
            frame = cv2.flip(frame, 1)
        return frame

    def get_frame(self, frame_number):
        self.video_stream.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        status, frame = self.video_stream.read()
        return status, frame

    def run(self):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((self.nx * self.ny, 3), np.float32)
        objp[:,:2] = np.mgrid[0:self.ny, 0:self.nx].T.reshape(-1, 2)
        chessboard_dims = (self.nx, self.ny)

        objpoints = []
        imgpoints = []

        self.video_stream = cv2.VideoCapture(self.video_filename)
        total_frames = int(self.video_stream.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frames_with_corners = 0
        for nth_frame in range(0, total_frames, self.sample_rate):
            status, frame = self.get_frame(nth_frame)
            if not status:
                break
            frame = self.reorient(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners_found, corners = cv2.findChessboardCorners(gray, chessboard_dims)
            if corners_found:
                self.frames_with_corners += 1
                corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                objpoints.append(objp)
                imgpoints.append(corners)
            self.progress.emit(int(100 * nth_frame / total_frames))

        print(self.frames_with_corners)
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            gray.shape[::-1],
            None,
            None,
        )

        self.mtx = mtx
        self.dist = dist