'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class ExperimentPhase(models.TextChoices):
    '''
    experiment phases
    '''
    INSTRUCTIONS = 'Instructions', _('Instructions')
    RUN = 'Run', _('Run')
    NAMES = 'Names', _('Names')
    DONE = 'Done', _('Done')

class PeriodblockInheritance(models.TextChoices):
    '''
    periodlbock inheritance
    '''
    PRESET = 'Preset', _('Preset')
    COPY =  'Copy', _('Copy')
    MIDPOINT = 'Midpoint', _('Midpoint')

class SummaryType(models.TextChoices):
    '''
    summary types
    '''
    PARTIAL = 'Partial', _('Partial')
    FULL = 'Full', _('Full')