import astral, astral.geocoder, astral.sun
from datetime import datetime
import pytz
from time import sleep

class Timelapser:

    def __init__(self, city, sleep_interval, loop_func):

        print('[+][timelapser] initialised timelapser instance')

        # once we know where we are we can get the currrnt time in the local timezone
        self.city = astral.geocoder.lookup(city, astral.geocoder.database())
        self.start_time = self.last_datetime = self.now()
        
        # so we know if there's light outside
        self.update_sun()

        # function to run inside loop()
        self.loop_func = loop_func
        self.loop_running = False 

        # set how long to sleep between calls to loop_func
        self.sleep_interval = int(sleep_interval)
        
    def now(self):
        """Returns datetime.now() in the local timezone."""
        return datetime.now(pytz.timezone(self.city.timezone))
   

    def update_sun(self):
        """Updates info of when the sun rises/sets - useful when the main loop runs several days."""

        # get the daylight (start, end) for today in the local timezone
        self.today_light = astral.sun.daylight(self.city.observer, date = self.now(), tzinfo=self.city.timezone)

    def light_outside(self):
        """Returns True if the latest datetime in the main loop is between sunrise and sunset, False otherwise."""
        
        if self.last_datetime in self.today_light:
            return True
        else:
            return False
    
    def loop(self):
        """The main purpose of this class: runs a given function in a loop, but keeping track of day and night for camera setup and image processing purposes."""
        print('[+][timelapser] starting timelapser loop')
        self.loop_running = True

        # one iteration per day
        while self.loop_running: 
            print("[+][timelapser] it's a new day")

            # update the day and the sunrise/sunset times
            self.today = self.now().day
            self.update_sun()
            
            # initialise latest datetime for nested loop
            self.last_datetime = self.now()

            # as many iterations in a day as sleep_interval allows
            while self.last_datetime.day == self.today:                 
                
                # do custom stuff! 
                print('[+][timelapser] about to call loop_func')
                self.loop_func()


                # stop command allows current iteration to finish
                # before breaking out of loop
                if not self.loop_running:
                    break

                # take a break
                print('[+][timelapser] will now sleep ' + str(self.sleep_interval))
                sleep(self.sleep_interval)

                # update last_datetime to check if a new day has started
                self.last_datetime = self.now()

