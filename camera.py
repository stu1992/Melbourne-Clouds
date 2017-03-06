import picamera
import logging
from fractions import Fraction


class camera:
    camera = None
    log = None
    preset = None
    preset_map = {
            'night':{
            'resolution' : (1920,1080),
            'exposure_mode' : 'off',
            'framerate' : Fraction(1, 6),
            'shutter_speed': 3000000,
            'iso' : 800},
            
            'twilight':{
            'resolution' : (1920,1080),
            'exposure_mode' : 'off',
            'framerate' : Fraction(1, 6),
            'shutter_speed': 3000000,
            'iso' : 800},
            
            'day':{
            'resolution' : (1920,1080),
            'exposure_mode' : 'auto',
            'framerate' : Fraction(30, 1),
            'shutter_speed': 0L,
            'iso' : 0L}
            }
            
    def __init__(self,preset='day'):
        self.log = logging.getLogger("Camera")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler("/var/lib/clouds/log")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.preset = preset
        self.camera = picamera.PiCamera()
        self.set_preset(preset)
        #self.camera.annotate_foreground = picamera.Color(y=0.0 u=1.0, v=0.5)
        self.camera.annotate_background = picamera.Color('#000')


        
        self.log.debug("camera started")
    
    def get_camera(self):
        return self.camera
    def set_preset(self,time):
        self.preset = time
        for attr in self.preset_map[time]:
            setattr(self.camera,attr,self.preset_map[time][attr])
        self.log.debug("camera preset changed:"+ str(self.preset_map[time]))
    
    def capture(self,location, anottation):
        #self.log.debug('taking snapshot -> '+ str(location))
        self.camera.annotate_text = anottation
        self.camera.capture(location)
        #self.log.debug('snapshot taken')
