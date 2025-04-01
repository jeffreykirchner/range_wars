'''
build test
'''

import logging
import sys
import pytest
import json

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync

from django.test import TestCase


from main.models import Session

from main.routing import websocket_urlpatterns

class TestSubjectPeriodblock(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None
    session = None
    parameter_set_json = None
    session_player_1 = None
    
    def setUp(self):
        sys._called_from_test = True
        logger = logging.getLogger(__name__)

        logger.info('setup tests')

        self.session = Session.objects.get(title="T1")
        self.parameter_set_json = self.session.parameter_set.json()

    def tearDown(self):
        async_to_sync(self.close_communicators)

    async def set_up_communicators(self, communicator_subject, communicator_staff):
        '''
        setup the socket communicators
        '''
        logger = logging.getLogger(__name__)

        session_player = await self.session.session_players.afirst()

        connection_path_staff = f"/ws/staff-session/{self.session.channel_key}/session-{self.session.id}/{self.session.channel_key}"

        application = URLRouter(websocket_urlpatterns)
        
        #subjects
        async for i in self.session.session_players.all():
            connection_path_subject = f"/ws/subject-home/{self.session.channel_key}/session-{self.session.id}/{i.player_key}"
            communicator_subject.append(WebsocketCommunicator(application, connection_path_subject))

            connected_subject, subprotocol_subject = await communicator_subject[-1].connect()
            assert connected_subject

            communicator_subject[-1].scope["session_player_id"] = i.id

            message = {'message_type': 'get_session',
                       'message_text': {"player_key" :str(i.player_key)}}

            await communicator_subject[-1].send_json_to(message)
            response = await communicator_subject[-1].receive_json_from()
            # logger.info(response)
            
            self.assertEqual(response['message']['message_type'],'get_session')
            self.assertEqual(response['message']['message_data']['session_player']['id'], i.id)

        #staff
        communicator_staff = WebsocketCommunicator(application, connection_path_staff)
        connected_staff, subprotocol_staff = await communicator_staff.connect()
        assert connected_staff

        # #get staff session
        message = {'message_type': 'get_session',
                   'message_text': {"session_key" :str(self.session.session_key)}}

        await communicator_staff.send_json_to(message)
        response = await communicator_staff.receive_json_from()
        #logger.info(response)
        
        self.assertEqual(response['message']['message_type'],'get_session')

        return communicator_subject, communicator_staff
    
    async def start_session(self, communicator_subject, communicator_staff):
        '''
        start session and advance past instructions
        '''
        logger = logging.getLogger(__name__)

        #reset session
        # message = {'message_type' : 'reset_experiment',
        #            'message_text' : {},
        #            'message_target' : 'self', }
        # await communicator_staff.send_json_to(message)

        # for i in communicator_subject:
        #     response = await i.receive_json_from()
        #     self.assertEqual(response['message']['message_type'],'update_reset_experiment')
        #     message_data = response['message']['message_data']
        #     self.assertEqual(message_data['value'],'success')
        
        # response = await communicator_staff.receive_json_from()
        
        # #start session
        message = {'message_type' : 'start_experiment',
                   'message_text' : {},
                   'message_target' : 'self', }

        await communicator_staff.send_json_to(message)

        response = await communicator_staff.receive_json_from(timeout=10)

        for i in communicator_subject:
            response = await i.receive_json_from(timeout=10)
            self.assertEqual(response['message']['message_type'],'update_start_experiment')
            message_data = response['message']['message_data']
            self.assertEqual(message_data['value'],'success')
        
        # #advance past instructions
        message = {'message_type' : 'next_phase',
                   'message_text' : {},
                   'message_target' : 'self',}

        await communicator_staff.send_json_to(message)
       
        for i in communicator_subject:
            response = await i.receive_json_from()
            self.assertEqual(response['message']['message_type'],'update_next_phase')
            message_data = response['message']['message_data']
            self.assertEqual(message_data['value'],'success')
           
        response = await communicator_staff.receive_json_from()

        return communicator_subject, communicator_staff
    
    async def close_communicators(self):
        '''
        close the socket communicators
        '''
        for i in self.communicator_subject:
            await i.disconnect()

        await self.communicator_staff.disconnect()

        # for i in self.communicator_subject:
        #     del i
        
        # del self.communicator_staff

    @pytest.mark.asyncio
    async def test_inheritance_copy_forward(self):
        '''
        test get session subject from consumer
        '''        
        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        #start timer
        message = {'message_type' : 'start_timer',
            'message_text' : {"action": "start"},
            'message_target' : 'self', 
            }
        
        await communicator_staff.send_json_to(message)
        response = await communicator_staff.receive_json_from()

        #set period block to play
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        world_state["period_blocks"][str(world_state["current_period_block"])]["phase"] = "play"

        await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        #force to next period block, storing summary data
        for i in range(11):
            message = {'message_type' : 'force_advance_to_period',
                        'message_text' : {'period_number':i+1,},
                        'message_target' : 'self', 
                       }
            
            await communicator_staff.send_json_to(message)
            response = await communicator_staff.receive_json_from()
        
        session_period = await self.session.session_periods.aget(period_number=1)
        self.assertNotEqual(session_period.summary_data.get("session_players", None), None)
        
        #range copied forward
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["current_period"], 11)

        session_player = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 10)
        self.assertEqual(session_player["range_end"], 10)
        
        session_player = world_state["session_players"][str(communicator_subject[1].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 20)
        self.assertEqual(session_player["range_end"], 20)

        session_player = world_state["session_players"][str(communicator_subject[2].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 30)
        self.assertEqual(session_player["range_end"], 30)

        session_player = world_state["session_players"][str(communicator_subject[3].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 40)
        self.assertEqual(session_player["range_end"], 40)

    
    @pytest.mark.asyncio
    async def test_inheritance_mid_point_average(self):
        '''
        test get mid point average calcuation
        '''        
        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        #start timer
        message = {'message_type' : 'start_timer',
            'message_text' : {"action": "start"},
            'message_target' : 'self', 
            }
        
        await communicator_staff.send_json_to(message)
        response = await communicator_staff.receive_json_from()

        #set period block to play
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        world_state["period_blocks"][str(world_state["current_period_block"])]["phase"] = "play"

        await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        #force to next period block, storing summary data
        for i in range(11):
            message = {'message_type' : 'force_advance_to_period',
                        'message_text' : {'period_number':i+1,},
                        'message_target' : 'self', 
                       }
            
            await communicator_staff.send_json_to(message)
            response = await communicator_staff.receive_json_from()
        
        session_period = await self.session.session_periods.aget(period_number=1)
        self.assertNotEqual(session_period.summary_data.get("session_players", None), None)
        
        #range copied forward
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["current_period"], 11)

        #update positions for period block 2
        for i in range(11, 21):

            await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
            response = await communicator_staff.receive_json_from()
            world_state = response['message']['message_data']

            session_player = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
            session_player["range_start"] = 10
            session_player["range_end"] = i+10

            await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
            response = await communicator_staff.receive_json_from()

            message = {'message_type' : 'force_advance_to_period',
                        'message_text' : {'period_number':i+1,},
                        'message_target' : 'self', 
                       }
            
            await communicator_staff.send_json_to(message)
            response = await communicator_staff.receive_json_from()
        
        #mid point calculation
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["current_period"], 21)

        session_player = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 17)
        self.assertEqual(session_player["range_end"], 17)
        self.assertEqual(session_player["position"], 1)

    @pytest.mark.asyncio
    async def test_inheritance_mid_point_position(self):
        '''
        test midpoint position calculation for session players
        '''        
        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        #start timer
        message = {'message_type' : 'start_timer',
            'message_text' : {"action": "start"},
            'message_target' : 'self', 
            }
        
        await communicator_staff.send_json_to(message)
        response = await communicator_staff.receive_json_from()

        #set period block to play
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        world_state["period_blocks"][str(world_state["current_period_block"])]["phase"] = "play"

        await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        #force to next period block, storing summary data
        for i in range(11):
            message = {'message_type' : 'force_advance_to_period',
                        'message_text' : {'period_number':i+1,},
                        'message_target' : 'self', 
                       }
            
            await communicator_staff.send_json_to(message)
            response = await communicator_staff.receive_json_from()
        
        session_period = await self.session.session_periods.aget(period_number=1)
        self.assertNotEqual(session_period.summary_data.get("session_players", None), None)
        
        #range copied forward
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["current_period"], 11)

        #update positions for period block 2
        for i in range(11, 21):

            await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
            response = await communicator_staff.receive_json_from()
            world_state = response['message']['message_data']

            session_player = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
            session_player["range_start"] = 40
            session_player["range_end"] = 40

            session_player = world_state["session_players"][str(communicator_subject[1].scope["session_player_id"])]
            session_player["range_start"] = 30
            session_player["range_end"] = 30

            session_player = world_state["session_players"][str(communicator_subject[2].scope["session_player_id"])]
            session_player["range_start"] = 20
            session_player["range_end"] = 20

            session_player = world_state["session_players"][str(communicator_subject[3].scope["session_player_id"])]
            session_player["range_start"] = 10
            session_player["range_end"] = 10

            await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
            response = await communicator_staff.receive_json_from()

            message = {'message_type' : 'force_advance_to_period',
                        'message_text' : {'period_number':i+1,},
                        'message_target' : 'self', 
                       }
            
            await communicator_staff.send_json_to(message)
            response = await communicator_staff.receive_json_from()
        
        #midpoint calculation
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["current_period"], 21)

        session_player = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 40)
        self.assertEqual(session_player["range_end"], 40)
        self.assertEqual(session_player["position"], 4)

        session_player = world_state["session_players"][str(communicator_subject[1].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 30)
        self.assertEqual(session_player["range_end"], 30)
        self.assertEqual(session_player["position"], 3)

        session_player = world_state["session_players"][str(communicator_subject[2].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 20)
        self.assertEqual(session_player["range_end"], 20)
        self.assertEqual(session_player["position"], 2)

        session_player = world_state["session_players"][str(communicator_subject[3].scope["session_player_id"])]
        self.assertEqual(session_player["range_start"], 10)
        self.assertEqual(session_player["range_end"], 10)
        self.assertEqual(session_player["position"], 1)





