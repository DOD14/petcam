import os
from pathlib import Path

class MotionManager:

    def __init__(self, motion_conf_dir, motion_save_dir):
        print('[+][motion] initialising motion_manager instance')
        
        self.motion_conf_files = Path(motion_conf_dir).iterdir()
        
        self.motion_running = False
        
        self.motion_save_dir = Path(motion_save_dir)
        self.captures = self.get_captures_as_set()
        print('[debug] __init__ self.captures: ' + str(self.captures))

    def get_captures_as_set(self):
        return set(self.motion_save_dir.iterdir())
        
    def get_new_captures(self):
        all_captures = self.get_captures_as_set()
        print('[debug] all_captures: ' + str(all_captures))
        new_captures = all_captures - self.captures
        print('[debug] new_captures: ' + str(new_captures))
        self.captures = all_captures
        
        return new_captures

    def start_motion(self, conf_file_path):
        self.motion_running = True
        os.system('sudo motion -c ' + str(conf_file_path))

    def stop_motion(self):
        os.system('sudo service motion stop')
        self.motion_running = False
