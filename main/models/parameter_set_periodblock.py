'''
parameterset periodblock 
'''

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import ParameterSet
from main.models import ParameterSetTreatment

import main

class ParameterSetPeriodblock(models.Model):
    '''
    session periodblock parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_periodblocks_a")
    parameter_set_treatment = models.ForeignKey(ParameterSetTreatment, on_delete=models.SET_NULL, related_name="parameter_set_periodblocks_b", blank=True, null=True)

    period_start = models.IntegerField(verbose_name='Period Start', default=1)         #starting period
    period_end = models.IntegerField(verbose_name='Period End', default=1)             #ending period

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id_label)
    
    class Meta:
        verbose_name = 'Parameter Set Periodblock'
        verbose_name_plural = 'Parameter Set Periodblocks'
        ordering=['period_start']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset periodblock
        '''

        self.id_label = new_ps.get("id_label")
        self.periodblock_number = new_ps.get("periodblock_number")
       
        self.save()
        
        message = "Parameters loaded successfully."

        return message
    
    def setup(self):
        '''
        default setup
        '''           
            
        self.save()
    
    def update_json_local(self):
        '''
        update parameter set json
        '''
        self.parameter_set.json_for_session["parameter_set_periodblocks"][self.id] = self.json()

        self.parameter_set.save()

        self.save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,

            "parameter_set_treatment" : self.parameter_set_treatment.id if self.parameter_set_treatment else None,

            "period_start" : self.period_start,
            "period_end" : self.period_end,

        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_periodblocks"][str(self.id)]

        # edit v as needed

        return v


