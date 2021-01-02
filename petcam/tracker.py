
class Tracker:

    def __init__(self, classes):
        print('\t[+] initialised tracker instance')
        
        # dummy state before first photo is classified
        self.last_state = "unknown"
        self.last_seen = {key:"unknown" for key in classes}

    def check_state_change(self, state, state_time):
        """Updates records of what was spotted when; returns a message if there's been a change."""

        # Update record of when state was last spotted 
        self.last_seen[state] = state_time

        # if there's been a change, construct and return a relevant message
        if self.last_state != state:
            message = "[!] update: " + self.last_state + " -> " + state
            self.last_state = state
            return message
        
        # if nothing's changed it's pointless to update last_state
        else:
            return None
