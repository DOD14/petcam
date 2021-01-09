import astral, astral.geocoder, astral.sun
from datetime import datetime
import pytz
from time import sleep

class Looper:

    def __init__(self, sleep_interval, sundial):

        print('[+][looper] initialised looper instance')

        # get time and sunlight info from sundial
        self.sundial = sundial

        # someone else will start main loop
        self.loop_running = False 

        # set how long to sleep between calls to loop_func
        self.sleep_interval = int(sleep_interval)
        

    def loop(self, func):
        """The main purpose of this class: runs a given function in a loop, but keeping track of day and night for camera setup and image processing purposes."""
        # start loop running
        print('[+][looper] starting looper loop')
        self.loop_running = True

        # one iteration per day
        while self.loop_running: 

            # update the sunrise/sunset times for today
            sundial.update_sun()

            # initialise latest datetime for nested loop
            self.last_datetime = sundial.now()
            today = self.last_datetime.day

            print("[+][looper] it's " + self.last_datetime.strftime('%A'))

            # as many iterations in a day as sleep_interval allows
            while self.loop_running and self.last_datetime.day == today:                 
                
                # do custom stuff! 
                print('[+][looper] about to call func()')
                func()


                # /stop command allows current iteration to finish
                # before breaking out of loop
                if not self.loop_running:
                    break

                # take a break
                print('[+][looper] will now sleep ' + str(self.sleep_interval))
                sleep(self.sleep_interval)

                # update last_datetime to check if a new day has started
                self.last_datetime = sundial.now()

        print('[+][looper] loop ended')
