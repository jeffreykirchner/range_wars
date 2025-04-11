print("Update chat period")

from main.models import Session
import random
import string

#get session number from command line argument
session_number = 8

session = Session.objects.get(id=session_number)

#filter for type equals "chat", "range", "cents" or "help_doc"
session_events = session.session_events.filter(type__in=["chat", "range", "cents", "help_doc"]).order_by('timestamp')[3]
first_event_time = session_events.timestamp

last_time_stamp = None
last_period_number = None

for i in session.session_events.filter(type__in=["chat", "range", "cents", "help_doc"]).order_by('timestamp'):
    #store seconds since first event in period
    
    if i.type == "chat":
        i.period_number = (i.timestamp - last_time_stamp).total_seconds() + last_period_number
        i.save()
    
    last_time_stamp = i.timestamp
    last_period_number = i.period_number

print(f"Fourth event time: {first_event_time}")
