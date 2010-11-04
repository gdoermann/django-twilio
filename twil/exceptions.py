class TwilioException(Exception):
	DEFAULT_MSG = 'Twilio Error'
	def __init__(self, msg = None, *args, **kwargs):
		if msg is None:
			msg = self.DEFAULT_MSG
		super(TwilioException, self).__init__(msg, *args, **kwargs)

class InvalidMessage(TwilioException):
	DEFAULT_MSG = 'Invalid SMS Message'

class RestException(TwilioException):
	def __init__(self, tree, *args, **kwargs):
		l = list(tree)
		self.status = l[0].text
		super(RestException, self).__init__(l[1].text, *args, **kwargs)

class UnknownResponseError(TwilioException):
	DEFAULT_MSG = 'Unknown Response'