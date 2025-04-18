'''
instruction set form
'''
from django import forms
from main.models import InstructionSet

class InstructionSetForm(forms.ModelForm):
    '''
    instruction set form 
    '''

    label = forms.CharField(label='Instruction Set Name',
                            widget=forms.TextInput(attrs={"width":"300px",
                                                          "v-model":"instruction_set.label",
                                                          "placeholder" : "Instruction Set Name"}))
    
    action_page_1 = forms.IntegerField(label='Required Action: Move Range', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                       "v-model":"instruction_set.action_page_1",
                                                                       "placeholder" : "Page Number"}))
    
    action_page_2 = forms.IntegerField(label='Required Action: Submit Range', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                        "v-model":"instruction_set.action_page_2",
                                                                       "placeholder" : "Page Number"}))
    
    action_page_3 = forms.IntegerField(label='Required Action: Roll Overs', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                       "v-model":"instruction_set.action_page_3",
                                                                       "placeholder" : "Page Number"}))
    
    action_page_4 = forms.IntegerField(label='Required Action: 4', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                       "v-model":"instruction_set.action_page_4",
                                                                       "placeholder" : "Page Number"}))
    
    action_page_5 = forms.IntegerField(label='Required Action: 5', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                       "v-model":"instruction_set.action_page_5",
                                                                       "placeholder" : "Page Number"}))
    
    action_page_6 = forms.IntegerField(label='Required Action: 6', 
                                       widget=forms.NumberInput(attrs={"min":"1", 
                                                                       "v-model":"instruction_set.action_page_6",
                                                                       "placeholder" : "Page Number"}))
    
    p1_example_start_range = forms.IntegerField(label='Person 1 Example Start Range',
                                                widget=forms.NumberInput(attrs={"min":"1", 
                                                                                "v-model":"instruction_set.p1_example_start_range",
                                                                                "placeholder" : "Start Range"}))
    
    p1_example_end_range = forms.IntegerField(label='Person 1 Example End Range',
                                              widget=forms.NumberInput(attrs={"min":"1", 
                                                                              "v-model":"instruction_set.p1_example_end_range",
                                                                              "placeholder" : "End Range"}))
    
    p2_example_start_range = forms.IntegerField(label='Person 2 Example Start Range',
                                                widget=forms.NumberInput(attrs={"min":"1", 
                                                                                    "v-model":"instruction_set.p2_example_start_range",
                                                                                    "placeholder" : "Start Range"}))
    
    p2_example_end_range = forms.IntegerField(label='Person 2 Example End Range',
                                              widget=forms.NumberInput(attrs={"min":"1", 
                                                                              "v-model":"instruction_set.p2_example_end_range",
                                                                              "placeholder" : "End Range"}))
    
    p3_example_start_range = forms.IntegerField(label='Person 3 Example Start Range',
                                                widget=forms.NumberInput(attrs={"min":"1", 
                                                                                    "v-model":"instruction_set.p3_example_start_range",
                                                                                    "placeholder" : "Start Range"}))
    
    p3_example_end_range = forms.IntegerField(label='Person 3 Example End Range',
                                              widget=forms.NumberInput(attrs={"min":"1", 
                                                                              "v-model":"instruction_set.p3_example_end_range",
                                                                              "placeholder" : "End Range"}))
    

    p4_example_start_range = forms.IntegerField(label='Person 4 Example Start Range',
                                                widget=forms.NumberInput(attrs={"min":"1", 
                                                                                    "v-model":"instruction_set.p4_example_start_range",
                                                                                    "placeholder" : "Start Range"}))
    
    p4_example_end_range = forms.IntegerField(label='Person 4 Example End Range',
                                              widget=forms.NumberInput(attrs={"min":"1", 
                                                                              "v-model":"instruction_set.p4_example_end_range",
                                                                              "placeholder" : "End Range"}))
    

    class Meta:
        model=InstructionSet
        fields = ('label', 
                  'action_page_1', 'action_page_2', 'action_page_3', 'action_page_4', 'action_page_5', 'action_page_6',
                  'p1_example_start_range', 'p1_example_end_range',
                  'p2_example_start_range', 'p2_example_end_range',
                  'p3_example_start_range', 'p3_example_end_range',
                  'p4_example_start_range', 'p4_example_end_range')