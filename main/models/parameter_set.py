'''
parameter set
'''
import logging
import json

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist

from main.models import InstructionSet

import main

class ParameterSet(models.Model):
    '''
    parameter set
    '''       
    period_length = models.IntegerField(verbose_name='Period Length, Production', default=60)                 #period length in seconds

    show_instructions = models.BooleanField(default=True, verbose_name='Show Instructions')                   #if true show instructions

    survey_required = models.BooleanField(default=False, verbose_name="Survey Required")                      #if true show the survey below
    survey_link = models.CharField(max_length = 1000, default = '', verbose_name = 'Survey Link', blank=True, null=True)

    prolific_mode = models.BooleanField(default=False, verbose_name="Prolific Mode")                          #put study into prolific mode
    prolific_completion_link = models.CharField(max_length = 1000, default = '', verbose_name = 'Forward to Prolific after sesison', blank=True, null=True) #at the completion of the study forward subjects to link

    world_width = models.IntegerField(verbose_name='Width of world in pixels', default=10000)                 #world width in pixels
    world_height = models.IntegerField(verbose_name='Height of world in pixels', default=10000)               #world height in pixels

    reconnection_limit = models.IntegerField(verbose_name='Limit Subject Screen Reconnection Trys', default=25)       #limit subject screen reconnection trys

    test_mode = models.BooleanField(default=False, verbose_name='Test Mode')                                #if true subject screens will do random auto testing

    json_for_session = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)                   #json model of parameter set 

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session.title

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.period_length = new_ps.get("period_length")

            self.show_instructions = True if new_ps.get("show_instructions") else False

            self.survey_required = True if new_ps.get("survey_required") else False
            self.survey_link = new_ps.get("survey_link")

            self.prolific_mode = True if new_ps.get("prolific_mode", False) else False
            self.prolific_completion_link = new_ps.get("prolific_completion_link", None)

            self.world_width = new_ps.get("world_width", 1000)
            self.world_height = new_ps.get("world_height", 1000)

            self.reconnection_limit = new_ps.get("reconnection_limit", None)

            self.save()

            #parameter set treatments
            self.parameter_set_treatments.all().delete()
            new_parameter_set_treatments = new_ps.get("parameter_set_treatments")
            new_parameter_set_treatments_map = {}

            for i in new_parameter_set_treatments:
                p = main.models.ParameterSetTreatment.objects.create(parameter_set=self)
                p.from_dict(new_parameter_set_treatments[i])

                new_parameter_set_treatments_map[i] = p.id

            #parameter set periodblocks
            self.parameter_set_periodblocks_a.all().delete()
            new_parameter_set_periodblocks = new_ps.get("parameter_set_periodblocks")
            new_parameter_set_periodblocks_map = {}

            for i in new_parameter_set_periodblocks:
                p = main.models.ParameterSetPeriodblock.objects.create(parameter_set=self)
                v = new_parameter_set_periodblocks[i]
                p.from_dict(v)

                new_parameter_set_periodblocks_map[i] = p.id

                if v.get("parameter_set_treatment", None) != None:
                    p.parameter_set_treatment_id=new_parameter_set_treatments_map[str(v["parameter_set_treatment"])]

                p.save()

            #parameter set players
            self.parameter_set_players.all().delete()

            new_parameter_set_players = new_ps.get("parameter_set_players")

            for i in new_parameter_set_players:
                p = main.models.ParameterSetPlayer.objects.create(parameter_set=self)
                v = new_parameter_set_players[i]
                p.from_dict(new_parameter_set_players[i], new_parameter_set_periodblocks_map)

                if v.get("instruction_set", None) != None:
                    p.instruction_set = InstructionSet.objects.filter(label=v.get("instruction_set_label",None)).first()
                
                p.save()

            self.update_player_count()

            self.json_for_session = None
            self.save()
            
        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        self.json_for_session = None

        self.save()

        for i in self.parameter_set_players.all():
            i.setup()

    # def add_player(self):
    #     '''
    #     add a parameterset player
    #     '''

    #     player = main.models.ParameterSetPlayer()
    #     player.parameter_set = self
    #     player.player_number = self.parameter_set_players.count() + 1
    #     player.id_label = player.player_number
    #     player.save()

    #     self.update_json_fk(update_players=True)
    
    def remove_player(self, parameterset_player_id):
        '''
        remove specified parameterset player
        '''
        
        try:
            player = self.parameter_set_players.get(id=parameterset_player_id)
            player.delete()

        except ObjectDoesNotExist:
            logger = logging.getLogger(__name__) 
            logger.warning(f"parameter set remove_player, not found ID: {parameterset_player_id}")

        self.update_player_count()
        self.update_json_fk(update_players=True)
    
    def update_player_count(self):
        '''
        update the number of parameterset players
        '''
        for count, i in enumerate(self.parameter_set_players.all()):
            i.player_number = count + 1
            i.update_json_local()
            i.save()
    
    def update_json_local(self):
        '''
        update json model
        '''
        self.json_for_session["id"] = self.id
                
        self.json_for_session["period_length"] = self.period_length

        self.json_for_session["show_instructions"] = 1 if self.show_instructions else 0

        self.json_for_session["survey_required"] = 1 if self.survey_required else 0
        self.json_for_session["survey_link"] = self.survey_link

        self.json_for_session["prolific_mode"] = 1 if self.prolific_mode else 0
        self.json_for_session["prolific_completion_link"] = self.prolific_completion_link
        
        self.json_for_session["world_width"] = self.world_width
        self.json_for_session["world_height"] = self.world_height

        self.json_for_session["reconnection_limit"] = self.reconnection_limit

        self.json_for_session["test_mode"] = 1 if self.test_mode else 0

        self.save()
    
    def update_json_fk(self, update_players=False, 
                             update_treatments=False,
                             update_periodblocks=False):
        '''
        update json model
        '''
        if update_players:
            self.json_for_session["parameter_set_players_order"] = list(self.parameter_set_players.all().values_list('id', flat=True))
            self.json_for_session["parameter_set_players"] = {p.id : p.json() for p in self.parameter_set_players.all()}

        if update_treatments:
            self.json_for_session["parameter_set_treatments_order"] = list(self.parameter_set_treatments.all().values_list('id', flat=True))
            self.json_for_session["parameter_set_treatments"] = {str(p.id) : p.json() for p in self.parameter_set_treatments.all()}

        if update_periodblocks:
            self.json_for_session["parameter_set_periodblocks_order"] = list(self.parameter_set_periodblocks_a.all().values_list('id', flat=True))
            self.json_for_session["parameter_set_periodblocks"] = {str(p.id) : p.json() for p in self.parameter_set_periodblocks_a.all()}
        self.save()

    def json(self, update_required=False):
        '''
        return json object of model, return cached version if unchanged
        '''
        if not self.json_for_session or \
           update_required:
            self.json_for_session = {}
            self.update_json_local()
            self.update_json_fk(update_players=True, 
                                update_treatments=True,
                                update_periodblocks=True)

        return self.json_for_session
    
    def get_json_for_subject(self):
        '''
        return json object for subject, return cached version if unchanged
        '''
        
        if not self.json_for_session:
            return None

        v = self.json_for_session
        
        return v
        

