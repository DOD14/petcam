import astral, astral.geocoder, astral.sun
from datetime import datetime
import pytz
from time import sleep

class Timelapser:

    def __init__(self, city, sleep_interval):
        # set how long to sleep between events
        self.sleep_interval = sleep_interval
        
        # once we know where we are we can get the currrnt time in the local timezone
        self.city = astral.geocoder.lookup(city, astral.geocoder.database())
        self.start_time = self.now()
        self.update_last_datetime()

        # keep track of what day it is so we update sunrise/sunset times at midnight
        self.update_today_day()

        # make a note of when the sun rises/sets
        today_sun = astral.sun.sun(self.city.observer, date = self.start_time, tzinfo=self.city.timezone)
        self.sunrise = today_sun["sunrise"]
        self.sunset = today_sun["sunset"]
        

    def now(self):
        return datetime.now(pytz.timezone(self.city.timezone))

    def light_outside(self):
        if now_datetime > sunrise and now_datetime < sunset:
            return True
        else:
            return False
    
    def update_today_day(self):
        self.today_day = self.now().day

    def update_last_datetime(self):
        self.last_datetime = self.now()

    def dump_properties(self):
        dump = '[+] initialised timelapser instance at ' + self.start_time.strftime('%H:%M:%S')
        dump += '[i] location: ' + str(self.city)
        dump += "[i] sunrise: " + str(self.sunrise)
        dump += "[i] sunset: " + str(self.sunset)
        dump += "[i] sleep interval: " + str(self.sleep_interval) + " seconds"
        return dump
