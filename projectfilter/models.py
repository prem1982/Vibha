from django.db import models
from vibha.projects.models import Project

class FeaturedProject(models.Model):
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        return self.project.name
    
class ProjectBudget(models.Model):
    project = models.ForeignKey(Project)
    cost_desc = models.CharField(max_length=100)
    num_items = models.PositiveIntegerField()
    cost_per_item = models.DecimalField(decimal_places=2,max_digits=10)
    is_active = models.BooleanField()
    subtotal = models.DecimalField(decimal_places=2,max_digits=12,editable=False)
    
    def save(self,*args,**kwargs):
        self.subtotal = self.num_items * self.cost_per_item
        super(ProjectBudget,self).save(*args,**kwargs)
    
    def __unicode__(self):
        return "%s %s %s"%(self.project,self.cost_desc,self.subtotal)
