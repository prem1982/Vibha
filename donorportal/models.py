from django.db import models
from django.contrib.auth.models import User
from vibha.projects.models import Project
from datetime import date,datetime

class Cart(models.Model):
    """
    Stores all cart details;
    To be queried with user instance only
    """
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    amount = models.DecimalField(decimal_places=2,max_digits=10,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    campaign = models.ForeignKey('Campaign',blank=True,null=True)
    
    def __unicode__(self):
        return "%s %s %s" %(self.user.username, self.project, self.campaign)
    
class Message(models.Model):
    """
    Stores all messages;
    To be queried with user instance only
    """
    from_user = models.ForeignKey(User, related_name="from_user")
    to_user = models.ForeignKey(User, related_name="to_user")
    date_sent = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=1000)
    body = models.TextField()
    
class CampaignManager(models.Manager):
    
    #Note: this is hooked to the current definition of is not completed. If change, both needs to be changed
    def get_non_completed(self):
        return self.filter(is_active=True, 
                           amount_collected__lt=models.F('amount'),
                           end_date__gte=date.today())

    def get_successful(self):
        return self.filter(amount_collected__gte=models.F('amount'))

    
class Campaign(models.Model):
    """
    Stores all campaigns in the system
    """
    user = models.ForeignKey(User)
    amount = models.DecimalField(decimal_places=2,max_digits=10)
    amount_collected = models.DecimalField(decimal_places=2,max_digits=10)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    latest_change_date = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project)
    end_date = models.DateTimeField()
    objects = CampaignManager()
    
    def __unicode__(self):
        return "%s %s %s" %(self.user.username, self.project, self.date_added)
    
    #Use this method in preference to is_active
    @property
    def is_completed(self):
        if not self.is_active:
            return True
        if self.amount_collected >= self.amount:
            return True
        if self.end_date < datetime.today():
            return True
        return False
    
    @models.permalink
    def get_absolute_url(self):
        return ['portal_campaign',(self.id,)]
    
    def how_completed(self):
        if self.is_completed:
            if not self.is_active:
                return 'Marked ended'
            if self.amount_collected >= self.amount:
                return 'Successful'
            if self.end_date < datetime.today():
                return 'Ended'
    
    def amount_remaining(self):
        return self.amount - self.amount_collected
    
class Donation(models.Model):
    """
    Each donation done for the campaign is stored in this model.
    This is to be updated after each donation to a campaign
    """
    campaign = models.ForeignKey(Campaign,blank=True,null=True)
    project = models.ForeignKey(Project,related_name='donation_portal',blank=True,null=True)
    user = models.ForeignKey(User)
    amount = models.DecimalField(decimal_places=2,max_digits=10)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date',]
        
    def save(self):
        if self.campaign is not None:
            self.project = self.campaign.project
            self.campaign.amount_collected += self.amount
            self.campaign.save()
        super(Donation,self).save()
        return self
        
    def __unicode__(self):
        return "%s %s %s" %(self.user, self.amount, self.date)



class WatchProject(models.Model):
    """
    all watch project stuff here
    """
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s %s' %(self.user, self.project)
        
