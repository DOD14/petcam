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
        
    def snap(self, timestamp, light_outside = True, resolution = None, iso = None, shutter_speed = None, awb_mode = None):
        """ Takes a photo using the command provided in the config file and brightens it up if necessary. Returns the path where the image has been saved."""
        
        # apply defaults if params not supplied
        resolution = resolution or self.resolution
        iso = iso or self.iso
        shutter_speed = shutter_speed or self.shutter_speed
        awb_mode = awb_mode or self.awb_mode

        # construct filename based on timestamp
        name = timestamp.strftime("%d-%m-%Y+%H:%M:%S") + ".jpg"
        img_path = str(self.img_save_dir.joinpath(name)) 
        print('[+][petcam] preparing to take photo in mode light_outside = ' + str(light_outside) + ": "  + img_path)

        # ensure camera not busy
        self.wait_cam_free()
        
        # set cam busy. snap pic, release cam
        self.camera_in_use = True

        with PiCamera(resolution=resolution) as cam: 
            
            if not light_outside:
                cam.framerate = Fraction(1000000, shutter_speed)
                cam.iso = iso
                cam.shutter_speed = shutter_speed 
                cam.exposure_mode = 'night'
                cam.awb_mode = awb_mode
            else:
                sleep(2)

            cam.capture(img_path)

        self.camera_in_use = False
        
        # brighten if below brightness threshold
        self.brighten_if_needed(img_path)

        # in case someone wants to have a look
        # without waiting for a new photo
        self.last_snap = img_path 
        self.snaps.append(name)

        return img_path 

    def wait_cam_free(self):
        """Sleeps until the camera_in_use flag is set to False."""
        
        # print a message before going silent
        if self.camera_in_use:
            print('[+][petcam] waiting for camera')
        
        # sleep until camera ready
        while self.camera_in_use:
            sleep(1)
    

    def brighten_if_needed(self, filename, brightness_threshold = None, brighten_factor = None):
        """Receives the path to an image, and if the mean pixel value is below a threshold, brightens image by a factor."""

        brightness_threshold = brightness_threshold or self.brightness_threshold
        brighten_factor = brighten_factor or self.brighten_factor

        # get mean pixels values from grayscale version of image
        img = Image.open(filename)
        gray = img.convert('L')
        brightness = ImageStat.Stat(gray).mean[0]
        
        # if the image is dark, enhance it and save under the same name
        if brightness < brightness_threshold:
            print("[+][petcam] image brightness (" + str(brightness) + ") < threshold (" + str(brightness_threshold) + ")")
            print('[+][petcam] brightening up image by a factor of ' + str(brighten_factor))
            bright = ImageEnhance.Brightness(img)
            bright.enhance(brighten_factor).save(filename, "JPEG")
        else:
            print("[+][petcam] image brightness (" + str(brightness) + ") > threshold (" + str(brightness_threshold) + ")")


    def snaps_to_video(self, video_size = None, fps = None):

        video_size = video_size or self.resolution
        fps = fps or self.fps

        videoname = str(self.vid_save_dir.joinpath(self.snaps[-1]).with_suffix('.mp4'))
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        out = cv2.VideoWriter(
                videoname,
                fourcc,
                fps,
                video_size
                )
        for snap in self.snaps:
            img_path = str(self.img_save_dir.joinpath(snap))
            print('[+][petcam] reading image: ' + img_path)
            img = cv2.imread(img_path)
            img = cv2.resize(img, video_size)
            out.write(img)
        out.release()
        return videoname 
