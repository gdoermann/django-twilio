from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from twil.main import TwilioAccount

tsettings = getattr(settings, 'TWILIO_SETTINGS', None)
if not tsettings:
    raise ImproperlyConfigured('You must specify your TWILIO_SETTINGS in your settings file.')

ACCOUNTS = {}
for sid, d in tsettings.items():
    ACCOUNTS[sid] = TwilioAccount(sid, d)

# This sets the default variables
SID = getattr(settings, 'DEFAULT_ACCOUNT', None)
try:
    DEFAULT = ACCOUNTS[SID]
except:
    DEFAULT = TwilioAccount(SID, tsettings[SID])
