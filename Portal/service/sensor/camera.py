import threading
import picamera

class CameraManager:
    def start(self):
        if self.camera is None:
            self.camera = CameraThread()
            self.camera.start()

class CameraThread(threading.Thread):

    def run(self):
        camera = picamera.PiCamera()
        with picamera.PiCamera() as camera:

#
# camera = picamera.PiCamera()
# camera.resolution = (1024, 768)
# # camera.start_preview()
