import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayerGroup

from main.forms import ParameterSetPlayerGroupForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

class ParameterSetPlayerGroupsMixin():
    '''
    parameter set plaeyer mixin
    '''

    async def update_parameter_set_player_group(self, event):
        '''
        update a parameterset player_group
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_player_group(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_player_group(data):
    '''
    update parameterset player_group
    '''   
    logger = logging.getLogger(__name__) 
    # logger.info(f"Update parameterset player_group: {data}")

    session_id = data["session_id"]
    parameterset_player_group_id = data["parameterset_player_group_id"]
    form_data = data["form_data"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_player_group = ParameterSetPlayerGroup.objects.get(id=parameterset_player_group_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_player_group parameterset_player_group, not found ID: {parameterset_player_group_id}")
        return
    
    form_data_dict = form_data

    # logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerGroupForm(form_data_dict, instance=parameter_set_player_group)

    if form.is_valid():         
        form.save()              
        session.parameter_set.update_json_fk(update_players=True)

        return {"value" : "success"}                      
                                
    logger.warning("Invalid parameterset player_group form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}
    
