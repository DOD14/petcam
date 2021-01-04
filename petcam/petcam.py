import os
from PIL import Image, ImageStat, ImageEnhance
from time import sleep

class Petcam:

    def __init__(self, day_snap_cmd, night_snap_cmd, save_dir = 'photos', brightness_threshold=80, brighten_factor=2.0):
        
        print('[+][petcam] initialised petcam instance')
       
        # just initilise a bunch of attributes
        self.camera_in_use = False
        self.day_cmd = day_snap_cmd
        self.night_cmd = night_snap_cmd
        self.save_dir = save_dir
        self.brightness_threshold = brightness_threshold
        self.brighten_factor = brighten_factor
        self.last_snap = None
        self.snaps = []

    def snap(self, timestamp, light_outside=False):
        """ Takes a photo using the command provided in the config file and brightens it up if necessary. Returns the path where the image has been saved."""
        
        # construct filename based on timestamp
        name = timestamp.strftime("%d-%m-%Y+%H:%M:%S") + ".jpg"
        img_path = self.save_dir + "/" + name 
        print('[+][petcam] preparing to take photo in mode light_outside = ' + str(light_outside) + ": "  + img_path)

        # ensure camera not busy
        self.wait_cam_free()
        
        # set cam busy. snap pic, release cam
        self.camera_in_use = True
        cmd = self.day_cmd if light_outside else self.night_cmd
        cmd += " " + img_path 
        print('[+][petcam] executing command: ' + cmd)
        os.system(cmd)
        self.camera_in_use = False
        
        # what it says on the tin
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
    

    def brighten_if_needed(self, filename):
        """Receives the path to an image, and if the mean pixel value is below a threshold, brightens image by a factor."""

        # get mean pixels values from grayscale version of image
        img = Image.open(filename)
        gray = img.convert('L')
        brightness = ImageStat.Stat(gray).mean[0]
        
        # if the image is dark, enhance it and save under the same name
        if brightness < self.brightness_threshold:
            print("[+][petcam] image brightness (" + str(brightness) + ") < threshold (" + str(self.brightness_threshold) + ")")
            print('[+][petcam] brightening up image by a factor of ' + str(self.brighten_factor))
            bright = ImageEnhance.Brightness(img)
            bright.enhance(self.brighten_factor).save(filename, "JPEG")
