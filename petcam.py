import os
from time import sleep

class Petcam:

    def __init__(self, save_dir = 'photos', day_snap_cmd, night_snap_cmd):
        print('[+] initialised petcam instance')
        self.camera_in_use = False
        self.day_cmd = day_cmd
        self.night_cmd = night_cmd
        self.save_dir = save_dir

    def snap(self, timestamp, night=False):
        
        filename = self.save_dir + "/" + timestamp + ".jpg"
        print('[+] preparing to take photo: ' + filename)

        # ensure camera not busy
        self.wait_cam_free()
        
        # set cam busy. snap pic, release cam
        self.camera_in_use = True
        cmd = self.night_cmd if night else self.day_cmd
        print('[+] executing command: ' + cmd)
        os.system(cmd + filename)
        self.camera_in_use = False

    def wait_cam_free(self):
        if self.camera_in_use:
            print('[+] waiting for camera')
        while self.camera_in_use:
            sleep(1)
    
    # probably setup-specific. change to suit your project
    def brighten_image(self, filename)
        # todo: use PIL instead and decide whether to brighten up based on mean pixel values
        convert_cmd = "convert -brightness-contrast 70x70 " + filename + " " + filename
        os.system(convert_cmd)
