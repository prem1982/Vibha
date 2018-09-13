from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext,loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import get_object_or_404,redirect
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMessage, SMTPConnection
from django.db.models import Sum
from django.conf import settings
from django.contrib.sites.models import Site

from vibha.projects.models import Project
from vibha.projectfilter.models import FeaturedProject
from vibha.donorportal.models import Cart,Campaign,Donation,Message,WatchProject
from vibha.donorportal.forms import RaiseFundsForm,TellFriendsForm
from vibha.debug import ipython, idebug

@login_required
def portal_home(request):
    return render_to_response('donorportal/portal-menu.html',{},RequestContext(request))

@login_required
def watch_project_toggle(request,project_slug):
    project = get_object_or_404(Project,slug=project_slug)
    try:
        watch_project = WatchProject.objects.get(user=request.user,
                                                 project=project)
        watch_project.delete()
        request.user.message_set.create(message='Project %s removed from watch list.'%project.name)
    except:
        watch_project = WatchProject.objects.create(user=request.user,
                                                    project=project)
        request.user.message_set.create(message='Project %s added to the watch list'%project.name)
    return redirect('portal_watch')

@login_required
def portal_watch(request):
    in_watchlist = True
    projects = [wp.project for wp in request.user.watchproject_set.all()]
    return render_to_response('donorportal/watch_projects.html',
                              {'projects':projects, 'in_watchlist':in_watchlist},
                              RequestContext(request))

@login_required
def cart_submit(request):
    if request.POST.get('update-cart',''):
        amount_list = request.POST.getlist('amount')
        cart_entries = request.user.cart_set.all()
        for index,item in enumerate(cart_entries):
            ''' Figure out the maximum donation possible. This should not exceed the
            project budget or the campaign goals
            '''
            project_funding_amount = long(item.project.latest_funding().budget)
            funding_needed =  project_funding_amount - (item.project.donation_portal.aggregate(total=Sum('amount'))['total'] or 0)
            if item.campaign is not None:
                funding_needed = min(item.campaign.amount_remaining(),funding_needed)

            try:
                item.amount = Decimal(amount_list[index])
                if item.amount > funding_needed:
                    request.user.message_set.create(message='Your donation amount %s for %s exceeded max needed, so it has been set to %s'%(item.amount,item.project,funding_needed))
                    item.amount = funding_needed
                assert item.amount > 0
                item.save()
            except:
                request.user.message_set.create(message='Value entered for the donation of %s did not seem to be valid amount'%item.project)

        request.user.message_set.create(message='Project donation amounts in the cart have been updated')
        return HttpResponseRedirect(reverse(portal_cart))
    else:
        return cart_checkout(request)


def donation(**kwargs):
    """
    All the checkouts are routed through here.

    values = dict(
    user = request.user,
    amount = request.POST['amount'],
    campaign = request.POST['campaign'],
    )
    """

    donation = Donation(**kwargs)
    return donation.save()

from vibha.donorportal.forms import DonationAmountForm

def cart_checkout(request):
    cart_entries = request.user.cart_set.all()
    total_amount = cart_entries.aggregate(total_amount=Sum('amount'))['total_amount']
    if total_amount is None:
        return HttpResponseRedirect(reverse('portal_donations'))
    form = DonationAmountForm(request,total_amount)
    if request.POST.get('cart_checkout')=='Confirm':
        form = DonationAmountForm(data=request.POST,request=request,total_amount=total_amount)
        if form.is_valid():

            #Verify cart amount equal to donated amount?
            if total_amount == form.cleaned_data['amount']:

                donations = []
                current_donation_details = {'total_amount':total_amount,'donations':donations}
                for cart_obj in cart_entries:

                    #Add donation object
                    donation_id = donation(user=cart_obj.user,
                                        amount=cart_obj.amount,
                                        project=cart_obj.project,
                                        campaign=cart_obj.campaign)

                    donations.append({ 'user' : cart_obj.user,
                                       'amount' : cart_obj.amount,
                                       'project': cart_obj.project,
                                       'campaign': cart_obj.campaign,
                                       'donation': donation_id,
                                       })

                    form.save(cart_obj.project,cart_obj.campaign, donation_id)
                    #remove cart object
                    cart_obj.delete()

                
                request.session['current_donation_details'] = current_donation_details
                send_donation_receipt_mails(current_donation_details,request)
                request.user.message_set.create(message='Thank you for the donation of %s. A confirmation of your donation has been sent to your email %s. '%(total_amount,request.user.email))
                return HttpResponseRedirect(reverse('portal_donations'))

    return render_to_response('donorportal/donation_form.html',{'form':form},RequestContext(request))

from django.template import loader
from django.contrib.sites.models import Site

def send_donation_receipt_mails(current_donation_details,request):
    try:
        master_donation = current_donation_details['donations'][0]['donation'].master.get()
    except:
        return

    extra_context = {'site':Site.objects.get_current(),
                     'current_donation_details':current_donation_details,
                     'donation':master_donation
                     }
    context = RequestContext(request,
                             extra_context)


    user_message = loader.render_to_string('email_templates/receipt_email.txt',context)
    admin_message = loader.render_to_string('email_templates/receipt_admin_email.txt',context)

    send_mail(subject='Donation by %s' % (request.user.get_full_name() or request.user.username),
              message=admin_message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list = ['donations@vibha.org', 'office@vibha.org',],
              fail_silently=False,
              )

    send_mail(subject='Thank you for the donation',
              message=user_message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list = [request.user.email,],
              fail_silently=False,
              )


def fake_donation(**kwargs):
    """
    values = dict(
    user = request.user,
    amount = request.POST['amount'],
    campaign = request.POST['campaign'],
    )
    """
    #values.update(details)
    donation = Donation(**kwargs)
    return donation.save()

@login_required
def portal_projects(request):
    ds = Donation.objects.filter(user=request.user)
    cs = Campaign.objects.filter(user=request.user)
    project_ids = [el.project_id for el in ds] + [el.project_id for el in cs]
    projects = Project.objects.filter(id__in=project_ids)
    return render_to_response('donorportal/portal-projects.html',{'projects':projects},RequestContext(request))


@login_required
def delete_cart_element(request,cart_element_id):
    cart_obj = Cart.objects.get(pk=cart_element_id,user=request.user)
    project = cart_obj.project
    if request.method == 'POST':
        if request.POST.get('confirm_delete_cart','')=='Yes':
            cart_obj.delete()
            request.user.message_set.create(message='Project %s removed from your cart'%project.name)
        else:
            request.user.message_set.create(message='Project removal from cart cancelled')
        return HttpResponseRedirect(reverse(portal_cart))
    return render_to_response('donorportal/cart_remove_confirm.html',{'project':project},RequestContext(request))


@login_required
def portal_cart(request):
    user = request.user
    if request.method == 'POST':

        if request.POST.get('pid',''):
            req_project = get_object_or_404(Project,id=request.POST['pid'])
            amount = int(request.POST.get('amount','100'))
            if Cart.objects.filter(user=user,
                                   project=req_project).count():
                user.message_set.create(message='Project already exists in cart')
            else:
                request.user.cart_set.create(project=req_project,
                                             amount=amount,)
                user.message_set.create(message='Project added to cart')

        else:

            req_campaign = get_object_or_404(Campaign,id=request.POST['cid'])
            if Cart.objects.filter(user=user,
                                   campaign=req_campaign).count():
                user.message_set.create(message='Campaign already exists in cart')
            else:
                request.user.cart_set.create(campaign=req_campaign,
                                             project=req_campaign.project,
                                             amount=100,)
                user.message_set.create(message='Project of the campaign added to cart')


    cart_entries = user.cart_set.all()
    featured_projects = FeaturedProject.objects.all()
    total_amount = cart_entries.aggregate(total_amount=Sum('amount'))['total_amount']
    return render_to_response('donorportal/portal-cart.html',
                              {'cartdetails':cart_entries,
                               'total_amount':total_amount,
                               'featured_projects':featured_projects},
                              RequestContext(request))

def campaign(request,campaign_id):
    campaign1 = get_object_or_404(Campaign,id=campaign_id)
    donations = campaign1.donation_set.all()
    return render_to_response('donorportal/campaign.html',
                              {'campaign':campaign1,
                               'donations':donations,
                               'show_permalink':False},
                              RequestContext(request))

def campaign_list(request):
    campaigns = Campaign.objects.get_non_completed()
    successfull = False
    if request.GET.get('show')=='successfull':
        campaigns = Campaign.objects.get_successful()
        successfull = True
    return render_to_response('donorportal/campaigns.html',
                              {'campaigns':campaigns,
                               'successfull':successfull,
                               'show_permalink':True,
                               },
                              RequestContext(request))

@login_required
def create_campaign_start(request):
    if request.method == 'POST':
        project = Project.objects.get(id=int(request.POST['pid']))
        funding_detail = project.projectfundingdetail_set.latest('end_date')
        funding_detail_value = long(funding_detail.budget)
        to_session = {'project':project,'funding_detail':funding_detail}
        raise_funds_form = RaiseFundsForm()
        payload = locals()
        request.session.update(to_session)
        return render_to_response('donorportal/create_campaign1.html',payload,RequestContext(request))
    else: return HttpResponseRedirect(reverse('list_projects'))

@login_required
def create_campaign_donate(request):
    if request.method == 'POST':
        raise_funds_form = RaiseFundsForm(request.POST)
        funding_detail_value = long(request.session['funding_detail'].budget)
        if raise_funds_form.is_valid() and raise_funds_form.cleaned_data['campaign_amount'] <= funding_detail_value:
            request.session.update(raise_funds_form.cleaned_data)
            form = DonationAmountForm(request,total_amount=request.session['donating_amount'])
            return render_to_response('donorportal/create_campaign2.html',{'form':form},RequestContext(request))
        else:
            payload = locals()
            request.user.message_set.create(message='Form has errors. Please correct. Campaign amount has to be less than or equal to funding required')
            payload.update(request.session)
            return render_to_response('donorportal/create_campaign1.html',payload,RequestContext(request))
    else: return HttpResponseRedirect(reverse('list_projects'))

from vibha.donorportal.forms import MessageForm
from decimal import Decimal

@login_required
def create_campaign_message(request):
    if request.method == 'POST':
        if not 'project' in request.session:
            project = Project.objects.get(id=int(request.POST['pid']))
            funding_detail = project.projectfundingdetail_set.latest('end_date')
            funding_detail_value = long(funding_detail.budget)
            to_session = {'project':project,'funding_detail':funding_detail}
            request.session.update(to_session)
        else:
            project = request.session['project']
            funding_detail = request.session['funding_detail']
            funding_detail_value = long(funding_detail.budget)


        ''' 
        if request.POST.has_key('confirmed'):
            form = DonationAmountForm(data=request.POST,request=request,total_amount=request.session['donating_amount'])
            if not form.is_valid():
                return render_to_response('donorportal/create_campaign2.html',{'form':form},RequestContext(request))

            assert form.cleaned_data['amount'] == request.session['donating_amount']
            request.session['donated_amount'] = form.cleaned_data['amount']
        '''

        #Message form post request
        form = MessageForm()
        if request.POST.get('form-type')=='message-form':
            form = MessageForm(request.POST)

        if form.is_valid():
            values = {}
            values.update(request.session)
            values.update(form.cleaned_data)
            camp_values = {'user':request.user,
                           'amount':int(values['campaign_amount']),
                           #This is 0, but the added donation, auto adds that value to donated.
                           'amount_collected':0,
                           'description':values['description'],
                           'project':values['project'],
                           'end_date':values['campaign_end_date']
                           }
            del request.session['project']
            camp = Campaign.objects.create(**camp_values)
            #donation = Donation()
            #donation.campaign = camp
            #donation.user = request.user
            #donation.amount = long(values['donated_amount'])
            #donation.save()

            extra_context = {'site': Site.objects.get_current(),
                             'campaign':camp}
            extra_context.update(values)
            mail_context = RequestContext(request,extra_context)
            mail_message = loader.render_to_string('email_templates/campaign_mail.txt',mail_context)
            subject='%s is raising funds for %s project on Vibha'%(request.user.get_full_name(),values['project'].name)
            from_email=settings.DEFAULT_FROM_EMAIL

            # Split into several messages so recipients dont see the other recipients
            msg = []
            for recipient in form.cleaned_data['to_email_field']:
                m = EmailMessage(subject,mail_message,from_email,[recipient])
                m.content_subtype = "html"
                msg.append(m)

            connection = SMTPConnection()
            connection.send_messages(msg)


            return HttpResponseRedirect('../campaign/%s/' %(camp.id))
        payload = locals()
        return render_to_response('donorportal/create_campaign3.html',payload,RequestContext(request))
    else: return HttpResponseRedirect(reverse('list_projects'))


#This method is not being used, right now
@login_required
def create_campaign_page(request):
    if request.method == 'POST':
        idebug()
        values = request.session
        values.update(request.POST)
        camp = Campaign()
        camp.amount = values['campaign_amount']
        camp.amount_collected = values['donated_amount']
        camp.description = values['description']
        camp.project = Project.objects.get(id=int(values['pid']))
        camp.save()
        donation = Donation()
        donation.campaign = camp
        donation.user = req.user
        donation.amount = values['donated_amount']
        donation.save()
    return HttpResponseRedirect(reverse('list_projects'))


@login_required
def portal_donations(request):
    donations = request.user.donation_set.all()
    return render_to_response('donorportal/donations.html',locals(),RequestContext(request))

@login_required
def portal_campaigns(request):
    campaigns = request.user.campaign_set.all()
    show_permalink = True
    return render_to_response('donorportal/user-campaigns.html',locals(),RequestContext(request))

@login_required
def duplicate_receipt(request):
    donation = get_object_or_404(Donation,id=request.POST.get('did'),user=request.user)
    context = RequestContext(request,dict(
        site=Site.objects.get_current(),
        donation=donation.master.get()
    ))

    email_message = loader.render_to_string('email_templates/receipt_email.txt',context)

    send_mail(subject='Duplicate receipt for your donation',
              message=email_message,
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list = [request.user.email,],
              fail_silently=False,
              )

    request.user.message_set.create(message='A duplicate email receipt has been sent to you')
    return redirect('portal_donations')


def debug(request):
    project = Project.objects.all()[0]
    payload = locals()
    return render_to_response('project_part.html',payload)
