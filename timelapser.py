import astral, astral.geocoder, astral.sun
from datetime import datetime
import pytz
from time import sleep

class Timelapser:

    def __init__(self, city, sleep_interval):
        
        # once we know where we are we can get the currrnt time in the local timezone
        self.city = astral.geocoder.lookup(city, astral.geocoder.database())
        self.start_time = self.now()
        
        # set how long to sleep between events
        self.sleep_interval = sleep_interval

    def now(self):
        return datetime.now(pytz.timezone(self.city.timezone))

    def update_sun(self):
        # make a note of when the sun rises/sets
        today_sun = astral.sun.sun(self.city.observer, date = self.now(), tzinfo=self.city.timezone)
        self.sunrise = today_sun["sunrise"]
        self.sunset = today_sun["sunset"]

    def light_outside(self, date):
        if date > sunrise and date < sunset:
            return True
        else:
            return False
    
    def loop(self, function):
        while True: # one iteration per day
            print('[+] starting timelapser loop')
            
            self.today = self.now().day
            self.update_sun()
            
            self.last_datetime = self.now()
            while self.last_datetime.day == self.today: # as many iterations in a day as sleep_interval allows
                # do stuff
                function()

                # take a break
                sleep(self.sleep_interval)

                # update last_datetime to check if a new day has started
                self.last_datetime = self.now()

    def dump_properties(self):
        dump = '[+] initialised timelapser instance at ' + self.start_time.strftime('%H:%M:%S')
        dump += '[i] location: ' + str(self.city)
        dump += '[i] today: ' + str(self.today)
        dump += "[i] sunrise: " + str(self.sunrise)
        dump += "[i] sunset: " + str(self.sunset)
        dump += "[i] sleep interval: " + str(self.sleep_interval) + " seconds"
        return dump
