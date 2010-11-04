from twil import models
from twil.const import DEFAULT
import logging
import traceback

log = logging.getLogger('twil.sms')

def send_sms(phone_number, text, fail_silently = False, account = DEFAULT):
    d = { 
        'To' : phone_number, 
        'From' : account.NUMBER, 
        'Body' : text, 
        }
    try:
        r = account.twilio.request(account.URLS.MESSAGES, 'POST', d)
        return models.Sms.objects.parse_message(r)
    except Exception, e:
        if not fail_silently:
            raise e
        log.error(traceback.format_exc())
