""" Required Settings for you to set to connect 
to Twillio in your django settings file """


DEFAULT_ACCOUNT = "Your Default Twilio Account SID"
TWILIO_SETTINGS = {
   "Account SID":{
        'api' : '2010-04-01',
        'caller_id' : '123-456-7890',
        'number' : '123-456-7890',
        'sandbox_number' : '1234567890',
        'token' : 'Your Token',
      }
   # Add as many accounts as you have
}

