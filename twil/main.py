from django.core.exceptions import ImproperlyConfigured
import twilio

class TwilioAccount:
    API_VERSION = '2010-04-01'
    CALLER_ID = None
    NUMBER = None
    SANDBOX_NUMBER = NUMBER
    SID = None
    TOKEN = None
    
    class URLS:
        BASE = None
        MESSAGES = None
    
    def __init__(self, sid, d):
        self.API_VERSION = d.get('api', '2010-04-01')
        self.CALLER_ID = d.get('caller_id', None)
        self.NUMBER = d.get('number', None)
        self.SANDBOX_NUMBER = d.get('sandbox_number', self.NUMBER)
        self.SID = sid
        self.TOKEN = d.get('token', None)
        
        if not self.CALLER_ID:
            raise ImproperlyConfigured('You must specify a TWILIO_CALLER_ID in your settings')
        
        if not self.NUMBER:
            raise ImproperlyConfigured('You must specify your TWILIO_NUMBER in your settings')
        
        if not self.SID:
            raise ImproperlyConfigured("You must provide your TWILIO_SID.")
        
        if not self.TOKEN:
            raise ImproperlyConfigured("You must provide your TWILIO_TOKEN.")
        
        self.URLS.BASE = '/%s/Accounts/%s/' %(self.API_VERSION, self.SID)
        self.URLS.MESSAGES = self.URLS.BASE + 'SMS/Messages'
        
        # A common twilio account to be used accross the site.  
        self.twilio = twilio.Account(self.SID, self.TOKEN)