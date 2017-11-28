import service.sensor_manager
from service.sensor_manager import Sensor, SensorType

camera = None


def setup_camera(sensor_manager: service.sensor_manager.SensorManager):
    try:
        import picamera
        global camera

        camera = picamera.PiCamera()
        camera.resolution = (1024, 768)
        camera.start_preview()
        camera_sensor = Sensor(SensorType.PI_CAMERA, "Pi CAM", "@PI_CAM", None)
        sensor_manager._register_sensor(camera_sensor)

    except:
        pass
