'''
parameterset treatment edit form
'''

from django import forms

from main.models import ParameterSetTreatment

class ParameterSetTreatmentForm(forms.ModelForm):
    '''
    parameterset field type edit form
    '''
    
    id_label_pst = forms.CharField(label='Name',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_treatment.id_label_pst",
                                                              "autocomplete":"off",}))
    
    left_x = forms.DecimalField(label='Left X',
                                min_value=0,
                                widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.left_x",
                                                                "step":"1",
                                                                "min":"0"}))
    
    left_y = forms.DecimalField(label='Left Y',
                                min_value=0,
                                widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.left_y",
                                                                "step":"1",
                                                                "min":"0"}))
    
    middle_x = forms.DecimalField(label='Middle X',
                                  min_value=0,
                                  widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.middle_x",
                                                                  "step":"1",
                                                                  "min":"0"}))
    
    middle_y = forms.DecimalField(label='Middle Y',
                                  min_value=0,
                                  widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.middle_y",
                                                                  "step":"1",
                                                                  "min":"0"}))    
    
    right_x = forms.DecimalField(label='Right X',
                                 min_value=0,
                                 widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.right_x",
                                                                 "step":"1",
                                                                 "min":"0"}))
    
    right_y = forms.DecimalField(label='Right Y',
                                 min_value=0,
                                 widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.right_y",
                                                                 "step":"1",
                                                                 "min":"0"}))
    
    range_width = forms.DecimalField(label='Range Width',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.range_width",
                                                                     "step":"1",
                                                                     "min":"0"}))
    
    range_height = forms.DecimalField(label='Range Height',
                                      min_value=0,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.range_height",
                                                                      "step":"1",
                                                                      "min":"0"}))
    
    range_height_ticks = forms.IntegerField(label='Range Height Ticks',
                                            min_value=1,
                                            widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.range_height_ticks",
                                                                            "step":"1",
                                                                            "min":"1"}))
    
    values = forms.CharField(label='Values',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_treatment.values",
                                                          "autocomplete":"off",}))
    
    costs = forms.CharField(label='Costs',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_treatment.costs",
                                                          "autocomplete":"off",}))

    class Meta:
        model=ParameterSetTreatment
        fields =['id_label_pst', 'left_x', 'left_y', 'middle_x', 'middle_y', 'right_x', 'right_y', 
                 'range_width', 'range_height', 'range_height_ticks', 'values', 'costs']
    
