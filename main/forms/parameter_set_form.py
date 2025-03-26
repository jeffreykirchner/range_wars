'''
Parameterset edit form
'''

from django import forms

from main.models import ParameterSet

import  main

class ParameterSetForm(forms.ModelForm):
    '''
    Parameterset edit form
    '''

    period_length = forms.IntegerField(label='Period Length (sec)',
                                       min_value=1,
                                       widget=forms.NumberInput(attrs={"v-model":"parameter_set.period_length",
                                                                       "step":"1",
                                                                       "min":"250"}))
    
    show_instructions = forms.ChoiceField(label='Show Instructions',
                                          choices=((1, 'Yes'), (0,'No' )),
                                          widget=forms.Select(attrs={"v-model":"parameter_set.show_instructions",}))

    survey_required = forms.ChoiceField(label='Show Survey',
                                        choices=((1, 'Yes'), (0,'No' )),
                                        widget=forms.Select(attrs={"v-model":"parameter_set.survey_required",}))

    survey_link =  forms.CharField(label='Survey Link',
                                   required=False,
                                   widget=forms.TextInput(attrs={"v-model":"parameter_set.survey_link",}))
    
    prolific_mode = forms.ChoiceField(label='Prolific Mode',
                                      choices=((1, 'Yes'), (0,'No' )),
                                      widget=forms.Select(attrs={"v-model":"parameter_set.prolific_mode",}))

    prolific_completion_link =  forms.CharField(label='After Session, Forward Subjects to URL',
                                                required=False,
                                                widget=forms.TextInput(attrs={"v-model":"parameter_set.prolific_completion_link",}))
    
    reconnection_limit = forms.IntegerField(label='Re-connection Limit',
                                            min_value=1,
                                            widget=forms.NumberInput(attrs={"v-model":"parameter_set.reconnection_limit",
                                                                            "step":"1",
                                                                            "min":"1"}))     

    inheritance_window = forms.IntegerField(label='Inheritance Window',
                                            min_value=1,
                                            widget=forms.NumberInput(attrs={"v-model":"parameter_set.inheritance_window",
                                                                            "step":"1",
                                                                            "min":"1"}))                                                        

    test_mode = forms.ChoiceField(label='Test Mode',
                                  choices=((1, 'Yes'), (0, 'No')),
                                  widget=forms.Select(attrs={"v-model":"parameter_set.test_mode",}))

    class Meta:
        model=ParameterSet
        fields =['period_length',
                 'show_instructions',
                 'survey_required', 'survey_link', 'prolific_mode', 'prolific_completion_link', 'reconnection_limit',
                 'inheritance_window', 'test_mode']

    def clean_survey_link(self):
        
        try:
           survey_link = self.data.get('survey_link')
           survey_required = self.data.get('survey_required')

           if survey_required and not "http" in survey_link:
               raise forms.ValidationError('Invalid link')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return survey_link
    
    def clean_prolific_completion_link(self):
        
        try:
           prolific_completion_link = self.data.get('prolific_completion_link')
           prolific_mode = self.data.get('prolific_mode')

           if prolific_mode and not "http" in prolific_completion_link:
               raise forms.ValidationError('Enter Prolific completion URL')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return prolific_completion_link
