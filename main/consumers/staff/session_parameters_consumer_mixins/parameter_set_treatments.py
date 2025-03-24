import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetTreatment

from main.forms import ParameterSetTreatmentForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

class ParameterSetTreatmentsMixin():
    '''
    parameter set treatment mixin
    '''

    async def update_parameter_set_treatment(self, event):
        '''
        update a parameterset treatment
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_treatment(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_treatment(self, event):
        '''
        remove a parameterset treatment
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_treatment(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_treatment(self, event):
        '''
        add a parameterset treatment
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_treatment(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
        
    async def duplicate_parameterset_treatment(self, event):
        '''
        duplicate a parameterset treatment
        '''
        message_data = {}
        message_data["status"] = await take_duplicate_parameterset_treatment(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])
        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_treatment(data):
    '''
    update parameterset treatment
    '''   
    logger = logging.getLogger(__name__) 
    # logger.info(f"Update parameterset treatment: {data}")

    session_id = data["session_id"]
    parameterset_treatment_id = data["parameterset_treatment_id"]
    form_data = data["form_data"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_treatment = ParameterSetTreatment.objects.get(id=parameterset_treatment_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_treatment, not found ID: {parameterset_treatment_id}")
        return
    
    form_data_dict = form_data

    # logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetTreatmentForm(form_data_dict, instance=parameter_set_treatment)
    
    if form.is_valid():         
        form.save()              
        parameter_set_treatment.parameter_set.update_json_fk(update_treatments=True)

        return {"value" : "success"}                      
                                
    logger.warning("Invalid parameterset treatment form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_treatment(data):
    '''
    remove the specifed parmeterset treatment
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Remove parameterset treatment: {data}")

    session_id = data["session_id"]
    parameterset_treatment_id = data["parameterset_treatment_id"]

    try:        
        session = Session.objects.get(id=session_id)
        parameter_set_treatment = ParameterSetTreatment.objects.get(id=parameterset_treatment_id)
        
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_treatment, not found ID: {parameterset_treatment_id}")
        return
    
    parameter_set_treatment.delete()
    session.parameter_set.update_json_fk(update_treatments=True)
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_treatment(data):
    '''
    add a new parameter treatment to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    # logger.info(f"Add parameterset treatment: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_parameterset_treatment session, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_treatment_last = ParameterSetTreatment.objects.filter(parameter_set=session.parameter_set).last()

    parameter_set_treatment = ParameterSetTreatment.objects.create(parameter_set=session.parameter_set)

    if parameter_set_treatment_last:
        parameter_set_treatment.from_dict(parameter_set_treatment_last.json())

    parameter_set_treatment.id_label_pst = "~"
    parameter_set_treatment.save()

    session.parameter_set.update_json_fk(update_treatments=True)

    return {"value" : "success"}
    
@sync_to_async
def take_duplicate_parameterset_treatment(data):
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
        logger.warning(f"take_duplicate_parameterset_treatment player, not found ID: {session_id}")
        return {"value" : "fail"}
    
    parameter_set_treatment_source = ParameterSetTreatment.objects.get(id=data["parameterset_treatment_id"])

    parameter_set_treatment = ParameterSetTreatment()
    parameter_set_treatment.parameter_set = parameter_set
    
    parameter_set_treatment.from_dict(parameter_set_treatment_source.json())
    parameter_set_treatment.id_label_pst = parameter_set_treatment.id_label_pst + " (copy)"
    parameter_set_treatment.save()
        
    parameter_set.update_json_fk(update_treatments=True)

    return {"value" : "success"}