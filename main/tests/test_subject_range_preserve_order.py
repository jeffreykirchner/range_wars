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

class TestSubjectConsumer2(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None
    session = None
    parameter_set_json = None
    session_player_1 = None
    
    def setUp(self):
        sys._called_from_test = True
        logger = logging.getLogger(__name__)

        logger.info('setup tests')

        self.session = Session.objects.get(title="1")
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

    @pytest.mark.asyncio
    async def test_range_centers(self):
        '''
        test allowable past centers
        '''

        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        #move purple to left
        data = {"range_start": 11,       
                "range_end": 11}
            
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[1].send_json_to(message)

        response = await communicator_subject[1].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')

        response = await communicator_staff.receive_json_from()

        #move purple to left shared center with red
        data = {"range_start": 9,       
                "range_end": 11}
            
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[1].send_json_to(message)

        response = await communicator_subject[1].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')

        response = await communicator_staff.receive_json_from()

        #try to move purple center past red's center
        data = {"range_start": 8,       
                "range_end": 11}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[1].send_json_to(message)

        response = await communicator_subject[1].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'fail')

        response = await communicator_staff.receive_json_from()

        #try to move red past center of purple
        data = {"range_start": 10,       
                "range_end": 11}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[0].send_json_to(message)

        response = await communicator_subject[0].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'fail')

        response = await communicator_staff.receive_json_from()
    
    @pytest.mark.asyncio
    async def test_range_neighbors(self):
        '''
        test allowable range into non-neighbors
        '''

        communicator_subject = []
        communicator_staff = None

        logger = logging.getLogger(__name__)
        logger.info(f"called from test {sys._called_from_test}" )

        communicator_subject, communicator_staff = await self.set_up_communicators(communicator_subject, communicator_staff)
        communicator_subject, communicator_staff = await self.start_session(communicator_subject, communicator_staff)

        #move red to right
        data = {"range_start": 10,       
                "range_end": 19}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[0].send_json_to(message)

        response = await communicator_subject[0].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')

        response = await communicator_staff.receive_json_from()

        #move blue to left, next to red
        data = {"range_start": 20,       
                "range_end": 30}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[2].send_json_to(message)

        response = await communicator_subject[2].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'success')

        response = await communicator_staff.receive_json_from()

        #try to move blue into red
        data = {"range_start": 19,       
                "range_end": 30}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[2].send_json_to(message)

        response = await communicator_subject[2].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'fail')
        self.assertEqual(message_data['error_message'],"Your range cannot overlap with Red's.")

        response = await communicator_staff.receive_json_from()

        #try to move red into blue
        data = {"range_start": 10,       
                "range_end": 20}
                    
        message = {'message_type' : 'range',
                   'message_text' : data,
                   'message_target' : 'group', }

        await communicator_subject[0].send_json_to(message)

        response = await communicator_subject[0].receive_json_from()
        message_data = response['message']['message_data']
        self.assertEqual(message_data['status'],'fail')
        self.assertEqual(message_data['error_message'],"Your range cannot overlap with Blue's.")

        response = await communicator_staff.receive_json_from()

