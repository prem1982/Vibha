from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import redirect
from django.contrib.localflavor.us.forms import USPhoneNumberField,USZipCodeField,USStateField,USStateSelect
from django.contrib.auth import login,authenticate
from django.utils.datastructures import SortedDict
from django.forms.util import ErrorList

from vibha.utils.shortcuts import states_in_the_US_and_other, states_in_the_US
from vibha.registration.models import UserProfile
from vibha.registration.countries import LIST_OF_COUNTRIES
from vibha.captcha_re.fields import ReCaptchaField
from vibha.registration.utils import ReadOnlyField

from vibha.debug import ipython

class RegistrationForm(forms.Form):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    email = forms.EmailField(label="Email address")
    firstname = forms.CharField(label='First Name')
    lastname = forms.CharField(label='Last Name')
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password Again"), widget=forms.PasswordInput)
    country = forms.ChoiceField(choices=LIST_OF_COUNTRIES)
    captcha = ReCaptchaField()
    
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        for field in self.fields.itervalues():
            try:
                if field.widget.input_type == 'text':
                    field.widget.attrs['class'] = ' '.join([field.widget.attrs.setdefault('class',''),'textbox'])
            except:
                pass
            
    def clean_firstname(self):
        firstname = self.cleaned_data["firstname"].strip()

        if firstname != '':
            return firstname
        raise forms.ValidationError(_("First name cannot be blank"))

    def clean_lastname(self):
        lastname = self.cleaned_data["lastname"].strip()

        if lastname != '':
            return lastname
        raise forms.ValidationError(_("Last name cannot be blank"))

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A registered user with this email already exists"))
    

class ProfileForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(ProfileForm,self).__init__(*args,**kwargs)
        self.instance = kwargs['instance']
        self.fields.insert(0,'username',ReadOnlyField(initial=kwargs['instance'].user.username))
        self.fields.insert(1,'email',ReadOnlyField(initial=kwargs['instance'].user.email))
        self.fields.insert(2,'first_name',forms.CharField(initial=kwargs['instance'].user.first_name))
        self.fields.insert(3,'last_name',forms.CharField(initial=kwargs['instance'].user.last_name))
            
        for field in self.fields.itervalues():
            try:
                if field.widget.input_type == 'text':
                    field.widget.attrs['class'] = ' '.join([field.widget.attrs.setdefault('class',''),'textbox'])
            except:
                pass
        self.fields['state'] = forms.ModelChoiceField(queryset=states_in_the_US_and_other(),help_text='Please use "Other" listed at the end for a non-US address')
    
    #def clean(self):
        #if self.cleaned_data['country']=='US':
            #self.fields['phone_number'] = USPhoneNumberField()
            #self.fields['zipcode'] = USZipCodeField()            
            #has_exceptions = False
            #try:
                #USPhoneNumberField.clean(self.fields['phone_number'], self.cleaned_data['phone_number'])
            #except Exception, e:
                #has_exceptions = True
                #self._errors['phone_number'] = ErrorList([e.message])
                #del self.cleaned_data['phone_number']
            #if 'phone_number' in self.cleaned_data:
                #try:
                    #USPhoneNumberField.clean(self.fields['phone_number'], self.cleaned_data['phone_number'])
                #except Exception, e:
                    #has_exceptions = True
                    #self._errors['phone_number'] = ErrorList(['Phone numbers must be in XXX-XXX-XXXX'])
                    #del self.cleaned_data['zipcode']
            #if 'zipcode' in self.cleaned_data:
                #try:
                    #USZipCodeField.clean(self.fields['zipcode'], self.cleaned_data['zipcode'])
                #except Exception, e:
                    #has_exceptions = True
                    #self._errors['zipcode'] = ErrorList(['The zip code is not valid'])
                    #del self.cleaned_data['zipcode']
            #if 'state' in self.cleaned_data:
                #try:
                    #states_in_the_US().get(postal_code=self.cleaned_data['state'])
                #except:
                    #has_exceptions = True
                    #self._errors['state'] = ErrorList(['This is not a valid US state.'])
            #if has_exceptions:
                #pass
                #raise forms.ValidationError('Please fix the errors below.')
        #return self.cleaned_data
    
    def save(self):
        if 'first_name' in self.changed_data or 'last_name' in self.changed_data:
            self.instance.user.first_name = self.cleaned_data['first_name']
            self.instance.user.last_name = self.cleaned_data['last_name']
            self.instance.user.save()
        super(ProfileForm,self).save()
        #if self.changed_data.fget
        
    class Meta:
        model = UserProfile
        exclude = ['user']

class ProfileFormUS(ProfileForm):
    phone_number = USPhoneNumberField(required = False)
    zipcode = USZipCodeField(required = False)
    def __init__(self, *args, **kwargs):
        super(ProfileFormUS, self).__init__(*args, **kwargs)
        self.fields['state'] = forms.ModelChoiceField(queryset=states_in_the_US(),help_text='Please use "Other" listed at the end for a non-US address')
    #state = USPhoneNumberField()#forms.ModelChoiceField(queryset=states_in_the_US(), required = False)

#This code is not being used
class RegistrationWizard(FormWizard):
    def done(self,request,form_list):
        form = form_list[0]
        new_user = User()
        new_user.username = form.cleaned_data['username']
        new_user.email = form.cleaned_data['email']
        new_user.set_password(form.cleaned_data['password1'])
        pw = form.cleaned_data['password1']
        
        new_user.first_name = form.cleaned_data['firstname']
        new_user.last_name = form.cleaned_data['lastname']
        new_user.save()
        
        form = form_list[1]
        profile = form.save(commit=False)
        profile.user = new_user
        profile.save()
        
        user_auth = authenticate(username=new_user.username,password=pw)
        login(request,user_auth)
        request.user.message_set.create(message='You have been successfully signed up and logged in')
        
        return redirect('homepage')

    def get_template(self, step):
        return 'registration/portal-register.html'
    
    def process_step(self,request,form,step):
        if step==0:
            try:
                if form.cleaned_data['country'] == 'US':
                    self.form_list[1] = ProfileFormUS
            except:
                pass

    
