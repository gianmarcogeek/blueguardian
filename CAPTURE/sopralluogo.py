import cv2
import threading
import numpy as np
import datetime
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
inPIN = 7
GPIO.setup(inPIN, GPIO.IN)


class CSI_Camera:

    def __init__(self):
        self.video_capture = None
        self.frame = None
        self.grabbed = False
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            self.grabbed, self.frame = self.video_capture.read()

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)

    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        if self.video_capture is not None:
            self.running = True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running = False
        self.read_thread.join()
        self.read_thread = None

    def updateCamera(self):
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            except RuntimeError:
                print("Could not read image from camera")

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def release(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        if self.read_thread is not None:
            self.read_thread.join()


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=10,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def run_camera():
    window_title = "Single Camera Stream"
    camera = CSI_Camera()
    camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            capture_width=3840,
            capture_height=2160,
            flip_method=0,
            display_width=3840,
            display_height=2160,
        )
    )
    camera.start()

    if camera.video_capture.isOpened():

        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

        save_in_progress = False

        try:
            while True:
                _, image = camera.read()
                button = GPIO.input(inPIN)

                image_preview = image.copy()
                image_preview = cv2.resize(image_preview, (426, 240))

                if button and not save_in_progress:
                    save_in_progress = True
                    image_preview = cv2.rectangle(image_preview, (0, 0), (image_preview.shape[1], image_preview.shape[0]), (0, 255, 0), 80)
                
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, image_preview)
                else:
                    break

                keyCode = cv2.waitKey(30) & 0xFF
                if keyCode == 27:
                    break
                if save_in_progress:
                    img_name = "./pictures/camera_{}.png".format(datetime.datetime.now())
                    cv2.imwrite(img_name, image)
                    save_in_progress = False
        finally:
            camera.stop()
            camera.release()
        cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")
        camera.stop()
        camera.release()


if __name__ == "__main__":
    run_camera()