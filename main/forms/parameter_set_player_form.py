'''
parameterset player edit form
'''

from django import forms

from main.models import ParameterSetPlayer
from main.models import InstructionSet

class ParameterSetPlayerForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    id_label = forms.CharField(label='Label Used in Chat',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.id_label",}))
    
    hex_color = forms.CharField(label='Color (e.g. 0x00AABB, Crimson)',
                                widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.hex_color",}))
    
    instruction_set = forms.ModelChoiceField(label='instruction_set',
                                             empty_label=None,
                                             queryset=InstructionSet.objects.all(),
                                             widget=forms.Select(attrs={"v-model":"current_parameter_set_player.instruction_set",}))

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'hex_color','instruction_set']
    
