import cv2
from fractions import Fraction
import os
from pathlib import Path
from picamera import PiCamera
from PIL import Image, ImageStat, ImageEnhance
from time import sleep

class Petcam:

    def __init__(self, img_save_dir = 'photos', vid_save_dir = 'videos', resolution = (256, 256), iso = 800, shutter_speed = 6000000, awb_mode = 'tungsten', fps = 5, brightness_threshold=80, brighten_factor=2.0):
        
        print('[+][petcam] initialised petcam instance')
       
        # just initilise a bunch of attributes
        self.camera_in_use = False
        
        self.img_save_dir = Path(img_save_dir)
        self.vid_save_dir = Path(vid_save_dir)

        self.last_snap = None
        self.snaps = []
        
        # the following can be overridden when calling functions 
        self.resolution = resolution
        self.iso = iso
        self.shutter_speed = shutter_speed
        self.awb_mode = awb_mode
        self.fps = fps
        self.brightness_threshold = brightness_threshold
        self.brighten_factor = brighten_factor
        
    def snap(self, name, light_outside = True, resolution = None, iso = None, shutter_speed = None, awb_mode = None):
        """ Takes a photo using using day/night settings and brightens it up if necessary. Returns the path where the image has been saved."""
        
        # apply defaults if params not supplied
        resolution = resolution or self.resolution
        iso = iso or self.iso
        shutter_speed = shutter_speed or self.shutter_speed
        awb_mode = awb_mode or self.awb_mode
        
        # construct img_path  
        img_path = str(self.img_save_dir.joinpath(name)) 
        print('[+][petcam] preparing to take photo in mode light_outside = ' + str(light_outside) + ": "  + img_path)

        # ensure camera not busy
        self.wait_cam_free()
        
        # set cam busy
        self.camera_in_use = True

        # actually instantiate PiCamera 
        with PiCamera(resolution=resolution) as cam: 
            
            # lots of adjustments for low light  
            if not light_outside:
                cam.framerate = Fraction(1000000, shutter_speed)
                cam.iso = iso
                cam.shutter_speed = shutter_speed 
                cam.exposure_mode = 'night'
                cam.awb_mode = awb_mode

            # auto adjust in daylight
            else:
                sleep(5)
            
            # actually capture the photo!
            cam.capture(img_path)
        
        # release camera
        self.camera_in_use = False
        
        # brighten if below brightness threshold
        self.brighten_if_needed(img_path)

        # for the record
        self.last_snap = img_path 
        self.snaps.append(img_path)
        
        # return path to new image
        return img_path 


    def wait_cam_free(self):
        """Sleeps until the camera_in_use flag is set to False."""
        
        # print a message before going silent
        if self.camera_in_use:
            print('[+][petcam] waiting for camera')
        
        # sleep until camera ready
        while self.camera_in_use:
            sleep(1)
    

    def brighten_if_needed(self, img_path, brightness_threshold = None, brighten_factor = None):
        """Receives the path to an image, and if the mean pixel value is below a threshold, brightens image by a factor."""
        
        # use defaults if not supplied
        brightness_threshold = brightness_threshold or self.brightness_threshold
        brighten_factor = brighten_factor or self.brighten_factor

        # get mean pixels values from grayscale version of image
        img = Image.open(img_path)
        gray = img.convert('L')
        brightness = ImageStat.Stat(gray).mean[0]
        
        # if the image is dark, enhance it and save under the same name
        if brightness < brightness_threshold:
            bright = ImageEnhance.Brightness(img)
            bright.enhance(brighten_factor).save(img_path, "JPEG")


    def snaps_to_video(self, video_size = None, fps = None):
        """Converts all snapshots in the snaps dict to a video and returns video path"""

        # use defaults if not supplied
        video_size = video_size or self.resolution
        fps = fps or self.fps

        # name video after the latest snap
        vid_name = Path(self.snaps[-1]).with_suffix('.mp4').name
        
        # will save video in vid_save_dir
        vid_path = str(self.vid_save_dir.joinpath(vid_name))

        # after some trial-and-error this shows up nicely in telegram
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        
        # create VideoWriter with our settings
        out = cv2.VideoWriter(
                vid_path,
                fourcc,
                fps,
                video_size
                )
        
        # loop over snaps
        for snap in self.snaps:
            # read, resize, write
            img = cv2.imread(snap)
            img = cv2.resize(img, video_size)
            out.write(img)
        out.release()
        
        return vid_path 
