import logging
import math
import json

from datetime import datetime
from decimal import Decimal

from asgiref.sync import sync_to_async

from main.models import Session
from main.models import SessionEvent

from main.globals import ExperimentPhase
from main.globals import round_up

class TimerMixin():
    '''
    timer mixin for staff session consumer
    '''

    async def start_timer(self, event):
        '''
        start or stop timer 
        '''
        logger = logging.getLogger(__name__)
        # logger.info(f"start_timer {event}")

        if self.controlling_channel != self.channel_name:
            logger.warning(f"start_timer: not controlling channel")
            return

        if event["message_text"]["action"] == "start":            
            self.world_state_local["timer_running"] = True

            self.world_state_local["timer_history"].append({"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                                                        "count": 0})
        else:
            self.world_state_local["timer_running"] = False

        
        await self.store_world_state(force_store=True)

        # if self.world_state_local["timer_running"]:
        #     result = {"timer_running" : True}
        #     await self.send_message(message_to_self=result, message_to_group=None,
        #                             message_type=event['type'], send_to_client=True, send_to_group=False)
        
        #     #start continue timer
        #     # await self.channel_layer.send(
        #     #     self.channel_name,
        #     #     {
        #     #         'type': "continue_timer",
        #     #         'message_text': {},
        #     #     }
        #     # )
        # else:
            #stop timer
        result = {"timer_running" : self.world_state_local["timer_running"]}
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
        
        # logger.info(f"start_timer complete {event}")

    async def continue_timer(self, event):
        '''
        continue to next second of the experiment
        '''

        if self.controlling_channel != self.channel_name:
            return
        
        logger = logging.getLogger(__name__)
        #logger.info(f"continue_timer: start")

        if not self.world_state_local["timer_running"]:
            # logger.info(f"continue_timer timer off")
            await self.send_message(message_to_self=True, message_to_group=None,
                                    message_type="stop_timer_pulse", send_to_client=True, send_to_group=False)
            return

        stop_timer = False
        send_update = True
        new_period_block = False

        result = {"earnings":{}}

        #check session over

        #if session is not over check if a full second has passed
        if self.world_state_local["current_experiment_phase"] != ExperimentPhase.NAMES:

            ts = datetime.now() - datetime.strptime(self.world_state_local["timer_history"][-1]["time"],"%Y-%m-%dT%H:%M:%S.%f")

            #check if a full second has passed
            if self.world_state_local["timer_history"][-1]["count"] == math.floor(ts.seconds):
                send_update = False

            if send_update:
                ts = datetime.now() - datetime.strptime(self.world_state_local["timer_history"][-1]["time"],"%Y-%m-%dT%H:%M:%S.%f")

                self.world_state_local["timer_history"][-1]["count"] = math.floor(ts.seconds)

                total_time = 0  #total time elapsed
                for i in self.world_state_local["timer_history"]:
                    total_time += i["count"]

                #check for end game
                if self.world_state_local["current_period"] == len(self.world_state_local["session_periods_order"]):
                    # do end game
                    return

                period_block = self.world_state_local["period_blocks"][str(self.world_state_local["current_period_block"])]

                if  period_block["phase"] == "start" or period_block["phase"] == "take_intial_ranges":
                    #check if all session players are ready
                    all_ready = True

                    for p in period_block["session_players"]:
                        session_player = period_block["session_players"][p]

                        if session_player["ready"] == False:
                            all_ready = False
                            break
                
                    if all_ready:
                        period_block["phase"] = "play"
                else:

                    self.world_state_local["time_remaining"] = 1
                    self.world_state_local["current_period"] += 1

                    last_session_period_id = self.world_state_local["session_periods_order"][self.world_state_local["current_period"]-2]
                    current_session_period_id = self.world_state_local["session_periods_order"][self.world_state_local["current_period"]-1]

                    last_session_period = self.world_state_local["session_periods"][str(last_session_period_id)]
                    current_session_period = self.world_state_local["session_periods"][str(current_session_period_id)]

                    self.world_state_local["current_period_block"] =  current_session_period["parameter_set_periodblock_id"]

                    if last_session_period["parameter_set_periodblock_id"] != current_session_period["parameter_set_periodblock_id"]:
                        #the period is over 
                        send_update = True

        if send_update:
            session = await Session.objects.aget(id=self.session_id)

            # self.world_state_local = await sync_to_async(session.update_treatment)(self.world_state_local, self.parameter_set_local)
            self.world_state_local = await sync_to_async(session.update_revenues)(self.world_state_local, self.parameter_set_local)

            #add period earnings to session players
            for player_id in self.world_state_local["session_players"]:
                player = self.world_state_local["session_players"][player_id]
                player["earnings"] = Decimal(player["earnings"]) + Decimal(player["total_profit"])

            #session status
            result["value"] = "success"
            result["stop_timer"] = stop_timer
            result["time_remaining"] = self.world_state_local["time_remaining"]
            result["current_period"] = self.world_state_local["current_period"]
            result["timer_running"] = self.world_state_local["timer_running"]
            result["started"] = self.world_state_local["started"]
            result["finished"] = self.world_state_local["finished"]
            result["current_experiment_phase"] = self.world_state_local["current_experiment_phase"]
            result["session_players"] = self.world_state_local["session_players"]
            result["period_blocks"] = self.world_state_local["period_blocks"]

            session_player_status = {}

            result["session_player_status"] = session_player_status

            self.session_events.append(SessionEvent(session_id=self.session_id, 
                                                    type="time",
                                                    period_number=self.world_state_local["current_period"],
                                                    time_remaining=self.world_state_local["time_remaining"],
                                                    data=result))
            
            await SessionEvent.objects.abulk_create(self.session_events, ignore_conflicts=True)

            self.session_events = []

            if stop_timer:
                self.world_state_local["timer_running"] = False

            await self.store_world_state(force_store=True)
            
            if period_block["phase"] == "take_intial_ranges":
                await self.send_message(message_to_self=result, message_to_group=None,
                                        message_type="time", send_to_client=True, send_to_group=False)

            else:
                if period_block["phase"] == "start":
                    period_block["phase"] = "take_intial_ranges"

                await self.send_message(message_to_self=False, message_to_group=result,
                                        message_type="time", send_to_client=False, send_to_group=True)

    async def update_time(self, event):
        '''
        update time phase
        '''

        event_data = json.loads(event["group_data"])

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
        
    #async helpers
    