print("Update chat period")

from main.consumers.staff.session_parameters_consumer_mixins.parameter_set_treatments import take_update_parameter_set_treatment

from main.models import ParameterSetTreatment
from main.models import Session
from main.models import ParameterSet

from asgiref.sync import async_to_sync, sync_to_async



#get session ids from comand in csv format
session_id_csv = input("Enter session ids in csv format: ")
session_ids = session_id_csv.split(",")

#get range width from the command line
range_width = input("Enter range width: ")
range_height = input("Enter range height: ")
cost = input("Enter cost line y: ")

parameter_sets = Session.objects.filter(id__in=session_ids).values_list('parameter_set', flat=True).distinct()

#refesh all parameter sets json
for pst in ParameterSetTreatment.objects.filter(parameter_set__in=parameter_sets):
    
    json_payload = {"id":pst.id,
                "enable_chat":1 if pst.enable_chat else 0,
                "range_width":range_width,
                "scale_width":range_width,
                "cost_percent":cost,
                "id_label_pst":pst.id_label_pst,
                "range_height":range_height,
                "scale_height":range_height,
                "scale_height_ticks":pst.scale_height_ticks,
                "values_count":pst.values_count,
                "enable_contest":1 if pst.enable_contest else 0,
                "preserve_order":1 if pst.preserve_order else 0,
                "enable_ready_button":1 if pst.enable_ready_button else 0,
                "enable_transfer_cents":1 if pst.enable_transfer_cents else 0}
    
    async_to_sync(take_update_parameter_set_treatment)({"session_id": pst.parameter_set.session.id,
                                                        "parameterset_treatment_id": pst.id,
                                                        "form_data": json_payload})
