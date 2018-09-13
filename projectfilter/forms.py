from django import forms
from vibha.projectfilter.models import *
from vibha.projects.models import State,FocusArea,Project

funding_list = [
    ("",'--Any Funding--'),
    (1,'Under $500'),
    (2,'$500 to $1000'),
    (3,'$1000 to $2500'),
    (4,'Over $2500'),]

class FilterForm(forms.Form):
    projects_list = Project.objects.filter(show_adopt_project=True)
    state = forms.ModelChoiceField(queryset=State.objects.filter(location__project__in=projects_list).distinct(),required=False,empty_label='--Any State--')
    focus_area = forms.ModelChoiceField(queryset = FocusArea.objects.filter(focussubarea__project__in=projects_list).distinct(),required=False,empty_label='--Any Focusarea--')
    funding_required = forms.ChoiceField(choices=funding_list,required=False)    
        
