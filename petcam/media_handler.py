import cv2
import os
from pathlib import Path
from .helper import Helper

class MediaHandler(Helper):

    def __init__(self, img_save_dir = None, vid_save_dir = None, mode='local', save_photos = False, adjust_gamma = True, resolution = (240,320), video_fps = 5):
        
        print('[+][media_handler] initialised instance')
       
        # just initialise a bunch of attributes
        if img_save_dir:
            self.img_save_dir = Path(img_save_dir)
        if vid_save_dir:
            self.vid_save_dir = Path(vid_save_dir)
            self.photos_used_in_video = []
        
        if mode == 'local':
            print(mode)
            #from petcam import Petcam
            #self.camera_src = Petcam()
        elif mode == 'remote':
            from picam_server import SocketReceiver
            self.camera_src = SocketReceiver()
    
        self.resolution = resolution
        self.fps = video_fps

    def init_cmd_dict(self):
        self.cmd_dict = {'/take-photo':[self.show_photo, u'\U0001F4F8']}
        cmd_dict_for_telebot = {key: [self, value[1]] for key, value in self.cmd_dict.items()}
        print(str(cmd_dict_for_telebot))
        return cmd_dict_for_telebot

    def _take_photo(self, name):
        # photo is compatible with cv2 operations
        photo = self.camera_src.take_photo()

        # return path to new image
        return photo
    
    def show_photo(self):
        print('[debug] i show you a photo')
    
    def photos_to_video(self, photo_paths = [], video_size = None, fps = None):
        """Converts supplied photos (by path) to a video and returns video path"""

        # use defaults if not supplied
        video_size = video_size or self.resolution
        fps = fps or self.fps

        # name video after the latest snap
        vid_name = Path(self.photo_paths[-1]).with_suffix('.mp4').name
        
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
        for photo_path in photo_paths:
            # read, resize, write
            img = cv2.imread(photo_path)
            img = cv2.resize(img, video_size)
            out.write(img)
        out.release()
        
        return vid_path 
