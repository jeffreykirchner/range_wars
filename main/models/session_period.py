'''
session period model
'''

#import logging

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session

import main

class SessionPeriod(models.Model):
    '''
    session period model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_periods")
    parameter_set_periodblock = models.ForeignKey('ParameterSetPeriodBlock', on_delete=models.CASCADE, related_name="session_periods_b", null=True, blank=True) #period block for session period

    period_number = models.IntegerField()                        #period number from 1 to N across all period blocks
    round_number = models.IntegerField(null=True, blank=True)    #round number within period block

    summary_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True, verbose_name="Summary Data")       #summary data for session period

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'period_number'], name='unique_SD')
        ]
        verbose_name = 'Session Period'
        verbose_name_plural = 'Session Periods'
        ordering = ['period_number']
    
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,
            "period_number" : self.period_number,
            "round_number" : self.round_number,
            "parameter_set_periodblock_id" : self.parameter_set_periodblock.id if self.parameter_set_periodblock else None,
            "payments_made" : False,
        }
        