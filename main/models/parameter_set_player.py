'''
parameterset player 
'''

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import ParameterSet
from main.models import InstructionSet

import main

class ParameterSetPlayer(models.Model):
    '''
    session player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_players")
    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.SET_NULL, related_name="parameter_set_players_c", blank=True, null=True)

    id_label = models.CharField(verbose_name='ID Label', max_length=20, default="1")      #id label shown on screen to subjects
    player_number = models.IntegerField(verbose_name='Player number', default=0)          #player number, from 1 to N 

    hex_color = models.CharField(verbose_name='Hex Color', max_length = 30, default="0x000000") #color of player

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id_label)
    
    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering=['player_number']

    def from_dict(self, new_ps, new_parameter_set_periodblocks_map):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.id_label = new_ps.get("id_label")
        self.player_number = new_ps.get("player_number")
        self.hex_color = new_ps.get("hex_color")

        self.save()

        #add player groups
        if new_parameter_set_periodblocks_map:

            new_parameter_set_player_groups = new_ps.get("parameter_set_player_groups")

            for pg in new_parameter_set_player_groups:
                parameter_set_player_group = main.models.ParameterSetPlayerGroup()
                new_parameter_set_player_group = new_parameter_set_player_groups[pg]

                parameter_set_player_group.parameter_set_player = self
                parameter_set_player_group.parameter_set_period_block_id = int(new_parameter_set_periodblocks_map[str(pg)])
                parameter_set_player_group.group_number = new_parameter_set_player_group["group_number"]
                parameter_set_player_group.position = new_parameter_set_player_group["position"]
                parameter_set_player_group.start_box = new_parameter_set_player_group["start_box"]

                parameter_set_player_group.save()

        
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
        self.parameter_set.json_for_session["parameter_set_players"][self.id] = self.json()

        self.parameter_set.save()

        self.save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,

            "instruction_set" : self.instruction_set.id if self.instruction_set else None,
            "instruction_set_label" : self.instruction_set.label if self.instruction_set else "---",

            "player_number" : self.player_number,
            "id_label" : self.id_label,
            "hex_color" : self.hex_color,

            "parameter_set_player_groups" : {str(p.parameter_set_period_block.id) : p.json() for p in self.parameter_set_player_groups_a.all()}
        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_players"][str(self.id)]

        # edit v as needed

        return v


