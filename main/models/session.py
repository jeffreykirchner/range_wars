'''
session model
'''

from datetime import datetime
from tinymce.models import HTMLField
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal

import logging
import uuid
import csv
import io
import json
import random
import re
import string

from django.conf import settings

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

import main

from main.models import ParameterSet

from main.globals import ExperimentPhase
from main.globals import round_half_away_from_zero
from main.globals import round_up

#experiment sessoin
class Session(models.Model):
    '''
    session model
    '''
    parameter_set = models.OneToOneField(ParameterSet, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_a")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="sessions_b")

    title = models.CharField(max_length=300, default="*** New Session ***")    #title of session
    start_date = models.DateField(default=now)                                 #date of session start

    channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    id_string = models.CharField(max_length=6, unique=True, null=True, blank=True)                       #unique string for session to auto login subjects by id

    controlling_channel = models.CharField(max_length = 300, default="")         #channel controlling session

    started =  models.BooleanField(default=False)                                #starts session and filll in session
   
    shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    invitation_text = HTMLField(default="", verbose_name="Invitation Text")       #inviataion email subject and text
    invitation_subject = HTMLField(default="", verbose_name="Invitation Subject")

    world_state = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True, verbose_name="Current Session State")       #world state at this point in session

    replay_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True, verbose_name="Replay Data")   

    period_block_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True, verbose_name="Period Block Data")      #period block data

    website_instance_id = models.CharField(max_length=300, default="", verbose_name="Website Instance ID", null=True, blank=True)           #website instance from azure

    soft_delete =  models.BooleanField(default=False)                             #hide session if true

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def creator_string(self):
        return self.creator.email
    creator_string.short_description = 'Creator'

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_date']
        

    def get_start_date_string(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%#m/%#d/%Y")

    def get_group_channel_name(self):
        '''
        return channel name for group
        '''
        page_key = f"session-{self.id}"
        room_name = f"{self.channel_key}"
        return  f'{page_key}-{room_name}'
    
    def send_message_to_group(self, message_type, message_data):
        '''
        send socket message to group
        '''
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.get_group_channel_name(),
                                                {"type" : message_type,
                                                 "data" : message_data})

    def start_experiment(self):
        '''
        setup and start experiment
        '''

        self.started = True
        self.start_date = datetime.now()
        
        session_periods = []

        for i in self.parameter_set.parameter_set_periodblocks_a.all():
            round_number = 1
            for j in range(i.period_start, i.period_end+1):
                session_periods.append(main.models.SessionPeriod(session=self, 
                                                                parameter_set_periodblock=i,
                                                                period_number=j,
                                                                round_number=round_number))
                round_number += 1
        
        main.models.SessionPeriod.objects.bulk_create(session_periods)

        self.save()

        for i in self.session_players.all():
            i.start()

        self.setup_world_state()
        self.setup_summary_data()

    def setup_summary_data(self):
        '''
        setup summary data
        '''

        session_players = self.session_players.values('id','parameter_set_player__id').all()

        summary_data = {}
        
        for i in session_players:
            i_s = str(i["id"])
            summary_data[i_s] = {}

            summary_data_player = summary_data[i_s]
            summary_data_player["earnings"] = 0
            summary_data_player["cherries_harvested"] = 0

            summary_data_interactions = {}
            for j in session_players:
                j_s = str(j["id"])
                summary_data_interactions[j_s] = {"cherries_i_took":0, 
                                                  "cherries_i_sent":0,
                                                  "cherries_they_took":0, 
                                                  "cherries_they_sent":0,}
            
            summary_data_player["interactions"] = summary_data_interactions
                
        self.session_periods.all().update(summary_data=summary_data)

    def setup_world_state(self):
        '''
        setup world state
        '''
        parameter_set = self.parameter_set.json()

        self.world_state = {"last_update":str(datetime.now()), 
                            "last_store":str(datetime.now()),
                            "session_players":{},
                            "session_players_order":[],
                            "current_period":1,
                            "current_round":1,
                            "number_of_periods":self.session_periods.all().count(),
                            "groups":{},
                            "current_experiment_phase":ExperimentPhase.INSTRUCTIONS if self.parameter_set.show_instructions else ExperimentPhase.RUN,
                            "current_period_block":parameter_set["parameter_set_periodblocks_order"][0] if parameter_set["parameter_set_periodblocks_order"] else None,
                            "period_blocks":{},
                            "time_remaining":self.parameter_set.period_length,
                            "timer_running":False,
                            "timer_history":[],
                            "started":True,
                            "finished":False,
                            "session_periods":{str(i.id) : i.json() for i in self.session_periods.all()},
                            "session_periods_order" : list(self.session_periods.all().values_list('id', flat=True)),}
        
        inventory = {str(i):0 for i in list(self.session_periods.all().values_list('id', flat=True))}

        #session periods
        for i in self.world_state["session_periods"]:
            self.world_state["session_periods"][i]["consumption_completed"] = False

        #session players
        for i in self.session_players.prefetch_related('parameter_set_player').all().values('id', 
                                                                                            'parameter_set_player__start_x',
                                                                                            'parameter_set_player__start_y',
                                                                                            'parameter_set_player__id' ):
            v = {}

            v['range_start'] = 1
            v['range_end'] = 1
            v['range_middle'] = 1
            v['revenues'] = []             #revenue share for each value
            v['overlaps'] = {}             #overlaps totals with other group members
            v['earnings'] = 0              #total earnings
            v['cost'] = 0                  #cost for each location in range 
            v['total_cost'] = 0            #total cost
            v['total_revenue'] = 0         #total revenue 
            v['total_profit'] = 0          #total profit
            v['total_loss'] = 0            #total loss
            v['group_number'] = 0          #current group number
            v['parameter_set_player_id'] = i['parameter_set_player__id']
            
            self.world_state["session_players"][str(i['id'])] = v
            self.world_state["session_players_order"].append(i['id'])
        

        #period blocks
        self.period_block_data = {}
        for i in parameter_set["parameter_set_periodblocks"]:
            #world state
            self.world_state["period_blocks"][str(i)] = {"id":i, 
                                                         "phase":"start",
                                                         "session_players":{}}
            
            #period block data
            self.period_block_data[str(i)] = {"session_players":{}}

            for p in self.world_state["session_players"]:
                self.world_state["period_blocks"][str(i)]["session_players"][p] = {"ready":False}

                self.period_block_data[str(i)]["session_players"][p] = {"cents_sent":{},
                                                                        "chat_messages_sent":0,
                                                                        "total_revenue":0,
                                                                        "total_cost":0,
                                                                        "total_profit":0,}
        
        if not self.started:
            self.save()
            return
        
        #test code
        # range_start = 0
        # range_end = 25
        # min_range = 0
        # max_range = 90
        # for i in self.world_state["session_players"]:
        #     self.world_state["session_players"][i]["range_start"] = range_start
        #     self.world_state["session_players"][i]["range_end"] = range_end

        #     range_start += -5
        #     range_end += 30

        #     if range_start < min_range:
        #         range_start = min_range
        #     if range_start > max_range:
        #         range_start = max_range
        #     if range_end > max_range:
        #         range_end = max_range
        #     if range_end < min_range:
        #         range_end = min_range
        
        # for i in self.world_state["session_players"]:
        #     self.world_state["session_players"][i]["range_start"] = 3
        #     break

        self.world_state = self.update_treatment(self.world_state, self.parameter_set.json())
        self.world_state = self.update_revenues(self.world_state, self.parameter_set.json())

        self.save()

    def update_treatment(self, world_state, parameter_set):
        '''
        update treatment
        '''
        
        # world_state = self.world_state
        # parameter_set = self.parameter_set.json()
        period_block = parameter_set["parameter_set_periodblocks"][str(world_state["current_period_block"])]
        treatment = parameter_set["parameter_set_treatments"][str(period_block["parameter_set_treatment"])]
        costs = treatment["costs"].split(",")
        world_state["groups"] = {}
        world_state["group_map"] = {}      #maps group number and position to session player id 

        for i in world_state["session_players"]:
            session_player = world_state["session_players"][i]
            parameter_set_player = parameter_set["parameter_set_players"][str(session_player["parameter_set_player_id"])]
            parameter_set_player_group = parameter_set_player["parameter_set_player_groups"][str(period_block["id"])]

            session_player["cost"] = costs[parameter_set_player_group["position"]-1]
            session_player["revenues"] = {str(i): 0 for i in treatment["values"].split(",")}
            session_player["range_start"] = parameter_set_player_group["start_box"]
            session_player["range_end"] = parameter_set_player_group["start_box"]
            session_player["range_middle"] =  (Decimal(session_player["range_start"]) + Decimal(session_player["range_end"]) + 1) / 2

            #setup groups
            if str(parameter_set_player_group["group_number"]) not in world_state["groups"]:
                world_state["groups"][str(parameter_set_player_group["group_number"])] = []
            
            world_state["group_map"][str(parameter_set_player_group["group_number"]) + "-" + str(parameter_set_player_group["position"])] = i

            world_state["groups"][str(parameter_set_player_group["group_number"])].append(int(i))
            session_player["group_number"] = parameter_set_player_group["group_number"]
        
        return world_state

    def update_revenues(self, world_state, parameter_set):
        '''
        update revenues
        '''
        logger = logging.getLogger(__name__)

        # world_state = self.world_state
        # parameter_set = self.parameter_set.json()
        period_block = parameter_set["parameter_set_periodblocks"][str(world_state["current_period_block"])]
        treatment = parameter_set["parameter_set_treatments"][str(period_block["parameter_set_treatment"])]
        values = treatment["values"].split(",")
        box_value = float(treatment["range_width"]) / len(values)

        #reset revenues to zero for all values
        for i in world_state["session_players"]:
            world_state["session_players"][i]["revenues"] = {str(i): 0 for i in values}
            world_state["session_players"][i]["overlaps"] = {}

        #update revenues for each group at each value
        for g in world_state["groups"]:
            group = world_state["groups"][g]

            for t in range(len(values)):
                players_in_range = []

                for p in group:
                    session_player = world_state["session_players"][str(p)]

                    if session_player["range_start"] <= t <= session_player["range_end"]:
                        players_in_range.append(p)

                for p in players_in_range:
                    session_player = world_state["session_players"][str(p)]
                    session_player["revenues"][values[t]] = 1/len(players_in_range) * box_value

                    #store overlap totals
                    for o in players_in_range:
                        if o == p:
                            continue

                        if str(o) not in session_player["overlaps"]:
                            session_player["overlaps"][str(o)] = 0

                        session_player["overlaps"][str(o)] += 1
        
        #update total revenue for each player
        for i in world_state["session_players"]:
            session_player = world_state["session_players"][i]
            session_player["total_revenue"] = 0
            session_player["total_loss"] = 0
            session_player["total_cost"] = (session_player["range_end"] - session_player["range_start"] + 1) * float(session_player["cost"]) * box_value
            session_player["total_cost"] = round_half_away_from_zero(Decimal(session_player["total_cost"]), 2)

            for r in range(session_player["range_start"], session_player["range_end"]+1):
                value = values[r]
                revenue = session_player["revenues"][values[r]]

                ajusted_revenue = float(value) * float(revenue)
                session_player["total_revenue"] += ajusted_revenue

                #check for losses
                if ajusted_revenue - (float(session_player["cost"]) * box_value) < 0:
                    session_player["total_loss"] += (ajusted_revenue - (float(session_player["cost"]) * box_value))

            session_player["total_revenue"] = round_half_away_from_zero(Decimal(session_player["total_revenue"]), 2)
            session_player["total_profit"] = session_player["total_revenue"] - session_player["total_cost"]
        
        return world_state

    def reset_experiment(self):
        '''
        reset the experiment
        '''
        self.started = False

        #self.time_remaining = self.parameter_set.period_length
        #self.timer_running = False
        self.world_state ={}
        self.period_block_data = {}
        self.save()

        for p in self.session_players.all():
            p.reset()

        self.session_periods.all().delete()
        self.session_events.all().delete()

        # self.parameter_set.setup()
    
    def reset_connection_counts(self):
        '''
        reset connection counts
        '''
        self.session_players.all().update(connecting=False, connected_count=0)
    
    def get_current_session_period(self):
        '''
        return the current session period
        '''
        if not self.started:
            return None

        return self.session_periods.get(period_number=self.world_state["current_period"])

    async def aget_current_session_period(self):
        '''
        return the current session period
        '''
        if not self.started:
            return None

        return await self.session_periods.aget(period_number=self.world_state["current_period"])
    
    def update_player_count(self):
        '''
        update the number of session players based on the number defined in the parameterset
        '''

        self.session_players.all().delete()
    
        for count, i in enumerate(self.parameter_set.parameter_set_players.all()):
            new_session_player = main.models.SessionPlayer()

            new_session_player.session = self
            new_session_player.parameter_set_player = i
            new_session_player.player_number = i.player_number

            new_session_player.save()

    def user_is_owner(self, user):
        '''
        return turn is user is owner or an admin
        '''

        if user.is_staff:
            return True

        if user==self.creator:
            return True
        
        return False

    def get_download_summary_csv(self):
        '''
        return data period summary in csv format
        '''
        logger = logging.getLogger(__name__)
        
        
        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            session_periods = self.session_periods.all()
            parameter_set = self.parameter_set.json()
            world_state = self.world_state
           
            top_row = ["Session ID", "Period", "Period Block", "Treatment", "Client #", "Group", "Position", "Label", 
                       "Range Start", "Range End", "Range Middle", 
                       "Total Cost", "Total Revenue", "Total Profit", "Total Loss"]
            
            for player_number, player_id in enumerate(world_state["session_players"]):               
                top_row.append(f'Overlap #{player_number+1}')
            
            writer.writerow(top_row)

            
            # logger.info(parameter_set_players)

            for session_period in session_periods:
                summary_data = session_period.summary_data

                if not summary_data.get("session_players", False):
                    continue

                parameter_set_periodblock = parameter_set["parameter_set_periodblocks"][str(session_period.parameter_set_periodblock.id)]
                parameter_set_treatment = parameter_set["parameter_set_treatments"][str(parameter_set_periodblock["parameter_set_treatment"])]

                for player_number, player_id in enumerate(summary_data["session_players"]):
                    
                    session_player = summary_data["session_players"][player_id]
                    parameter_set_player = parameter_set["parameter_set_players"][str(session_player["parameter_set_player_id"])]
                    parameter_set_player_group = parameter_set_player["parameter_set_player_groups"][str(parameter_set_periodblock["id"])] 

                    temp_row = [self.id, 
                                session_period.period_number, 
                                f'{parameter_set_periodblock["period_start"]} to {parameter_set_periodblock["period_end"]}',
                                parameter_set_treatment["id_label_pst"],
                                player_number+1,      
                                parameter_set_player_group["group_number"],
                                parameter_set_player_group["position"],
                                parameter_set_player["id_label"],
                                session_player["range_start"],
                                session_player["range_end"],
                                session_player["range_middle"],
                                session_player["total_cost"],
                                session_player["total_revenue"],
                                session_player["total_profit"],
                                session_player["total_loss"]]
                    
                    for player_number, player_id in enumerate(world_state["session_players"]):
                        if player_id in session_player["overlaps"]:
                            temp_row.append(session_player["overlaps"][player_id])
                        else:
                            temp_row.append("")
                    
                    writer.writerow(temp_row)
                    
            v = output.getvalue()
            output.close()

        return v
    
    def get_download_period_block_csv(self):
        '''
        return data period block in csv format
        '''
        logger = logging.getLogger(__name__)
        
        #  {"cents_sent":{},
        #                                                                 "chat_messages_sent":0,
        #                                                                 "total_revenue":0,
        #                                                                 "total_cost":0,
        #                                                                 "total_profit":0,}
        
        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            top_row = ["Session ID", "Period Block", "Treatment", "Client #", "Group", "Position", "Label", 
                       "Chat Count", "Total Revenue", "Total Cost", "Total Profit"]

            for player_number, player_id in enumerate(self.world_state["session_players"]):
                top_row.append(f'Cents Sent #{player_number+1}')
            
            writer.writerow(top_row)

            parameter_set = self.parameter_set.json()

            for period_block_id in self.period_block_data:
                period_block = self.period_block_data[period_block_id]
                parameter_set_periodblock = parameter_set["parameter_set_periodblocks"][str(period_block_id)]
                parameter_set_treatment = parameter_set["parameter_set_treatments"][str(parameter_set_periodblock["parameter_set_treatment"])]

                for player_number, player_id in enumerate(period_block["session_players"]):
                    session_player = period_block["session_players"][player_id]
                    parameter_set_player = parameter_set["parameter_set_players"][str(self.world_state["session_players"][player_id]["parameter_set_player_id"])]
                    parameter_set_player_group = parameter_set_player["parameter_set_player_groups"][str(parameter_set_periodblock["id"])]

                    temp_row = [self.id,
                                f'{parameter_set_periodblock["period_start"]} to {parameter_set_periodblock["period_end"]}',
                                parameter_set_treatment["id_label_pst"],
                                player_number+1,      
                                parameter_set_player_group["group_number"],
                                parameter_set_player_group["position"],
                                parameter_set_player["id_label"],
                                session_player["chat_messages_sent"],
                                session_player["total_revenue"],
                                session_player["total_cost"],
                                session_player["total_profit"]]
                    
                    for player_number, player_id in enumerate(self.world_state["session_players"]):
                        if player_id in session_player["cents_sent"]:
                            temp_row.append(session_player["cents_sent"][player_id])
                        else:
                            temp_row.append("")

                    writer.writerow(temp_row)


            v = output.getvalue()
            output.close()

        return v
    
    def get_download_action_csv(self):
        '''
        return data actions in csv format
        '''
        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            writer.writerow(["Session ID", "Period", "Group", "Client #", "Label", "Action","Info (Plain)", "Info (JSON)", "Timestamp"])

            # session_events =  main.models.SessionEvent.objects.filter(session__id=self.id).prefetch_related('period_number', 'time_remaining', 'type', 'data', 'timestamp')
            # session_events = session_events.select_related('session_player')

            world_state = self.world_state
            parameter_set_players = {}
            for i in self.session_players.all().values('id','player_number','parameter_set_player__id_label'):
                parameter_set_players[str(i['id'])] = i

            session_players = {}
            for i in self.session_players.all().values('id','player_number','parameter_set_player__id_label'):
                session_players[str(i['id'])] = i

            for p in self.session_events.exclude(type="time").exclude(type="world_state").exclude(type='target_locations'):
                writer.writerow([self.id,
                                p.period_number, 
                                p.group_number, 
                                parameter_set_players[str(p.session_player_id)]["player_number"], 
                                parameter_set_players[str(p.session_player_id)]["parameter_set_player__id_label"], 
                                p.type, 
                                self.action_data_parse(p.type, p.data, session_players),
                                p.data, 
                                p.timestamp])
            
            v = output.getvalue()
            output.close()

        return v

    def action_data_parse(self, type, data, session_players):
        '''
        return plain text version of action
        '''

        if type == "chat":
            return  data["text"]
        elif type == "help_doc":
            return data
        elif type == "range":
            return f'{data["range_start"]} to {data["range_end"]}'
        elif type == "cents":
            return f'{data["amount"]} cent(s) to #{session_players[str(data["recipient"])]["player_number"]}'

        return ""
    
    def get_download_recruiter_csv(self):
        '''
        return data recruiter in csv format
        '''
        with io.StringIO() as output:

            writer = csv.writer(output)

            parameter_set_players = {}
            for i in self.session_players.all().values('id','student_id'):
                parameter_set_players[str(i['id'])] = i

            for p in self.world_state["session_players"]:
                writer.writerow([parameter_set_players[p]["student_id"],
                                 round_up(Decimal(self.world_state["session_players"][p]["earnings"])/100,2)])

            v = output.getvalue()
            output.close()

        return v
    
    def get_download_payment_csv(self):
        '''
        return data payments in csv format
        '''
        with io.StringIO() as output:

            writer = csv.writer(output)

            writer.writerow(['Session', 'Date', 'Player', 'Name', 'Student ID', 'Earnings'])

            # session_players = self.session_players.all()

            # for p in session_players:
            #     writer.writerow([self.id, self.get_start_date_string(), p.player_number,p.name, p.student_id, p.earnings/100])

            parameter_set_players = {}
            for i in self.session_players.all().values('id', 'player_number', 'name', 'student_id'):
                parameter_set_players[str(i['id'])] = i

            for p in self.world_state["session_players"]:
                writer.writerow([self.id,
                                 self.get_start_date_string(),
                                 parameter_set_players[p]["player_number"],
                                 parameter_set_players[p]["name"],
                                 parameter_set_players[p]["student_id"],
                                 self.world_state["session_players"][p]["earnings"]])

            v = output.getvalue()
            output.close()

        return v
    
    def json(self):
        '''
        return json object of model
        '''
                                                                      
        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "id_string":self.id_string,
            "parameter_set":self.parameter_set.json(),
            "session_periods":{i.id : i.json() for i in self.session_periods.all()},
            "session_periods_order" : list(self.session_periods.all().values_list('id', flat=True)),
            "session_players":{i.id : i.json(False) for i in self.session_players.all()},
            "session_players_order" : list(self.session_players.all().values_list('id', flat=True)),
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "world_state" : self.world_state,
            "collaborators" : {str(i.id):i.email for i in self.collaborators.all()},
            "collaborators_order" : list(self.collaborators.all().values_list('id', flat=True)),
            "creator" : self.creator.id,
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''
        
        return{
            "started":self.started,
            "parameter_set":self.parameter_set.get_json_for_subject(),

            "session_players":{i.id : i.json_for_subject(session_player) for i in self.session_players.all()},
            "session_players_order" : list(self.session_players.all().values_list('id', flat=True)),

            "session_periods":{i.id : i.json() for i in self.session_periods.all()},
            "session_periods_order" : list(self.session_periods.all().values_list('id', flat=True)),

            "world_state" : self.world_state,
        }
    
    def json_for_timer(self):
        '''
        return json object for timer update
        '''

        session_players = []

        return{
            "started":self.started,
            "session_players":session_players,
            "session_player_earnings": [i.json_earning() for i in self.session_players.all()]
        }
    
    def json_for_parameter_set(self):
        '''
        return json for parameter set setup.
        '''
        message = {
            "id" : self.id,
            "started": self.started,
        }
    
        return message
        
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()

@receiver(post_save, sender=Session)
def post_save_session(sender, instance, created, *args, **kwargs):
    '''
    after session is initialized
    '''
    if created:
        id_string = ''.join(random.choices(string.ascii_lowercase, k=6))

        while Session.objects.filter(id_string=id_string).exists():
            id_string = ''.join(random.choices(string.ascii_lowercase, k=6))

        instance.id_string = id_string
