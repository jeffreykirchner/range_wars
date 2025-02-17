'''
parameterset player_group edit form
'''

from django import forms

from main.models import ParameterSetPlayerGroup

class ParameterSetPlayerGroupForm(forms.ModelForm):
    '''
    parameterset player_group edit form
    '''

    group_number = forms.IntegerField(label='Group Number',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player_group.group_number",
                                                                      "step":"1",
                                                                      "min":"1"}))
    
    position = forms.IntegerField(label='Position',
                                  min_value=1,
                                  widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player_group.position",
                                                                   "step":"1",
                                                                   "min":"1"}))
    
    start_box = forms.IntegerField(label='Start Box',
                                    min_value=0,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_player_group.start_box",
                                                                    "step":"1",
                                                                    "min":"0"}))

   
    class Meta:
        model=ParameterSetPlayerGroup
        fields =['group_number', 'position', 'start_box']
    
