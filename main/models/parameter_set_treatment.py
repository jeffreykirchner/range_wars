'''
parameterset treatment 
'''

from django.db import models

from main.models import ParameterSet
from main.models import ParameterSetGroup
from main.models import InstructionSet

class ParameterSetTreatment(models.Model):
    '''
    session treatment parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_treatments")
    
    id_label_pst = models.CharField(verbose_name='ID Label', max_length=30, default="Name Here")      #id label shown on screen to subjects

    left_x = models.DecimalField(verbose_name='Left Vertex X', default=0, max_digits=4, decimal_places=2)               #left Vertex x
    left_y = models.DecimalField(verbose_name='Left Vertex Y', default=0, max_digits=4, decimal_places=2)               #left Vertex y
    middle_x = models.DecimalField(verbose_name='Middle Vertex X', default=1, max_digits=4, decimal_places=2)           #middle Vertex x
    middle_y = models.DecimalField(verbose_name='Middle Vertex Y', default=2, max_digits=4, decimal_places=2)           #middle Vertex y
    right_x = models.DecimalField(verbose_name='Right Vertex X', default=0, max_digits=4, decimal_places=2)             #right Vertex x
    right_y = models.DecimalField(verbose_name='Right Vertex Y', default=2, max_digits=4, decimal_places=2)             #right Vertex y

    range_width = models.DecimalField(verbose_name='Range Width', default=2, max_digits=4, decimal_places=2)             #range width
    range_height = models.DecimalField(verbose_name='Range Height', default=2, max_digits=4, decimal_places=2)           #range height

    costs = models.CharField(verbose_name='Costs', max_length=100, default="0,0,0,0")    #costs for each Vertex
    revenues = models.CharField(verbose_name='Revenues', max_length=100, default="0.25,0.25,0.25,0.25") #revenues for each Vertex

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id_label_pst)
    
    class Meta:
        verbose_name = 'Parameter Set Treatment'
        verbose_name_plural = 'Parameter Set Treatments'
        # ordering=['id_label']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset treatment
        '''

        self.id_label_pst = new_ps.get("id_label")

        self.left_x = new_ps.get("left_x")
        self.left_y = new_ps.get("left_y")
        self.middle_x = new_ps.get("middle_x")
        self.middle_y = new_ps.get("middle_y")
        self.right_x = new_ps.get("right_x")
        self.right_y = new_ps.get("right_y")

        self.range_width = new_ps.get("range_width")
        self.range_height = new_ps.get("range_height")

        self.costs = new_ps.get("costs")
        self.revenues = new_ps.get("revenues")

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
        self.parameter_set.json_for_session["parameter_set_treatments"][self.id] = self.json()

        self.parameter_set.save()

        self.save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,

            "id_label_pst" : self.id_label_pst,
            
            "left_x" : self.left_x,
            "left_y" : self.left_y,
            "middle_x" : self.middle_x,
            "middle_y" : self.middle_y,
            "right_x" : self.right_x,
            "right_y" : self.right_y,

            "range_width" : self.range_width,
            "range_height" : self.range_height,

            "costs" : self.costs,
            "revenues" : self.revenues,
        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_players"][str(self.id)]

        # edit v as needed

        return v


