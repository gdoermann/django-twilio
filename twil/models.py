from django.db import models
from twil.const import DEFAULT, ACCOUNTS
from twil.exceptions import InvalidMessage, TwilioException, RestException, \
    UnknownResponseError
from twil.util import response_dict, twilio_date
from xml.etree import ElementTree
import logging
import traceback
log = logging.getLogger('twil.models')

class SmsManager(models.Manager):
    def update_sid(self, sid):
        sms = self.get(sid = sid)
        sms.update()
    
    def pull(self, 
             from_number = None, 
             to_number = None, 
             date = None, 
             date_operator = '=', 
             page = None, 
             max_pages = None,
             account = DEFAULT):
        """ Perform a GET on the messages url for the account specified,
        process each message and save the message back to the database
        if it does not already exist.
        """
        url = account.URLS.MESSAGES
        on_page = 0
        data = []
        if from_number:
            data.append('From=%s' %(from_number))
        if to_number:
            data.append('To=%s' %(to_number))
        if date:
            date_str = date.strftime('%Y-%m-%d')
            data.append('DateSent%s%s' %(date_operator, date_str))
        if page:
            on_page = page
        if page is not None and max_pages is None:
            max_pages = 1
        if data:
            url = '%s?%s' %(url, '&'.join(data))
        
        response = account.twilio.request(url, 'GET')
        root = ElementTree.fromstring(response)
        tree = list(root)[0]
        
        def get_next_page(tree):
            return tree.attrib.get('nextpageuri')
        messages = []
        if tree.tag.lower() == 'smsmessages':
            new_tree, msgs = self._handle_messages(response = response)
            messages += msgs
            next_page = get_next_page(new_tree)
            while next_page and on_page < max_pages:
                on_page += 1
                new_tree, msgs = self._handle_messages(uri = next_page)
                messages += msgs
                next_page = get_next_page(new_tree)
        elif tree.tag.lower() == 'smsmessage':
            messages.append(self.parse_message(tree))
        elif tree.tag.lower() == 'restexception':
            raise RestException(tree)
        else:
            raise UnknownResponseError(tree)
        return messages
    
    def _handle_messages(self, uri = None, response = None, account = DEFAULT):
        """ Handle multiple messages from either a uri or from a response """
        if response is None:
            assert(uri)
            response = account.twilio.request(uri, 'GET')
        root = ElementTree.fromstring(response)
        tree = list(root)[0]
        messages = []
        for msg in list(tree):
            messages.append(self.parse_message(msg))
        return tree, messages
    
    def parse_message(self, tree, commit = True):
        """ Parse the message response from twilio """
        sms = self.model()
        if isinstance(tree, basestring):
            tree = ElementTree.fromstring(tree)[0]
        sms.parse(tree)
        try:
            sms = self.get(sid = sms.sid)
            sms.parse(tree)
        except self.model.DoesNotExist:
            pass
        if commit:
            sms.save()
        return sms
    
    def pull_recieved(self, **kwargs):
        """ Pull messages sent TO your number """
        account = kwargs.get('account', DEFAULT)
        kwargs['to_number'] = account.NUMBER
        return self.pull(**kwargs)
    
    def send(self, phone_number, text, fail_silently = False, account = DEFAULT):
        """ Send message to number and save message to database """
        d = { 
            'To' : phone_number, 
            'From' : account.NUMBER, 
            'Body' : text, 
            }
        try:
            r = account.twilio.request(account.URLS.MESSAGES, 'POST', d)
            return self.parse_message(r)
        except Exception, e:
            if not fail_silently:
                raise e
            log.error(traceback.format_exc())

class Sms(models.Model):
    QUEUED = 0
    SENDING = 1
    SENT = 2
    FAILED = 3
    RECIEVED = 4
    
    STATUS_CHOICES = (
          (QUEUED, 'queued'),
          (SENDING, 'sending'), 
          (SENT, 'sent'),
          (FAILED, 'failed'),
          (RECIEVED, 'received')
          )
    
    OUTBOUND = 0
    INCOMING = 1
    OUTBOUND_CALL = 2
    OUTBOUND_REPLY = 3
    
    DIRECTION_CHOICES = (
         (OUTBOUND, 'outbound-api'),
         (INCOMING, 'incoming'),
         (INCOMING, 'inbound'),
         (OUTBOUND_CALL, 'outbound-call'),
         (OUTBOUND_REPLY, 'outbound-reply'),
         )
    
    sid = models.CharField(max_length = 100)
    account_sid = models.CharField(max_length = 100)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    sent = models.DateTimeField()
    to_number = models.CharField(max_length = 30)
    from_number = models.CharField(max_length = 30)
    body = models.CharField(max_length = 160)
    status = models.IntegerField(choices = STATUS_CHOICES, default= QUEUED)
    price = models.DecimalField(decimal_places = 3, max_digits = 30, null=True)
    direction = models.IntegerField(choices = DIRECTION_CHOICES, default = OUTBOUND)
    
    objects = SmsManager()
    
    def parse(self, msg):
        # Any attributes in the message will be set on the object
        if isinstance(msg, basestring):
            msg = ElementTree.fromstring(msg)
            if msg.tag.lower() == 'twilioresponse':
                msg = list(msg)[0]
                if msg.tag.lower() == 'restexception':
                    raise RestException(msg)
        if not msg.tag.lower() == 'smsmessage':
            raise InvalidMessage("Invalid SMS Message")
        d = response_dict(msg)
        
        def map_item(attr, name, parser = None):
            if not d.has_key(name):
                return
            s = d[name]
            if parser:
                s = parser(s)
            setattr(self, attr, s)
        
        map_item('sid', 'Sid')
        map_item('account_sid', 'AccountSid')
        map_item('to_number', 'To')
        map_item('from_number', 'From')
        map_item('body', 'Body')
        map_item('status', 'Status')
        map_item('sid', 'Sid')
        map_item('sid', 'Sid')
        map_item('created', 'DateCreated', twilio_date)
        map_item('updated', 'DateUpdated', twilio_date)
        map_item('sent', 'DateSent', twilio_date)
        map_item('status', 'Status', self.parse_status)
        map_item('direction', 'Direction', self.parse_direction)
    
    def parse_status(self, status):
        for i, s in self.STATUS_CHOICES:
            if status.lower() == s.lower():
                self.status = i
                return i
        raise TwilioException('Invalid Status: %s' %(str(status)))
    
    def parse_direction(self, direction):
        for i, s in self.DIRECTION_CHOICES:
            if direction.lower() == s.lower():
                self.direction = i
                return i
        raise TwilioException('Invalid Direction: %s' %(str(direction)))
    
    @property
    def uri(self):
        URLS = ACCOUNTS[self.account_sid].URLS
        return URLS.MESSAGES + '/%s' %(self.sid)
    
    def update(self, commit= True, account = DEFAULT):
        r = account.twilio.request(self.uri, 'GET')
        self.parse(r)
        if commit:
            self.save()
    
    def __unicode__(self):
        return self.sid
    
    class Meta:
        get_latest_by = 'created'
