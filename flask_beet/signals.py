import blinker

""" Signals allow to subscribe to certain events from outside this extensions
"""

signals = blinker.Namespace()

beet_logged_in = signals.signal("beet-logged-in")
beet_onboarding = signals.signal("beet-onboarding")
