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

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None
    session = None
    parameter_set_json = None
    session_player_1 = None
    
    def setUp(self):
        sys._called_from_test = True
        logger = logging.getLogger(__name__)

        logger.info('setup tests')

        self.session = Session.objects.get(title="2")
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
    async def test_chat_group(self):
        '''
        test get session subject from consumer
        '''        
        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        session = await Session.objects.aget(title="2")
        world_state = session.world_state

        #send chat
        message = {'message_type' : 'chat',
                   'message_text' : {'text': 'How do you do?',},
                   'message_target' : 'group', 
                  }
        
        session_player_target = world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]
        await communicator_subject[0].send_json_to(message)

        for i in communicator_subject:
            session_player = world_state["session_players"][str(i.scope["session_player_id"])]

            if session_player["group_number"] == session_player_target["group_number"]:
                response = await i.receive_json_from()
                message_data = response['message']['message_data']
                self.assertEqual(message_data['status'],'success')
                self.assertEqual(message_data['text'],'How do you do?')
            else:
                response = await i.receive_nothing()
                self.assertTrue(response)
        
        #staff response
        response = await communicator_staff.receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')
        self.assertEqual(message_data['text'],'How do you do?')
    
    @pytest.mark.asyncio
    async def test_ranges(self):
        '''
        test allowable ranges
        '''

        #advance to period block 2
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

        #force advance to period 6
        message = {'message_type' : 'force_advance_to_period',
                   'message_text' : {'period_number': 6,},
                   'message_target' : 'self', 
                  }
        
        await communicator_staff.send_json_to(message)
        response = await communicator_staff.receive_json_from()
        
        #submit inital ranges
        for i in communicator_subject:
            data = {"range_start": 0,       
                    "range_end": 0}
            
            message = {'message_type' : 'range',
                       'message_text' : data,
                       'message_target' : 'group', }

            await i.send_json_to(message)

            response = await i.receive_json_from()
            message_data = response['message']['message_data']
            self.assertEqual(message_data['status'],'success')

            response = await communicator_staff.receive_json_from()
        
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        session_players = world_state["session_players"]

        for i in session_players:

            self.assertEqual(session_players[i]["range_start"], 0)
            self.assertEqual(session_players[i]["range_end"], 0)

            self.assertEqual(session_players[i]["total_cost"], '0.02')
            self.assertEqual(session_players[i]["total_revenue"], '0.06')
            self.assertEqual(session_players[i]["total_profit"], '0.04')

        
        #expand player 2 ranges
        data = {"range_start": 0,       
                "range_end": 4}
            
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[1].send_json_to(message)

        response = await communicator_subject[1].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')

        response = await communicator_staff.receive_json_from()

        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        session_player = world_state["session_players"][str(communicator_subject[1].scope["session_player_id"])]

        self.assertEqual(session_player["range_start"], 0)
        self.assertEqual(session_player["range_end"], 4)

        self.assertEqual(session_player["total_cost"], '0.09')
        self.assertEqual(session_player["total_revenue"], '0.54')
        self.assertEqual(session_player["total_profit"], '0.45')

    @pytest.mark.asyncio
    async def test_transfer_cents(self):
        '''
        test transfering cents
        '''

        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_stff = await self.start_session(communicator_subject, communicator_staff)

        #transfer funds when not enough
        data = {"amount": 1,
                "recipient": communicator_subject[1].scope["session_player_id"]};
        
        await communicator_subject[0].send_json_to({"message_type": "cents", 
                                                    "message_text": data, 
                                                    "message_target": "group"})
        
        response = await communicator_subject[0].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'fail')
        self.assertEqual(message_data['error_message'], "Insufficient funds.")
        response = await communicator_staff.receive_json_from()

        #transfer funds when enough
        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]["earnings"] = "100"
        await communicator_staff.send_json_to({"message_type": "set_world_state_local", "message_text": {"world_state": world_state}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]["earnings"], "100")

        data = {"amount": 1,
                "recipient": communicator_subject[1].scope["session_player_id"]};
        
        await communicator_subject[0].send_json_to({"message_type": "cents", 
                                                    "message_text": data, 
                                                    "message_target": "group"})
        
        response = await communicator_subject[0].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')
        response = await communicator_staff.receive_json_from()

        await communicator_staff.send_json_to({"message_type": "get_world_state_local", "message_text": {}})
        response = await communicator_staff.receive_json_from()
        world_state = response['message']['message_data']

        self.assertEqual(world_state["session_players"][str(communicator_subject[0].scope["session_player_id"])]["earnings"], "99")
        self.assertEqual(world_state["session_players"][str(communicator_subject[1].scope["session_player_id"])]["earnings"], "1")




