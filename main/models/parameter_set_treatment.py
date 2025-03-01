'''
parameterset treatment 
'''

from django.db import models

from main.models import ParameterSet
from main.models import InstructionSet

class ParameterSetTreatment(models.Model):
    '''
    session treatment parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_treatments")
    
    id_label_pst = models.CharField(verbose_name='ID Label', max_length=30, default="Name Here")      #id label shown on screen to subjects

    range_width = models.DecimalField(verbose_name='Range Width', default=2, max_digits=5, decimal_places=2)             #range width
    range_height = models.DecimalField(verbose_name='Range Height', default=2, max_digits=5, decimal_places=2)           #range height
    
    scale_width = models.DecimalField(verbose_name='Scale Width', default=2, max_digits=5, decimal_places=2)           #scale width
    scale_height = models.DecimalField(verbose_name='Scale Height', default=2, max_digits=5, decimal_places=2)           #scale height

    values = models.CharField(verbose_name='Values', max_length=1000, default="10,9,8,7,6,5,4,3,2,1")                     #Values for each box

    range_height_ticks = models.IntegerField(verbose_name='Range Height Ticks', default=10)                              #range height ticks

    costs = models.CharField(verbose_name='Costs', max_length=100, default="0,0,0,0")    #costs for each Vertex

    preserve_order = models.BooleanField(verbose_name='Preserve Order', default=False)   #preserve order of players on battle space

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id_label_pst)
    
    class Meta:
        verbose_name = 'Parameter Set Treatment'
        verbose_name_plural = 'Parameter Set Treatments'
        ordering=['id_label_pst']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset treatment
        '''

        self.id_label_pst = new_ps.get("id_label_pst")

        self.range_width = new_ps.get("range_width")
        self.range_height = new_ps.get("range_height")

        self.scale_width = new_ps.get("scale_width")
        self.scale_height = new_ps.get("scale_height")

        self.values = new_ps.get("values")

        self.range_height_ticks = new_ps.get("range_height_ticks")

        self.costs = new_ps.get("costs")

        self.preserve_order = True if new_ps.get("preserve_order") else False

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

            "range_width" : self.range_width,
            "range_height" : self.range_height,

            "scale_width" : self.scale_width,
            "scale_height" : self.scale_height,

            "values" : self.values,

            "range_height_ticks" : self.range_height_ticks ,

            "costs" : self.costs,

            "preserve_order" : 1 if self.preserve_order else 0,
        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_players"][str(self.id)]

        # edit v as needed

        return v


