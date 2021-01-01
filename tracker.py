
class Tracker:

    def __init__(self, classes):
        print('[+] initialised tracker instance')
        
        # dummy state before first photo is classified
        self.last_result = "unknown"
        self.last_seen = {key:"unknown" for key in classes}

    def check_state_change(self, result, result_time):
        # update our records of what was spotted when
        tracker.last_seen[result] = result_time
        if tracker.last_result != result:
            self.last_result = result
            return True
        else return False
