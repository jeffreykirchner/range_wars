'''
parameterset periodblock 
'''

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import ParameterSet
from main.models import ParameterSetTreatment
from main.models import HelpDocsSubject

from main.globals import PeriodblockInheritance

import main

class ParameterSetPeriodblock(models.Model):
    '''
    session periodblock parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_periodblocks_a")
    parameter_set_treatment = models.ForeignKey(ParameterSetTreatment, on_delete=models.SET_NULL, related_name="parameter_set_periodblocks_b", blank=True, null=True)
    help_doc = models.ForeignKey(HelpDocsSubject, on_delete=models.CASCADE, related_name="parameter_set_notices", blank=True, null=True)

    period_start = models.IntegerField(verbose_name='Period Start', default=1)         #starting period
    period_end = models.IntegerField(verbose_name='Period End', default=1)             #ending period

    inheritance = models.CharField(verbose_name='Inheritance', max_length=30, choices=PeriodblockInheritance.choices, default=PeriodblockInheritance.PRESET)

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

        self.period_start = new_ps.get("period_start")
        self.period_end = new_ps.get("period_end")

        self.inheritance = new_ps.get("inheritance", PeriodblockInheritance.PRESET)

        help_doc_id = new_ps.get("help_doc", None)

        if help_doc_id:
            help_doc = main.models.HelpDocsSubject.objects.filter(id=help_doc_id).first()

            if help_doc:
               self.help_doc = help_doc
            else:
                #look up by title
                parameter_set_player_first = self.parameter_set.parameter_set_players.first()
                if parameter_set_player_first:
                     self.help_doc = parameter_set_player_first.instruction_set.help_docs_subject.filter(title=new_ps.get("help_doc_title")).first()
        else:
            self.help_doc = None
       
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

            "help_doc" : self.help_doc.id if self.help_doc else None,
            "help_doc_title" : self.help_doc.title if self.help_doc else None,

            "period_start" : self.period_start,
            "period_end" : self.period_end,

            "inheritance" : self.inheritance,

        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_periodblocks"][str(self.id)]

        # edit v as needed

        return v


