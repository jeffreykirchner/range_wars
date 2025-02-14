
import json
from main.decorators import check_message_for_me

class InterfaceMixin():
    '''
    interface actions from subject screen mixin
    '''

    @check_message_for_me
    async def update_range(self, event):
        '''
        result of subject updating their range
        '''

        event_data = json.loads(event["group_data"])

        await self.send_message(message_to_self=event_data, message_to_subjects=None, message_to_staff=None, 
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        