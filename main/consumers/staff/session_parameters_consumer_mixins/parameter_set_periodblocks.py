import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPeriodblock

from main.forms import ParameterSetPeriodblockForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

import main

class ParameterSetPeriodblocksMixin():
    '''
    parameter set plaeyer mixin
    '''

    async def update_parameter_set_periodblock(self, event):
        '''
        update a parameterset periodblock
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_periodblock(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_periodblock(self, event):
        '''
        remove a parameterset periodblock
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_periodblock(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_periodblock(self, event):
        '''
        add a parameterset periodblock
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_periodblock(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
        
    async def duplicate_parameterset_periodblock(self, event):
        '''
        duplicate a parameterset periodblock
        '''

        message_data = {}
        message_data["status"] = await take_duplicate_parameterset_periodblock(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_periodblock(data):
    '''
    update parameterset periodblock
    '''   
    logger = logging.getLogger(__name__) 
    # logger.info(f"Update parameterset periodblock: {data}")

    session_id = data["session_id"]
    parameterset_periodblock_id = data["parameterset_periodblock_id"]
    form_data = data["form_data"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_periodblock = ParameterSetPeriodblock.objects.get(id=parameterset_periodblock_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_periodblock parameterset_periodblock, not found ID: {parameterset_periodblock_id}")
        return
    
    form_data_dict = form_data

    # logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPeriodblockForm(form_data_dict, instance=parameter_set_periodblock)
    form.fields["parameter_set_periodblock"].queryset = session.parameter_set.parameter_set_periodblocks.all()
    try:
        form.fields["help_doc"].queryset = session.parameter_set.parameter_set_players.first().instruction_set.help_docs_subject.all()
    except AttributeError:
        form.fields["help_doc"].queryset = None

    if form.is_valid():         
        form.save()              
        session.parameter_set.update_json_fk(update_periodblocks=True,
                                             update_players=True)

        return {"value" : "success"}                      
                                
    logger.warning("Invalid parameterset periodblock form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_periodblock(data):
    '''
    remove the specifed parmeterset periodblock
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Remove parameterset periodblock: {data}")

    session_id = data["session_id"]
    parameterset_periodblock_id = data["parameterset_periodblock_id"]

    try:        
        session = Session.objects.get(id=session_id)       

        parameter_set_periodblock = ParameterSetPeriodblock.objects.get(id=parameterset_periodblock_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_periodblock paramterset_periodblock, not found ID: {parameterset_periodblock_id}")
        return
    
    parameter_set_periodblock.delete()
    session.parameter_set.update_json_fk(update_periodblocks=True,
                                         update_players=True)
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_periodblock(data):
    '''
    add a new parameter periodblock to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset periodblock: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameter_set session, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_periodblock_last = ParameterSetPeriodblock.objects.filter(parameter_set=session.parameter_set).last()
    
    parameter_set_periodblock = ParameterSetPeriodblock.objects.create(parameter_set=session.parameter_set)

    if parameter_set_periodblock_last:
        parameter_set_periodblock.period_start = parameter_set_periodblock_last.period_end + 1
        parameter_set_periodblock.period_end = parameter_set_periodblock.period_start + 1
        parameter_set_periodblock.parameter_set_periodblock = parameter_set_periodblock_last.parameter_set_periodblock
    
    parameter_set_periodblock.save()
    
    for p in session.parameter_set.parameter_set_players.all():
        parameter_set_player_group_last = main.models.ParameterSetPlayerGroup.objects.filter(parameter_set_player=p).last()
        parameter_set_player_group = main.models.ParameterSetPlayerGroup.objects.create(parameter_set_player=p, 
                                                                                        parameter_set_period_block=parameter_set_periodblock)
       
        if parameter_set_player_group_last:
            parameter_set_player_group.from_dict(parameter_set_player_group_last.json())

    session.parameter_set.update_json_fk(update_periodblocks=True,
                                         update_players=True)

    return {"value" : "success"}

@sync_to_async
def take_duplicate_parameterset_periodblock(data):
    '''
    duplicate parameter treatment to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset player: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set = session.parameter_set
    except ObjectDoesNotExist:
        logger.warning(f"take_duplicate_parameterset_periodblock player, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_periodblock_source = ParameterSetPeriodblock.objects.get(id=data["parameterset_periodblock_id"])
    parameter_set_periodblock_last = ParameterSetPeriodblock.objects.filter(parameter_set=parameter_set).last()

    parameter_set_periodblock = ParameterSetPeriodblock()
    parameter_set_periodblock.parameter_set = parameter_set
    
    parameter_set_periodblock.from_dict(parameter_set_periodblock_source.json())    
    parameter_set_periodblock.parameter_set_treatment = parameter_set_periodblock_source.parameter_set_treatment

    #set start and end period
    if parameter_set_periodblock_last:
        parameter_set_periodblock.period_start = parameter_set_periodblock_last.period_end + 1
        parameter_set_periodblock.period_end = parameter_set_periodblock.period_start + parameter_set_periodblock_source.period_end - parameter_set_periodblock_source.period_start
       
   
    parameter_set_periodblock.save()
        
    parameter_set.update_json_fk(update_periodblocks=True)

    return {"value" : "success"}
    
