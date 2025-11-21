import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal

class CameraCalibration(QThread):
    progress = Signal(tuple)
    def __init__(self, video_filename, nx, ny, rotate, v_flip, h_flip, sample_rate, distorted):
        super().__init__()
        self.video_filename = video_filename
        self.nx = nx
        self.ny = ny
        self.rotate = rotate
        self.v_flip = v_flip
        self.h_flip = h_flip
        self.sample_rate = sample_rate
        self.mtx = None
        self.dist = None
        self.distorted = distorted
        self.frames_with_corners = []
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.rvecs = None
        self.tvecs = None

    def zoom(self, img, cx, cy, zoom):
        h, w, _ = [ zoom * i for i in img.shape ]
        cx, cy = [ zoom * c for c in (cx, cy) ]
        img = cv2.resize( img, (0, 0), fx=zoom, fy=zoom)
        img = img[ int(round(cy - h/zoom * .5)) : int(round(cy + h/zoom * .5)),
               int(round(cx - w/zoom * .5)) : int(round(cx + w/zoom * .5)),
               : ]
        return img

    def draw_chessboard(self, frame, corners, zoom=False):
        img = np.copy(frame)
        to_int = lambda _: (int(i) for i in _)
        radius = int(abs(corners[0][0][0] - corners[1][0][0]) / 2)
        x, y = to_int(corners[0][0])
        cv2.circle(img, (int(x), int(y)), radius, (255, 0, 0), radius // 5)
        x, y = to_int(corners[-1][0])
        cv2.circle(img, (x, y), radius, (0, 0, 255), radius // 5)
        for i in range(len(corners) - 1):
            x1, y1 = to_int(corners[i][0])
            x2, y2 = to_int(corners[i + 1][0])
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), radius // 5)

        if zoom:
            fx, fy = to_int(corners[-1][0])
            lx, ly = to_int(corners[0][0])
            cx = fx + (lx - fx) / 2
            cy = fy + (ly - fy) / 2
            zf = min(
                img.shape[1] / (lx - fx),
                img.shape[0] / (ly - fy),
            ) * 0.75
            img = self.zoom(img, cx, cy, zf)

        return img

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

    def detect_chessboard(self, video_stream):
        chessboard_dims = (self.nx, self.ny)
        nth_frame = 0
        while True:
            nth_frame += 1
            status, frame = self.video_stream.read()
            if nth_frame % self.sample_rate != 0:
                continue
            if not status:
                break
            frame = self.reorient(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners_found, corners = cv2.findChessboardCorners(gray, chessboard_dims)
            if corners_found:
                corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), self.criteria)
                yield nth_frame, frame, corners
            else:
                yield nth_frame, frame, None

    def calc_intrinsics(self, imgpoints, objpoints):
        h, w = self.shape
        self.mtx = cv2.initCameraMatrix2D(objpoints, imgpoints, (w, h))

        for i, points in enumerate(imgpoints):
            retval, rvec, tvec, inliers = cv2.solvePnPRansac(
                objpoints[0],
                points,
                self.mtx,
                np.zeros(5, dtype='float64'),
                confidence=0.9,
                reprojectionError=30,
            )
            if retval:
                self.rvecs.append(rvec)
                self.tvecs.append(tvec)
            yield i

    def calc_distorted_intrinsics(self, imgpoints, objpoints):
        h, w = self.shape
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            (w, h),
            None,
            None,
        )
        print(dist)
        if ret:
            self.rvecs = rvecs
            self.tvecs = tvecs
            self.dist = dist
            self.mtx = mtx
        else:
            raise Exception("Calibration failed")

    def run(self):
        objp = np.zeros((self.nx * self.ny, 3), np.float32)
        objp[:,:2] = np.mgrid[0:self.ny, 0:self.nx].T.reshape(-1, 2)

        objpoints = []
        imgpoints = []

        self.video_stream = cv2.VideoCapture(self.video_filename)
        total_frames = int(self.video_stream.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frames_with_corners = []
        self.shape = None
        for idx, frame, corners in self.detect_chessboard(self.video_stream):
            self.shape = frame.shape[:2]
            if corners is not None:
                self.frames_with_corners.append(frame)
                objpoints.append(objp)
                imgpoints.append(corners)
                frame = self.draw_chessboard(frame, corners)
            self.progress.emit((
                min(int(100 * idx / total_frames), 100),
                frame,
                "Detecting calibration board",
            ))

        if not self.frames_with_corners:
            raise Exception("Insufficient frames")
            '''
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                objpoints,
                imgpoints,
                gray.shape[::-1],
                None,
                None,
            )
            '''

        self.progress.emit((0, None, "Computing intrinsic properties"))
        h, w = self.shape
        if self.distorted:
            self.calc_distorted_intrinsics(imgpoints, objpoints)
            frame = self.frames_with_corners[0]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
                self.mtx,
                self.dist,
                (w, h),
                1,
                (w, h),
            )
            dst = cv2.undistort(frame, self.mtx, self.dist, None, newcameramtx)
            cv2.imshow("dist", dst)
            x, y, w, h = roi
            dst = dst[y:y+h, x:x+w]
            self.progress.emit((
                100,
                dst,
                "Estimation complete",
            ))
        else:
            self.mtx = cv2.initCameraMatrix2D(objpoints, imgpoints, (w, h))

            for i in self.calc_intrinsics(imgpoints, objpoints):
                self.progress.emit((
                    100 * (i + 1) / len(imgpoints),
                    None,
                    "Calculating pose",
                ))

        self.finished.emit()
