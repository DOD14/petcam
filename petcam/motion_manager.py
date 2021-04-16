import os
from pathlib import Path

class MotionManager:

    def __init__(self, motion_conf_dir, image_save_dir, video_save_dir):
        print('[+][motion] initialising motion_manager instance')
        
        self.motion_conf_files = Path(motion_conf_dir).iterdir()
        
        self.motion_running = False
        
        self.image_save_dir = Path(image_save_dir)
        self.captures = self.get_captures_as_set()
        
        self.video_save_dir = Path(video_save_dir)
        self.videos = self.get_videos_as_set()


    def get_captures_as_set(self):
        return set(self.image_save_dir.iterdir())
    
    def get_videos_as_set(self):
        return set(self.video_save_dir.iterdir())

    def get_new_captures(self):
        all_captures = self.get_captures_as_set()
        print('[debug] all_captures: ' + str(all_captures))
        print('[debug] self.captures: ' + str(self.captures))
        new_captures = all_captures - self.captures
        print('[debug] new_captures: ' + str(new_captures))
        self.captures = all_captures
        return new_captures

    def get_new_videos(self):
        all_videos = self.get_videos_as_set()
        new_videos= all_videos - self.videos
        self.videos = all_videos
        return new_videos

    def start_motion(self, conf_file_path):
        self.motion_running = True
        os.system("sudo kill `ps aux | grep motion | grep root | awk '{print $2}'`")
        os.system('sudo motion -c ' + str(conf_file_path))

    def stop_motion(self):
        os.system("sudo kill `ps aux | grep motion | grep root | awk '{print $2}'`")
        self.motion_running = False
