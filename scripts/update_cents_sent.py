from main.models import Session
import random
import string
import logging

logger = logging.getLogger(__name__)
#get session number from command line argument
session_number = 8

session = Session.objects.get(id=session_number)

#add cents_set to all session_period data
for i in session.session_periods.all():
    summary_data = i.summary_data

    #add cents_set to session_players in summary data
    for j in summary_data["session_players"]:
        summary_data["session_players"][str(j)]["cents_sent"] = {}

    i.save()

#add cents_set to session_player_periods in summary data from session events
for i in session.session_events.filter(type="cents"):
    data = i.data
    session_period = session.session_periods.get(period_number=i.period_number)
    session_player = session_period.summary_data["session_players"][str(i.session_player.id)]

    if str(data["recipient"]) not in session_player["cents_sent"]:
        session_player["cents_sent"][str(data["recipient"])] = 0

    session_player["cents_sent"][str(data["recipient"])] += data["amount"]


    session_period.save()
   