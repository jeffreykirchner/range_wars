'''
parameterset player group 
'''

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import ParameterSetPlayer
from main.models import ParameterSetPeriodblock

import main

class ParameterSetPlayerGroup(models.Model):
    '''
    session player group parameters 
    '''

    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="parameter_set_player_groups_a")
    parameter_set_period_block = models.ForeignKey(ParameterSetPeriodblock, on_delete=models.CASCADE, related_name="parameter_set_player_groups_b")

    group_number = models.IntegerField(verbose_name='Group Number', default=1)         #group during period block
    position = models.IntegerField(verbose_name='Position', default=1)                 #position on graph during period block
    start_box = models.IntegerField(verbose_name='Start Box', default=0)               #start box at beginning of period block

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.parameter_set_period_block)
    
    class Meta:
        verbose_name = 'Parameter Set Player Group'
        verbose_name_plural = 'Parameter Set Player Groups'
        ordering=['parameter_set_period_block__period_start']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset group
        '''

        self.group_number = new_ps.get("group_number")
        self.position = new_ps.get("position")
        self.start_box = new_ps.get("start_box")
       
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
        self.parameter_set.json_for_session["parameter_set_players"][self.parameter_set_player.id] = self.parameter_set_player.json()

        self.parameter_set.save()

        self.save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,

            "parameter_set_period_block" : self.parameter_set_period_block.id,

            "group_number" : self.group_number,
            "position" : self.position,
            "start_box" : self.start_box,

        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        # v = self.parameter_set.json_for_session["parameter_set_players"][str(self.id)]

        # edit v as needed

        return None


