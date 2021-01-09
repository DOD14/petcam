import astral, astral.geocoder, astral.sun
from datetime import datetime
import pytz

class Sundial:

    def __init__(self, city):

        print('[+][sundial] initialised sundial instance')

        self.city = astral.geocoder.lookup(city, astral.geocoder.database())
        self.start_time = self.last_datetime = self.now()

        # so we know if there's light outside
        self.update_sun()

    def now(self):
        """Returns datetime.now() in the local timezone."""
        return datetime.now(pytz.timezone(self.city.timezone))


    def update_sun(self):
        """Updates info of when the sun rises/sets - useful when the main loop runs several days."""

        # get the daylight (start, end) for today in the local timezone
        self.today_light = astral.sun.daylight(self.city.observer, date = self.now(), tzinfo=self.city.timezone)

    def light_outside(self):
        """Returns True if the latest datetime in the main loop is between sunrise and sunset, False otherwise."""
        return True if self.last_datetime in self.today_light else False
