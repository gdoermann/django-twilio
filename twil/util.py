from django.utils.datastructures import SortedDict
from xml.etree import ElementTree
import datetime

def response_dict(tree):
    if isinstance(tree, basestring):
        tree = ElementTree.fromstring(tree)
    d = SortedDict()
    for child in list(tree):
        if len(list(child)):
            d[child.tag] = response_dict(child)
        else:
            d[child.tag] = child.text
    return d

def twilio_date(d):
    parts = d.split()
    date_string = ' '.join(parts[:-1])
    format = "%a, %d %b %Y %H:%M:%S"
    return datetime.datetime.strptime(date_string, format)

def twilio_offset(d):
    parts = d.split()
    offset = parts[-1]
    return datetime.timedelta(hours = int(offset[:-2]), minutes = int(offset[-2:]))
