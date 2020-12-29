import astral, astral.geocoder, astral.sun
import pytz
from time import sleep

class Timelapser:

    def __init__(self, city)
        
        # once we know where we are we can get the currrnt time in the local timezone
        self.city = astral.geocoder.lookup(city. astral.geocoder.database())
        self.start_time = self.now()
        
        # keep track of what day it is so we update sunrise/sunset times at midnight
        self.today_day = self.start_time.day
        
        # make a note of when the sun rises/sets
        today_sun = astral.sun.sun(city.observer, date = self.start_time, tzinfo=self.city.timezone)
        self.sunrise = today_sun["sunrise"]
        self.sunset = today_sun["sunset"]
        
        print('[+] initialised timelapser instance at ' + self.start_time.strftime('%H:%M:%S'))
        print('[i] location: ' + str(city) + "\n[i] sunrise: " + str(sunrise) + "\n[i] sunset: " + str(sunset))

    def now(self):
        return datetime.now(pytz.timezone(self.city.timezone))

    def light_outside(self):
        if now_datetime > sunrise and now_datetime < sunset:
            return True
        else:
            return False

    def main_loop()
while True:
    
    print('[+] starting main loop')
    # find out what day is today so we can get sunrise/sunset times 
    # and update these when the day has changed

    # take photos with today's sunrise/sunset times
    now_datetime = now() 
    while now_datetime.day == today_day:
        
        # snap photo
        filename = snap()
       
        # classify image
        result = classifier.classify_image(model=model, img_path=filename, resize_shape=(256, 256))
        print("[i] classification result: " + result)
        
        # if there has been a state change, send a message
        if last_result != "unknown" and last_result != result:
            message = "[!] update: " + last_result + " -> " + result
            print("\"" + message + "\"")
            for rec in recipients:
                with open(filename, 'rb') as image:
                    print("[+] updating " + rec)
                    bot.sendPhoto(rec, image, caption=message)
        
        # update our records of what was spotted when
        last_result = result
        last_seen[result] = now_datetime

        # wait between photos
        print('[+] will now sleep ' + str(sleep_interval) + " seconds")
        sleep(sleep_interval)
        
        # update datetime for next photo
        now_datetime = now() 
        

