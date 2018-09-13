# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.template import loader
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Max,F
from django.contrib.auth.decorators import login_required

from vibha.projects.models import Project,State,FocusArea,ProjectFundingDetail
from vibha.donorportal.models import WatchProject, Donation
from vibha.donorportal.forms import TellFriendsForm
from vibha.search.utils import search_whoosh

from vibha.debug import ipython

def search(request):
    q = request.REQUEST.get('q','')
    r = search_whoosh(q)
    project_pks = [res['pk'] for res in r]
    projects = Project.objects.filter(pk__in=project_pks)[:10]
    active_link = 1
    return render_to_response('projectfilter/vibha_search.html',locals(),RequestContext(request))


@login_required
def tell_friend(request,slug):
    project = get_object_or_404(Project,slug=slug)
    if request.method=='POST':
        form = TellFriendsForm(data=request.POST,request=request)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message='Your emails have been sent')
            return redirect(project_page,slug)
    else:
        extra_context = dict(project=project,
                             site=Site.objects.get_current())
        context = RequestContext(request,extra_context)
        project_info = loader.render_to_string('email_templates/tell_friends.txt',context)
        form = TellFriendsForm(request=request,initial={'project_info':project_info})
    return render_to_response('projectfilter/tell_friend.html',
            {'form':form}, RequestContext(request))


def project_page(request,project_slug):
    project = get_object_or_404(Project,slug=project_slug)
    try:
        latest_funding = project.latest_funding()
        total_funding_required = long(latest_funding.budget)
        funding_needed =  total_funding_required - \
                (project.donation_portal.filter(date__gte=latest_funding.begin_date)\
                .aggregate(total=Sum('amount'))['total'] or 0)
    except:
        total_funding_required = 0
        funding_needed = 0

    if funding_needed < 0:
        funding_needed = 0
    try:
        is_watched = request.user.watchproject_set.filter(project=project).count()
    except:
        is_watched = False

    """ Show only reports of type
        Quaterly, Half-yearly, Annual and Newsletter"""
    """if request.user.is_authenticated():
        relevant_reports = project.report_set.all()[:4]
    else:
        relevant_reports = project.report_set.filter(show=1).filter(report_type__in=[5,6,7,11]).order_by('-report_date')[:4]
    """
    relevant_reports = project.get_relevant_reports()
    budgets = project.projectbudget_set.filter(is_active=True)
    budgets_total = budgets.aggregate(sum=Sum('subtotal'))['sum']

    picture = project.get_random_picture() 
    active_link = 1

    if request.user.is_authenticated():
        # Determine if the user has contrirbuted to this project
        donation = Donation.objects.filter(user__exact=request.user).\
                filter(project__exact=project).order_by('-date')
        if len(donation) > 0:
            donation = donation[0]
        else:
            donation = None

    payload = locals()
    return render_to_response('projectfilter/project-detail.html',payload,RequestContext(request))


from vibha.projectfilter.forms import FilterForm,funding_list

def filter_projects(request):
    projects_list = Project.objects.filter(show_adopt_project=True)
    
    form1 = FilterForm()
    states_list = State.objects.filter(location__project__in=projects_list).distinct()
    focus_list = FocusArea.objects.filter(focussubarea__project__in=projects_list).distinct()

    if request.method =='GET':
        if (request.REQUEST.has_key('state')):
            form1 = FilterForm(request.REQUEST)
            projects_list = projects_list.filter(location__state=request.REQUEST['state']).distinct()
            
        if (request.REQUEST.has_key('focus_area')):
            form1 = FilterForm(request.REQUEST)
            projects_list = projects_list.filter(focus_areas__focus=request.REQUEST['focus_area']).distinct()

    if (request.method=='POST'):
        form1 = FilterForm(request.POST)        
        if request.POST.get('state'):
            projects_list = projects_list.filter(location__state=request.POST['state']).distinct()
        if request.POST.get('focus_area'):
            projects_list = projects_list.filter(focus_areas__focus=request.POST['focus_area']).distinct()
            
        
        if request.POST.get('funding_required',''):
            if request.POST['funding_required']=='1':
                projects_list = get_remaining_funding_projects(projects_list,500,0)
            elif request.POST['funding_required']=='2':
                projects_list = get_remaining_funding_projects(projects_list,1000,500)
            elif request.POST['funding_required']=='3':
                projects_list = get_remaining_funding_projects(projects_list,2500,1000)
            elif request.POST['funding_required']=='4':
                projects_list = get_remaining_funding_projects(projects_list,500000,2500)
            
    active_link = 1
    payload = locals()
    return render_to_response('projectfilter/browse-project.html',payload,RequestContext(request))

def get_latest_pfds(**kwargs):
    return list(ProjectFundingDetail.objects.annotate(latest=Max('project__projectfundingdetail__end_date')).filter(end_date=F('latest')).filter(**kwargs).select_related())

def get_remaining_funding_projects(projects_list,maxamount,minamount=0):
    ''' Get a list of projects whose remaining funding is between
    min and max amount'''

    projects = []
    for p in projects_list:
        latest_funding = p.latest_funding()
        try:
            total_funding_required = long(latest_funding.budget)
        except:
            total_funding_required = 0
        raised = (p.donation_portal.filter(date__gte=latest_funding.begin_date).aggregate(total=Sum('amount'))['total'] or 0)
        funding_needed =  total_funding_required - raised

        if funding_needed > minamount and funding_needed <= maxamount:
            projects.append(p)

    return projects


from vibha.projectfilter.models import FeaturedProject
def home(request):
    projects_list = Project.objects.filter(show_adopt_project=True)
    states_list = State.objects.filter(location__project__in=projects_list).distinct()
    focus_list = FocusArea.objects.filter(focussubarea__project__in=projects_list).distinct()

    fps = FeaturedProject.objects.all().order_by('?')

    zipped = []
    for fp in fps:
        project = fp.project
        latest_funding = project.latest_funding()
        try:
            total_funding_required = long(latest_funding.budget)
        except:
            total_funding_required = 0
        raised = (project.donation_portal.filter(date__gte=latest_funding.begin_date).aggregate(total=Sum('amount'))['total'] or 0)
        funding_needed =  total_funding_required - raised
        if funding_needed < 0:
            funding_needed = 0

        percent = raised*100/total_funding_required
        if percent > 100:
            percent = 100
        zipped.append((
                fp, # project
                len(project.get_relevant_reports()), # Report count
                project.donation_portal.aggregate(donations=Count('amount'))['donations'], # Donation count
                raised, # Money raised
                funding_needed, # Money Remaining
                total_funding_required, # Total funding required
                percent # Percentage raised
                ))

    # Feed from ViBlog
    import feedparser
    rss = feedparser.parse("http://vibhablog.wordpress.com/feed/")
    for i in range(0,3): # Fix http links
        try:
            rss['entries'][i]['media_content'][1]['url'] = rss['entries'][i]['media_content'][1]['url'].replace("http://","https://")
        except:
            rss['entries'][i]['media_content'].append({'url': '/vibha-media/img/twitterAvatar.jpg'})


    return render_to_response('projectfilter/home-page.html',
                              {'fps':zipped,
                                  'focusareas':focus_list,
                                  'states':states_list,
                                  'rss':rss['entries'][0:3],
                                  'active_link':0
                                  },
                              RequestContext(request))

