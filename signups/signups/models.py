from django.db import models

# Create your models here.

class Contact(models.Model):

    # We have to maintain the number (index) of each location. This is
    # because the number (and not the name) is stored in the database.
    # This is probably is a poor design decision made in the past
    # (using numbers instead of names).
    a_000_ATLANTA          =   0
    a_100_AUSTIN           = 100
    a_200_BAY_AREA         = 200
    a_250_BOSTON           = 250
    a_275_CHICAGO          = 275
    a_300_DALLAS           = 300
    a_310_DENVER           = 310
    a_400_HOUSTON          = 400
    a_450_JACKSONVILLE     = 450
    a_500_LOS_ANGELES      = 500
    a_550_MILWAUKEE        = 550
    a_600_MINNESOTA        = 600
#    a_630_NEWYORK          = 630
    a_640_NEWJERSEY        = 640
    a_660_PHILADELPHIA     = 660
    a_700_SACRAMENTO       = 700
    a_800_WASHINGTON_D_C   = 800
    a_900_BANGALORE_INDIA  = 900
    a_950_CHENNAI_INDIA    = 950
    a_953_DELHI_INDIA      = 953
    a_951_HYDERABAD_INDIA  = 951
    a_952_MUMBAI_INDIA     = 952
    a_670_PUNE_INDIA       = 670
    a_998_OTHER_INDIA      = 998
    a_999_OTHER            = 999

    LOCATION_CHOICES = (
        (a_000_ATLANTA,         "Atlanta"),
        (a_100_AUSTIN,          "Austin"),
        (a_200_BAY_AREA,        "Bay Area"),
        (a_250_BOSTON,          "Boston"),
        (a_275_CHICAGO,         "Chicago"),
        (a_300_DALLAS,          "Dallas"),
        (a_310_DENVER,          "Denver"),
        (a_400_HOUSTON,         "Houston"),
        (a_450_JACKSONVILLE,    "Jacksonville"),
        (a_500_LOS_ANGELES,     "Los Angeles"),
        (a_550_MILWAUKEE,       "Milwaukee"),
        (a_600_MINNESOTA,       "Minnesota"),
 #       (a_630_NEWYORK,         "New York"),
        (a_640_NEWJERSEY,        "New Jersey"),
        (a_660_PHILADELPHIA,    "Philadelphia"),
        (a_700_SACRAMENTO,      "Sacramento"),
        (a_800_WASHINGTON_D_C,  "Washington D.C."),
        (a_900_BANGALORE_INDIA, "Bangalore-India"),
        (a_950_CHENNAI_INDIA,   "Chennai-India"),
        (a_953_DELHI_INDIA,   "Delhi-India"),
        (a_951_HYDERABAD_INDIA,   "Hyderabad-India"),
        (a_952_MUMBAI_INDIA,   "Mumbai-India"),
        (a_670_PUNE_INDIA,    	"Pune-India"),
        (a_998_OTHER_INDIA,     "Other-India"),
        (a_999_OTHER,           "Other"),
    )

    ac_email_dict = {
        a_000_ATLANTA:         "coordinator@atlanta.vibha.org, volunteer@atlanta.vibha.org",
        a_100_AUSTIN:          "coordinator@austin.vibha.org",
        a_200_BAY_AREA:        "volunteer@bayarea.vibha.org",
        a_250_BOSTON:          "coordinator@boston.vibha.org",
        a_275_CHICAGO:         "coordinator@chicago.vibha.org",
        a_300_DALLAS:          "coordinator@dallas.vibha.org",
        a_310_DENVER:          "coordinator@denver.vibha.org",
        a_400_HOUSTON:         "volunteer@houston.vibha.org",
        a_450_JACKSONVILLE:    "coordinator@jacksonville.vibha.org",
        a_500_LOS_ANGELES:     "volunteer@la.vibha.org",
        a_550_MILWAUKEE:       "coordinator@milwaukee.vibha.org, volunteer@milwaukee.vibha.org",
        a_600_MINNESOTA:       "coordinator@minnesota.vibha.org, volunteer@minnesota.vibha.org",
#        a_630_NEWYORK:         "coordinator@ny.vibha.org",
        a_640_NEWJERSEY:       "coordinator@nj.vibha.org",
        a_660_PHILADELPHIA:    "coordinator@philadelphia.vibha.org",
        a_670_PUNE_INDIA:      "coordinator@pune.vibha.org",
        a_700_SACRAMENTO:      "coordinator@sacramento.vibha.org",
        a_800_WASHINGTON_D_C:  "coordinator@dc.vibha.org, volunteer@dc.vibha.org",
        a_900_BANGALORE_INDIA: "volunteer@bangalore.vibha.org",
        a_950_CHENNAI_INDIA:   "coordinator@chennai.vibha.org",
        a_951_HYDERABAD_INDIA: "coordinator@hyderabad.vibha.org",
        a_952_MUMBAI_INDIA:    "coordinator@mumbai.vibha.org",
        a_953_DELHI_INDIA:     "coordinator@delhi.vibha.org",
        a_998_OTHER_INDIA:     "coordinator@india.vibha.org",
        a_999_OTHER:           "volunteernetwork@vibha.org",
    }

    b_00_UNDER_18, \
    b_01_UNDER_25, \
    b_02_UNDER_40, \
    b_03_OVER_40,  = range(4)

    AGE_CHOICES = (
        (b_00_UNDER_18, "Under 18"),
        (b_01_UNDER_25, "18-25"),
        (b_02_UNDER_40, "25-40"),
        (b_03_OVER_40,  "Over 40"),
    )

    c_00_IT,         \
    c_01_NON_PROFIT, \
    c_02_PRIVATE,    \
    c_03_PUBLIC,     = range(4)
    c_99_OTHER       = 99

    OCCUPATION_CHOICES = (
        (c_00_IT,         "IT"),
        (c_01_NON_PROFIT, "Non-profit organization"),
        (c_02_PRIVATE,    "Private sector"),
        (c_03_PUBLIC,     "Public sector"),
        (c_99_OTHER,      "Other"),
    )

    d_00_FRIEND,                 \
    d_01_SURFING_THE_WEB,        \
    d_02_VOLUNTEERMATCH,         \
    d_03_GUIDESTAR,              \
    d_04_ATTENDED_A_VIBHA_EVENT, \
    d_05_ADVERTISEMENT,          = range(6)
    d_99_OTHER                   = 99

    INTRO_SOURCE_CHOICES = (
        (d_00_FRIEND,                 "Friend"),
        (d_01_SURFING_THE_WEB,        "Surfing the Web"),
        (d_02_VOLUNTEERMATCH,         "VolunteerMatch"),
        (d_03_GUIDESTAR,              "Guidestar"),
        (d_04_ATTENDED_A_VIBHA_EVENT, "Attended a Vibha Event"),
        (d_05_ADVERTISEMENT,          "Advertisement"),
        (d_99_OTHER,                  "Other"),
    )

    signup_date    = models.DateTimeField("Signup date",  editable=False, auto_now=True)
    first_name     = models.CharField("First name",        max_length=100)
    last_name      = models.CharField("Last name",         max_length=100)
    email          = models.EmailField("E-mail")
    location       = models.IntegerField("Location",       choices=LOCATION_CHOICES)
    other_location = models.CharField("Other location",    max_length=100,                               blank=True, null=True)
    new_ac         = models.NullBooleanField("Start new AC?",                                               blank=True, null=True)
    phone          = models.CharField("Phone",             max_length=100,                               blank=True)
    age            = models.IntegerField("Age group",      choices=AGE_CHOICES,                         blank=True, null=True)
    occupation     = models.IntegerField("Occupation",     choices=OCCUPATION_CHOICES,                  blank=True, null=True)
    intro_source   = models.IntegerField("How did you hear about Vibha?", choices=INTRO_SOURCE_CHOICES, blank=True, null=True)
    comments       = models.TextField("Comments",         blank=True)
    # interests
    int_projects   = models.NullBooleanField("Projects",               blank=True, null=True)
    int_fundraise  = models.NullBooleanField("Fund Raising",           blank=True, null=True)
    int_volunteer  = models.NullBooleanField("Volunteer Relations",    blank=True, null=True)
    int_it         = models.NullBooleanField("IT",                     blank=True, null=True)
    int_programs   = models.NullBooleanField("Programs and products",  blank=True, null=True)
    int_marketing  = models.NullBooleanField("Marketing",              blank=True, null=True)

    def location_has_no_ac(self):
        return (self.location == self.a_998_OTHER_INDIA) or (self.location == self.a_999_OTHER)

    def interests(self):
        """The interests as a string"""
        l = []
        if self.int_projects:
            l.append("Projects")
        if self.int_fundraise:
            l.append("Fund Raising")
        if self.int_volunteer:
            l.append("Volunteer Relations")
        if self.int_it:
            l.append("IT")
        if self.int_programs:
            l.append("Programs and products")
        if self.int_marketing:
            l.append("Marketing")
        return ', '.join(l)

    def emailRecipients(self):
        """Returns a list of persons to whom the signup email should be sent"""
        l = []
        if self.email:
            l.append(self.email)
#         if self.int_projects:
#             l.append("nikhil@vibha.org")
#         if self.int_fundraise:
#             l.append("anurag@vibha.org")
#         if self.int_volunteer:
#             l.append("suchitra@vibha.org")
#         if self.int_it:
#             l.append("ravi@vibha.org")
#         if self.int_programs:
#             l.append("raja@vibha.org")
#         if self.int_marketing:
#             l.append("mathangi@vibha.org")
        try:
            ac_email = self.ac_email_dict[self.location]
            if ac_email:
                for email in ac_email.replace(' ','').split(','):
                    l.append(email)
        except KeyError:
            # Unknown location
            pass
        l.append('volunteer@vibha.org')
        return l

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

# vim:tw=150:nowrap:ts=4:sw=4:et:
