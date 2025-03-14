
import logging
import sys

from decimal import Decimal
from asgiref.sync import sync_to_async
from django.core.exceptions import  ObjectDoesNotExist

from main.models import SessionPlayer

class GetSessionMixin():
    '''
    Get session mixin for subject home consumer
    '''
    async def get_session(self, event):
            '''
            return a list of sessions
            '''
            logger = logging.getLogger(__name__) 
            # logger.info(f"Get Session {event}, thread sensitive {self.thread_sensitive}")

            self.connection_uuid = event["message_text"]["player_key"]
            self.connection_type = "subject"

            #get session id for subject
            try:
                session_player = await SessionPlayer.objects.select_related('session').aget(player_key=self.connection_uuid)
                instruction_set = await sync_to_async(session_player.get_instruction_set)()
                self.session_id = session_player.session.id
                self.session_player_id = session_player.id
                self.controlling_channel =  session_player.session.controlling_channel
            except ObjectDoesNotExist:
                result = {"session" : None, "session_player" : None}
            else:        
                result = await sync_to_async(take_get_session_subject, thread_sensitive=self.thread_sensitive)(self.session_player_id)   

            world_state = result["session"]["world_state"]

            if session_player.session.started:
                group_number = world_state['session_players'][str(self.session_player_id)]['group_number']

                #move local player to front of group list
                world_state['groups'][str(group_number)].remove(self.session_player_id)
                world_state['groups'][str(group_number)].insert(0, self.session_player_id)

                if world_state['current_experiment_phase'] == 'Instructions':
                    
                    #show example range to subject
                    for index, i in enumerate(world_state['groups'][str(group_number)]):
                        session_player_ws = world_state['session_players'][str(i)]
                        session_player_ws['range_start'] = instruction_set[f'p{index + 1}_example_start_range']
                        session_player_ws['range_end'] = instruction_set[f'p{index + 1}_example_end_range']
                        session_player_ws['range_middle'] = (Decimal( session_player_ws['range_start']) + Decimal(session_player_ws['range_end']) + 1) / 2
                    
                    #recalcuate the world state
                    world_state = await sync_to_async(session_player.session.update_revenues)(world_state, result["session"]["parameter_set"])

            await self.send_message(message_to_self=result, message_to_subjects=None, message_to_staff=None, 
                                    message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        
        result = await sync_to_async(take_get_session_subject, thread_sensitive=self.thread_sensitive)(self.session_player_id)
        
        world_state = result["session"]["world_state"]
        
        group_number = world_state['session_players'][str(self.session_player_id)]['group_number']

        #move local player to front of group list
        world_state['groups'][str(group_number)].remove(self.session_player_id)
        world_state['groups'][str(group_number)].insert(0, self.session_player_id)

        await self.send_message(message_to_self=result, message_to_subjects=None, message_to_staff=None, 
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_reset_experiment(self, event):
        '''
        reset experiment on subjects
        '''

        #get session json object
        result = await sync_to_async(take_get_session_subject, thread_sensitive=self.thread_sensitive)(self.session_player_id)

        await self.send_message(message_to_self=result, message_to_subjects=None, message_to_staff=None, 
                                message_type=event['type'], send_to_client=True, send_to_group=False)
        
    async def update_refresh_screens(self, event):
        '''
        refresh staff screen
        '''
        result = await sync_to_async(take_get_session_subject, thread_sensitive=self.thread_sensitive)(self.session_player_id)

        await self.send_message(message_to_self=result, message_to_subjects=None, message_to_staff=None, 
                                message_type=event['type'], send_to_client=True, send_to_group=False)

def take_get_session_subject(session_player_id):
    '''
    get session info for subject
    '''

    logger = logging.getLogger(__name__) 
    # logger.info(f'take_get_session_subject: id {session_player_id}')

    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)

        return {"session" : session_player.session.json_for_subject(session_player), 
                "session_player" : session_player.json(),
                "value" : "success"}

    except ObjectDoesNotExist:
        return {"session" : None, 
                "session_player" : None,
                "value" : "fail"}