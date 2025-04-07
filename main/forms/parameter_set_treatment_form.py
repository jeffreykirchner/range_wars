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
    
    scale_width = forms.DecimalField(label='Scale Width',
                                        min_value=0,
                                        widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.scale_width",
                                                                        "step":"1",
                                                                        "min":"0"}))
    
    scale_height = forms.DecimalField(label='Scale Height',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.scale_height",
                                                                     "step":"1",
                                                                     "min":"0"}))

    scale_height_ticks = forms.IntegerField(label='Scale Height Ticks',
                                            min_value=1,
                                            widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.scale_height_ticks",
                                                                            "step":"1",
                                                                            "min":"1"}))
    
    # values = forms.CharField(label='Values',
    #                         widget=forms.TextInput(attrs={"v-model":"current_parameter_set_treatment.values",
    #                                                       "autocomplete":"off",}))

    values_count = forms.IntegerField(label='Values Count',
                                    min_value=10,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.values_count",
                                                                    "step":"1",
                                                                    "min":"1"}))
    
    # costs = forms.CharField(label='Costs',
    #                         widget=forms.TextInput(attrs={"v-model":"current_parameter_set_treatment.costs",
    #                                                       "autocomplete":"off",}))
    
    cost_percent = forms.DecimalField(label='Cost Y Intercept',
                                        min_value=0,
                                        max_value=1,
                                        widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_treatment.cost_percent",
                                                                        "step":"0.1",
                                                                        "min":"0",
                                                                        "max":"1"}))
    
    preserve_order = forms.ChoiceField(label='Preserve Order',
                                      choices=((1, 'Yes'), (0, 'No')),
                                      widget=forms.Select(attrs={"v-model":"current_parameter_set_treatment.preserve_order",}))
    
    enable_chat = forms.ChoiceField(label='Enable Chat',
                                    choices=((1, 'Yes'), (0, 'No')),
                                    widget=forms.Select(attrs={"v-model":"current_parameter_set_treatment.enable_chat",}))
    
    enable_transfer_cents = forms.ChoiceField(label='Enable Profit Transfer',
                                              choices=((1, 'Yes'), (0, 'No')),
                                              widget=forms.Select(attrs={"v-model":"current_parameter_set_treatment.enable_transfer_cents",}))

    enable_contest = forms.ChoiceField(label='Enable Contest',
                                       choices=((1, 'Yes'), (0, 'No')),
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set_treatment.enable_contest",}))
    
    enable_ready_button = forms.ChoiceField(label='Enable Ready Button',
                                            choices=((1, 'Yes'), (0, 'No')),
                                            widget=forms.Select(attrs={"v-model":"current_parameter_set_treatment.enable_ready_button",}))

    class Meta:
        model=ParameterSetTreatment
        fields =['id_label_pst',  'range_width', 'range_height', 'scale_width', 'scale_height',
                 'scale_height_ticks', 'values_count', 'cost_percent', 
                 'preserve_order', 'enable_chat', 'enable_transfer_cents', 'enable_contest', 'enable_ready_button',]
    
