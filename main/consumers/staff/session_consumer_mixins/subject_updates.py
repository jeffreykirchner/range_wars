
import logging
import math
import json

from datetime import datetime, timedelta
from decimal import Decimal

from django.utils.html import strip_tags

from main.models import SessionPlayer
from main.models import Session
from main.models import SessionEvent
from main.globals import is_positive_integer

from main.globals import ExperimentPhase

import main

class SubjectUpdatesMixin():
    '''
    subject updates mixin for staff session consumer
    '''

    async def chat(self, event):
        '''
        take chat from client
        '''    
        if self.controlling_channel != self.channel_name:
            return    
       
        logger = logging.getLogger(__name__) 
        # logger.info(f"take chat: Session ")
        
        status = "success"
        error_message = ""
        player_id = None

        if status == "success":
            try:
                player_id = self.session_players_local[event["player_key"]]["id"]
                event_data = event["message_text"]
            except:
                logger.warning(f"chat: invalid data, {event['message_text']}")
                status = "fail"
                error_message = "Invalid data."
        
        target_list = [player_id]

        if status == "success":
            if not self.world_state_local["started"] or \
            self.world_state_local["finished"] or \
            self.world_state_local["current_experiment_phase"] != ExperimentPhase.RUN:
                logger.warning(f"take chat: failed, session not started, finished, or not in run phase")
                status = "fail"
                error_message = "Session not started."
        
        result = {"status": status, "error_message": error_message}
        result["player_id"] = player_id

        if status == "success":
            session_player = self.world_state_local["session_players"][str(player_id)]
            
            result["text"] = strip_tags(event_data["text"])
            
            self.session_events.append(SessionEvent(session_id=self.session_id, 
                                                    session_player_id=result["player_id"],
                                                    type="chat",
                                                    group_number=session_player["group_number"],
                                                    data=result))
            
            target_list = self.world_state_local["groups"][str(session_player["group_number"])]

            chat = {"session_player": player_id,
                    "message": result["text"],
                    "type": "chat"}
            
            async for s in SessionPlayer.objects.filter(id__in=target_list):
                await s.push_chat_display_history(chat)
            
            #store chat into period block data
            session = await Session.objects.aget(id=self.session_id)
            session.period_block_data[str(self.world_state_local["current_period_block"])]["session_players"][str(player_id)]["chat_messages_sent"] += 1
            await session.asave(update_fields=["period_block_data"])

        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, 
                                send_to_group=True, target_list=target_list)

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        event_data = json.loads(event["group_data"])

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        logger = logging.getLogger(__name__) 
        event_data = event["data"]

        #update not from a client
        if event_data["value"] == "fail":
            if not self.session_id:
                self.session_id = event["session_id"]

            # logger.info(f"update_connection_status: event data {event}, channel name {self.channel_name}, group name {self.room_group_name}")

            if "session" in self.room_group_name:
                #connection from staff screen
                if event["connect_or_disconnect"] == "connect":
                    # session = await Session.objects.aget(id=self.session_id)
                    self.controlling_channel = event["sender_channel_name"]

                    if self.channel_name == self.controlling_channel:
                        # logger.info(f"update_connection_status: controller {self.channel_name}, session id {self.session_id}")
                        await Session.objects.filter(id=self.session_id).aupdate(controlling_channel=self.controlling_channel) 
                        await self.send_message(message_to_self=None, message_to_group={"controlling_channel" : self.controlling_channel},
                                                message_type="set_controlling_channel", send_to_client=False, send_to_group=True)
                else:
                    #disconnect from staff screen
                    pass                   
            return
        
        subject_id = event_data["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        event_data["result"]["name"] = session_player.name
        event_data["result"]["student_id"] = session_player.student_id
        event_data["result"]["current_instruction"] = session_player.current_instruction
        event_data["result"]["survey_complete"] = session_player.survey_complete
        event_data["result"]["instructions_finished"] = session_player.instructions_finished

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_set_controlling_channel(self, event):
        '''
        only for subject screens
        '''
        pass

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        event_data = event["staff_data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_survey_complete(self, event):
        '''
        send survey complete update
        '''
        event_data = event["data"]

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def range(self, event):
        '''
        take range from client
        '''

        if self.controlling_channel != self.channel_name:
            return    
       
        logger = logging.getLogger(__name__) 

        status = "success"
        error_message = ""
        player_id = None
        
        try:
            player_id = self.session_players_local[event["player_key"]]["id"]
            event_data = event["message_text"]
        except:
            logger.warning(f"take_range: invalid data, {event['message_text']}")
            status = "fail"

        if status == "success":
            period_block = self.parameter_set_local["parameter_set_periodblocks"][str(self.world_state_local["current_period_block"])] 
            treatment =  self.parameter_set_local["parameter_set_treatments"][str(period_block["parameter_set_treatment"])]
            values = treatment["values"].split(",")
            session_player = self.world_state_local["session_players"][str(player_id)]
            parameter_set_player = self.parameter_set_local["parameter_set_players"][str(session_player["parameter_set_player_id"])]
            parameter_set_player_group = parameter_set_player["parameter_set_player_groups"][str(period_block["id"])]

            range_start = event_data["range_start"]
            range_end = event_data["range_end"]
            range_middle = (Decimal(range_start) + Decimal(range_end) + 1) / 2

            if range_start < 0 or \
               range_end < 0 or \
               range_start > len(values)-1 or \
               range_end > len(values)-1 or \
               range_start > range_end:
                status = "fail"
                error_message = "Invalid range."
                logger.warning(f"take_range: invalid range, {event_data}")

        #check if range is valid given the currrent treatment
        if status == "success":
            if treatment["preserve_order"]:
                group_number = parameter_set_player_group["group_number"]
                position = parameter_set_player_group["position"]

                left_1_session_player_id = self.world_state_local["group_map"].get(str(group_number) + "-" + str(position-1))
                left_2_session_player_id = self.world_state_local["group_map"].get(str(group_number) + "-" + str(position-2))
                right_1_session_player_id = self.world_state_local["group_map"].get(str(group_number) + "-" + str(position+1))
                right_2_session_player_id = self.world_state_local["group_map"].get(str(group_number) + "-" + str(position+2))
                
                #check if start range is <= left 2 range end
                if left_2_session_player_id:
                    left_2_range_start = self.world_state_local["session_players"][str(left_2_session_player_id)]["range_end"]
                    if range_start <= left_2_range_start:
                        left_2_parameter_set_player = self.parameter_set_local["parameter_set_players"][str(self.world_state_local["session_players"][str(left_2_session_player_id)]["parameter_set_player_id"])]
                        status = "fail"
                        error_message = f"Your range cannot overlap with {left_2_parameter_set_player['id_label']}'s."
                
                #check if end range >= right 2 range start
                if right_2_session_player_id:
                    right_2_range_end = self.world_state_local["session_players"][str(right_2_session_player_id)]["range_start"]
                    if range_end >= right_2_range_end:
                        right_2_parameter_set_player = self.parameter_set_local["parameter_set_players"][str(self.world_state_local["session_players"][str(right_2_session_player_id)]["parameter_set_player_id"])]
                        status = "fail"
                        error_message = f"Your range cannot overlap with {right_2_parameter_set_player['id_label']}'s."

                #check if middle range is < left 1 middle range
                if left_1_session_player_id:
                    left_1_range_middle = self.world_state_local["session_players"][str(left_1_session_player_id)]["range_middle"]
                    if Decimal(range_middle) < Decimal(left_1_range_middle):
                        left_1_parameter_set_player = self.parameter_set_local["parameter_set_players"][str(self.world_state_local["session_players"][str(left_1_session_player_id)]["parameter_set_player_id"])]
                        status = "fail"
                        error_message = f"Your mid-range cannot be lower than {left_1_parameter_set_player['id_label']}'s."
                
                #check if middle range is > right 1 middle range
                if right_1_session_player_id:
                    right_1_range_middle = self.world_state_local["session_players"][str(right_1_session_player_id)]["range_middle"]
                    if Decimal(range_middle) > Decimal(right_1_range_middle):
                        right_1_parameter_set_player = self.parameter_set_local["parameter_set_players"][str(self.world_state_local["session_players"][str(right_1_session_player_id)]["parameter_set_player_id"])]
                        status = "fail"
                        error_message = f"Your mid-range cannot be higher than {right_1_parameter_set_player['id_label']}'s."

        result = {"status": status, 
                  "error_message": error_message}
        
        if status == "success":
            period_block = self.world_state_local["period_blocks"][str(self.world_state_local["current_period_block"])]
            
            period_block["session_players"][str(player_id)]["ready"] = True

            session_player["range_start"] = range_start
            session_player["range_end"] = range_end
            session_player["range_middle"] = range_middle

            result["player_id"] = player_id
            result["range_start"] = range_start
            result["range_end"] = range_end
            result["range_middle"] = range_middle

            self.session_events.append(SessionEvent(session_id=self.session_id, 
                                                    session_player_id=player_id,
                                                    group_number=session_player["group_number"],
                                                    type=event['type'],
                                                    period_number=self.world_state_local["current_period"],                                                   
                                                    data=result))
        
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, 
                                send_to_group=True, target_list=[player_id])
            
    
    async def update_range(self, event):
        '''
        send survey complete update
        '''
        event_data = json.loads(event["group_data"])

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def cents(self, event):
        '''
        one player sends cents to another
        '''

        if self.controlling_channel != self.channel_name:
            return    
       
        logger = logging.getLogger(__name__) 

        status = "success"
        error_message = ""
        player_id = None
        text = ""

        try:
            player_id = self.session_players_local[event["player_key"]]["id"]
            event_data = event["message_text"]
            amount = event_data["amount"]
            recipient = event_data["recipient"]
        except:
            logger.warning(f"take_cents: invalid data, {event['message_text']}")
            error_message = "Invalid data."
            status = "fail"

        session_player_source = self.world_state_local["session_players"][str(player_id)]
        target_list = [player_id]

        #check amount
        if status == "success":
            if not is_positive_integer(amount):
                status = "fail"
                error_message = "Invalid amount."
            elif amount <= 0:
                status = "fail"
                error_message = "Amount must be positive."
            elif amount > 200:
                status = "fail"
                error_message = "You may transfer at most 200 cents at a time."
                
        #check recipient
        if status == "success":
            if not is_positive_integer(recipient):
                status = "fail"
                error_message = "Invalid recipient."
        
        #check if player has enough cents
        if status == "success":
            if Decimal(session_player_source["earnings"]) < amount:
                status = "fail"
                error_message = "Insufficient funds."
            
        if status == "success":
            session_player_recipient = self.world_state_local["session_players"][str(recipient)]

            session_player_source["earnings"] = Decimal(session_player_source["earnings"]) - amount
            session_player_recipient["earnings"] = Decimal(session_player_recipient["earnings"]) + amount

            parameter_set_player_source = self.parameter_set_local["parameter_set_players"][str(session_player_source["parameter_set_player_id"])]
            parameter_set_player_recipient = self.parameter_set_local["parameter_set_players"][str(session_player_recipient["parameter_set_player_id"])]
           
            text = f"<span style='color:{parameter_set_player_source['hex_color']}'>{parameter_set_player_source['id_label']}</span> \
                      transferred {amount} cent{'s' if amount>1 else ""} to \
                    <span style='color:{parameter_set_player_recipient['hex_color']}'>{parameter_set_player_recipient['id_label']}</span>."

           
            
            target_list = self.world_state_local["groups"][str(session_player_source["group_number"])]

            # store into chat history
            chat = {"session_player": player_id,
                    "message": text,
                    "type": "cents"}
        
            async for s in SessionPlayer.objects.filter(id__in=target_list):
                await s.push_chat_display_history(chat)

            #store cents into period block data
            session = await Session.objects.aget(id=self.session_id)

            pbd = session.period_block_data[str(self.world_state_local["current_period_block"])]["session_players"][str(player_id)]["cents_sent"]
           
            if str(recipient) in pbd:
                pbd[str(recipient)] += amount
            else:
                pbd[str(recipient)] = amount

            await session.asave(update_fields=["period_block_data"])
        
        result = {"status": status, 
                  "player_id": player_id,
                  "amount": amount,
                  "recipient": recipient,
                  "text": text,
                  "error_message": error_message}

        if status == "success":
             self.session_events.append(SessionEvent(session_id=self.session_id, 
                                                    session_player_id=player_id,
                                                    group_number=session_player_source["group_number"],
                                                    type=event['type'],
                                                    period_number=self.world_state_local["current_period"],                                                   
                                                    data=result))

        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False, 
                                send_to_group=True, target_list=target_list)
            
    async def update_cents(self, event):
        '''
        send survey complete update
        '''
        event_data = json.loads(event["group_data"])

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def instructions_range(self, event):
        '''
        process range update from client during instructions phase
        '''
        if self.controlling_channel != self.channel_name:
            return    
       
        logger = logging.getLogger(__name__) 

        status = "success"
        error_message = ""
        player_id = None
        text = ""

        try:
            player_id = self.session_players_local[event["player_key"]]["id"]
            session = await Session.objects.aget(id=self.session_id)
            event_data = event["message_text"]           
            instruction_world_state = event_data["world_state"] 
        except:
            logger.warning(f"instructions_update_treatment: invalid data, {event['message_text']}")
            error_message = "Invalid data."
            status = "fail"

        if status == "success":

            result = {"status": status, "error_message": error_message}
            result["world_state"] = session.update_revenues(instruction_world_state, self.parameter_set_local)

            target_list = [player_id]

            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, 
                                    send_to_group=True, target_list=target_list)


    async def update_instructions_range(self, event):
        '''
        update treatment on client during the instructions phase
        '''
        pass
