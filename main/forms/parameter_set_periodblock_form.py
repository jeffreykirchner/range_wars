'''
parameterset periodblock edit form
'''

from django import forms

from main.models import ParameterSetTreatment
from main.models import ParameterSetPeriodblock
from main.models import HelpDocsSubject

from main.globals import PeriodblockInheritance

class ParameterSetPeriodblockForm(forms.ModelForm):
    '''
    parameterset periodblock edit form
    '''
    
    parameter_set_treatment = forms.ModelChoiceField(label='Treatment',
                                                 queryset=ParameterSetTreatment.objects.none(),
                                                 widget=forms.Select(attrs={"v-model":"current_parameter_set_periodblock.parameter_set_treatment",}))
    
    period_start = forms.IntegerField(label='Period Start',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_periodblock.period_start",
                                                                      "step":"1",
                                                                       "min":"1"}))
    
    period_end = forms.IntegerField(label='Period End',
                                    min_value=1,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_periodblock.period_end",
                                                                    "step":"1",
                                                                    "min":"1"}))
    
    inheritance = forms.ChoiceField(label='Inheritance',
                                    choices=PeriodblockInheritance.choices,
                                    widget=forms.Select(attrs={"v-model":"current_parameter_set_periodblock.inheritance",}))

    help_doc = forms.ModelChoiceField(label='Optional Help Doc Pop-Up',
                                             required=False,
                                             queryset=HelpDocsSubject.objects.none(),
                                             widget=forms.Select(attrs={"v-model":"current_parameter_set_periodblock.help_doc",}))
    
    class Meta:
        model=ParameterSetPeriodblock
        fields =[ 'parameter_set_treatment', 'period_start', 'period_end', 'inheritance', 'help_doc', 'inheritance']
    
