import os
from PIL import Image, ImageStat, ImageEnhance
from time import sleep

class Petcam:

    def __init__(self, day_snap_cmd, night_snap_cmd, save_dir = 'photos', brightness_threshold=80, brighten_factor=2.0):
        print('[+] initialised petcam instance')
        self.camera_in_use = False
        self.day_cmd = day_snap_cmd
        self.night_cmd = night_snap_cmd
        self.save_dir = save_dir
        self.brightness_threshold = brightness_threshold
        self.brighten_factor = brighten_factor

    def snap(self, timestamp, light_outside=True):
        filename = self.save_dir + "/" + timestamp + ".jpg"
        print('[+] preparing to take photo in mode light_outside = ' + str(light_outside) + ": "  + filename)

        # ensure camera not busy
        self.wait_cam_free()
        
        # set cam busy. snap pic, release cam
        self.camera_in_use = True
        cmd = self.day_cmd if light_outside else self.night_cmd
        cmd += " " + filename
        print('[+] executing command: ' + cmd)
        os.system(cmd)
        self.camera_in_use = False
        
        self.brighten_if_needed(filename)

        return filename

    def wait_cam_free(self):
        if self.camera_in_use:
            print('[+] waiting for camera')
        while self.camera_in_use:
            sleep(1)
    
    def brighten_if_needed(self, filename):
        img = Image.open(filename)
        gray = img.convert('L')
        brightness = ImageStat.Stat(gray).mean[0]
        
        if brightness < self.brightness_threshold:
            print("[+] image brightness (" + str(brightness) + ") < threshold (" + str(self.brightness_threshold) + ")")
            print('[+] brightening up image by a factor of ' + str(self.brighten_factor))
            bright = ImageEnhance.Brightness(img)
            bright.enhance(self.brighten_factor).save(filename, "JPEG")
