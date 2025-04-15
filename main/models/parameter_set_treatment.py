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
    
    id_label_pst = models.CharField(verbose_name='ID Label', max_length=100, default="Name Here")      #id label shown on screen to subjects

    range_width = models.DecimalField(verbose_name='Range Width', default=2, max_digits=7, decimal_places=4)             #range width
    range_height = models.DecimalField(verbose_name='Range Height', default=2, max_digits=7, decimal_places=4)           #range height
    
    scale_width = models.DecimalField(verbose_name='Scale Width', default=2, max_digits=7, decimal_places=4)           #scale width
    scale_height = models.DecimalField(verbose_name='Scale Height', default=2, max_digits=7, decimal_places=4)         #scale height

    values = models.CharField(verbose_name='Values', max_length=5000, default="10,9,8,7,6,5,4,3,2,1")   
    values_count = models.IntegerField(verbose_name='Values Count', default=100)

    scale_height_ticks = models.IntegerField(verbose_name='Scale Height Ticks', default=10)                              #range height ticks

    costs = models.CharField(verbose_name='Costs', max_length=100, default="0,0,0,0")    #costs for each Vertex
    cost_percent = models.DecimalField(verbose_name='Scale Width', default=0.1, max_digits=7, decimal_places=4) 

    cost_area = models.DecimalField(verbose_name='Cost Area', default=0, max_digits=8, decimal_places=4)
    revenue_area = models.DecimalField(verbose_name='Revenue Area', default=0, max_digits=8, decimal_places=4)

    preserve_order = models.BooleanField(verbose_name='Preserve Order', default=False)                        #preserve order of players on battle space
    enable_chat = models.BooleanField( verbose_name='Enable Chat', default=True)                              #if true enable chat
    enable_transfer_cents = models.BooleanField(verbose_name='Enable Money Transfer', default=True)          #if true enable chat
    enable_contest = models.BooleanField(verbose_name='Enable Contest', default=True)                         #if true enable contest
    enable_ready_button = models.BooleanField(verbose_name='Enable Ready Button', default=True)               #if true enable ready button

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

        self.scale_width = new_ps.get("scale_width", 2)
        self.scale_height = new_ps.get("scale_height", 2)

        self.values = new_ps.get("values", "")
        self.values_count = new_ps.get("values_count", 100)

        self.scale_height_ticks = new_ps.get("scale_height_ticks")

        self.costs = new_ps.get("costs")
        self.cost_percent = new_ps.get("cost_percent", 0.5)

        self.cost_area = new_ps.get("cost_area", 0)
        self.revenue_area = new_ps.get("revenue_area", 0)

        self.preserve_order = True if new_ps.get("preserve_order") else False
        self.enable_chat = True if new_ps.get("enable_chat") else False
        self.enable_transfer_cents = True if new_ps.get("enable_transfer_cents") else False
        self.enable_contest = True if new_ps.get("enable_contest") else False
        self.enable_ready_button = True if new_ps.get("enable_ready_button") else False

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
            "values_count" : self.values_count,
            # "values_order" : self.values.split(","),

            "scale_height_ticks" : self.scale_height_ticks ,

            "costs" : self.costs,
            "cost_percent" : self.cost_percent,

            "cost_area" : self.cost_area,
            "revenue_area" : self.revenue_area,

            "preserve_order" : 1 if self.preserve_order else 0,
            "enable_chat" : 1 if self.enable_chat else 0,
            "enable_transfer_cents" : 1 if self.enable_transfer_cents else 0,
            "enable_contest" : 1 if self.enable_contest else 0,
            "enable_ready_button" : 1 if self.enable_ready_button else 0,
        }
    
    def get_json_for_subject(self, update_required=False):
        '''
        return json object for subject screen, return cached version if unchanged
        '''

        v = self.parameter_set.json_for_session["parameter_set_players"][str(self.id)]

        # edit v as needed

        return v


