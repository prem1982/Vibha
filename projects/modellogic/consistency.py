#!/usr/bin/env python2.5

"""Identify inconsistencies in the projects database and add this
information to the ActionItem table."""

from vibha.projects.models import ActionItem, Report, Project, ProjectStatusUpdate, Volunteer
from datetime import date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from vibha.utils.dates import TODAY, newer, older, in_the_past,in_the_future, days_to, days_from

# This is the record of Lux (Kumar Parthasarathy)
PROJECTS_EXEC = Volunteer.objects.get(id=40)
OFFICE_CONTACT = 'office@vibha.org'
TEST_CONTACT = 'amenon81+projectreminders@gmail.com'
MONITORING_GROUP_CONTACT = 'vibha-mg@googlegroups.com'
SELECTION_GROUP_CONTACT = 'projects@vibha.org'
DUMMY_PROJECT_IDS = [ 46, 65 ]

class ProjectDBInconsistent(object):
    """Base class of any incosistency we are trying to find in the Projects DB."""
    reminder_classes = []
    ai_type = None

    def __init__(self, project):
        self.project = project

    def already_added(self):
        return self.project.pending_action_items().filter(ai_type=self.ai_type).count() > 0

    def add_action_item_if_needed(self):
        """Add a TODO to the ActionItem table, if needed.  Returns the
        newly added action item, or the already present action item, or
        None if there is no inconsistency in the database to add to the
        table."""
        if self.already_added():
            action_item = self.project.pending_action_items().filter(ai_type=self.ai_type)[0]
            """Check to see if this action item has been completed; Do not
            do this for annual report - Annual reports need to be
            manually marked as completed
            """
            if self.check() or self.ai_type != ActionItem.t_13_ANNUAL_REPORT_DUE:
                # Not completed
                return action_item
            else:
                # Completed. Mark as completed
                action_item.completed = True
                action_item.save()
                return None
        else:
            if self.check():
                return self.add_action_item()
            else:
                return None

    def add_action_item(self, desc, due_date=TODAY, owner=None):
        if due_date < date(2011,01,01): # Ignoring action items prior to 2011
            return None
        if owner is None:
            owner = self.project.internal_contact
        ai = ActionItem(project=self.project,
                desc=desc,
                due_date=due_date,
                owner=owner,
                ai_type=self.ai_type)
        ai.save()
        return ai

    def do_all(self):
        action_item = self.add_action_item_if_needed()
        if action_item is not None:
            for EmailClass in self.reminder_classes:
                email_object = EmailClass(action_item)
                email_object.send_email_if_needed()

class ReminderEmail:
    """The base class used to send reminder e-mails."""
    message_template = None

    def __init__(self, action_item):
        self.action_item = action_item

    def should_email_today(self):
        raise NotImplementedError("ReminderEmail.should_email_today()")

    def send_email_if_needed(self):
        """If we should send an e-mail today, go ahead and send it."""
        if not self.action_item.stop_email and self.should_email_today():
            self.send_email()

    def subject(self):
        raise NotImplementedError("ReminderEmail.subject()")

    def message_template_params(self):
        return { 'action_item': self.action_item,
                 'project':     self.action_item.project,
               }

    def message(self):
        return render_to_string(self.message_template, self.message_template_params())

    def recipients(self):
        return [ self.action_item.owner.contact.email, TEST_CONTACT ]

    def send_email(self):
        sender = 'Vibha projects <projects@vibha.org>'
        send_mail(self.subject(),
                  self.message(),
                  sender,
                  self.recipients(),
                  fail_silently=False)
                  

class DailyReminder(ReminderEmail):
    """This e-mail should be sent every day."""

    def should_email_today(self):
        return True

class MondayReminder(ReminderEmail):
    """Send an e-mail on Mondays."""

    def should_email_today(self):
        return (TODAY.isoweekday() == 1)

class WeeklyReminder(ReminderEmail):
    """Send an e-mail weekly on Mondays."""

    def should_email_today(self):
        return (TODAY.isoweekday() == 1)

class AlternateWeekReminder(ReminderEmail):
    """Send an e-mail every odd week on Mondays."""

    def should_email_today(self):
        return (TODAY.isoweekday() == 1 and TODAY.isocalendar()[1] % 2 == 1)

class ProjectHasNoStatus(ProjectDBInconsistent):
    ai_type = ActionItem.t_00_PROJECT_HAS_NO_STATUS

    def check(self):
        return (self.project.status() is None)

    def add_action_item(self):
        desc = u'Project has no entry added to the ProjectStatusUpdate table'
        return super(ProjectHasNoStatus, self).add_action_item(desc=desc, owner=PROJECTS_EXEC)

    class ProjectHasNoStatusReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-has-no-status.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s) does not have a project status update' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectHasNoStatusReminder ]


class ProjectHasNoLead(ProjectDBInconsistent):
    ai_type = ActionItem.t_01_PROJECT_HAS_NO_LEAD

    def check(self):
        return ((self.project.status_int() == ProjectStatusUpdate.y_01_LEAD_ASSIGNED) and
                (self.project.internal_contact is None))

    def add_action_item(self):
        desc = u'Project has no lead assigned to it'
        return super(ProjectHasNoLead, self).add_action_item(desc=desc, owner=PROJECTS_EXEC)

    class ProjectHasNoLeadReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-has-no-lead.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s) does not have a lead' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectHasNoLeadReminder ]

class ProjectIdleForLong(ProjectDBInconsistent):
    """Has the project been in a state of a limbo for a long time?
    This is a state such as project has no lead assigned, project has is
    yet to be approved by an action center, project is waiting to be
    approved by the national team, etc."""

    ai_type = ActionItem.t_02_PROJECT_PROCESS_IDLE_FOR_LONG

    def check(self):
        status = self.project.status()
        return ((status is not None) and
                (status.status in [ ProjectStatusUpdate.y_00_RECEIVED_PROPOSAL,
                            ProjectStatusUpdate.y_01_LEAD_ASSIGNED,
                            ProjectStatusUpdate.y_02_AC_APPROVED,
                            ProjectStatusUpdate.y_03_NATIONAL_TEAM_APPROVED, ]) and
                (days_from(status.date) >= 30))

    def add_action_item(self):
        desc = u'Project process has been idle for a while now. Please do the needful.'
        if self.project.internal_contact is not None:
            owner = self.project.internal_contact
        else:
            owner = PROJECTS_EXEC
        return super(ProjectIdleForLong, self).add_action_item(desc=desc, owner=owner)

    class ProjectIdleForLongReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-idle-for-long.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s) process has been idle for long' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectIdleForLongReminder ]

class RejectedProjectNeedsRejectionLetter(ProjectDBInconsistent):
    ai_type = ActionItem.t_03_REJECTED_PROJECT_NEEDS_REJECTION_LETTER

    def check(self):
        status = self.project.status()
        if (status is not None) and (status.status == ProjectStatusUpdate.y_05_REJECTED):
            return ((status.reject_reason is None) or
                    (status.report is None) or
                    (status.report.report_type != Report.x14_REJECT_DESCRIPTION))
        else:
            return False

    def add_action_item(self):
        desc = u'Rejected project does not rejection letter or rejection reason.'
        return super(RejectedProjectNeedsRejectionLetter, self).add_action_item(desc)

    class RejectedProjectNeedsRejectionLetterReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/rejected-project-needs-rejection-letter.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): rejection reason or document unavailable' % (
                    unicode(project), project.id3())

    reminder_classes = [ RejectedProjectNeedsRejectionLetterReminder ]

class ProjectWaitingRenewal(ProjectDBInconsistent):
    """Check to see if the project is close to its funding
    end date"""
    ai_type = ActionItem.t_04_PROJECT_AWAITS_RENEWAL

    def check(self):
        if self.project.status_int() == ProjectStatusUpdate.y_04_BOARD_APPROVED:
            funding = self.project.latest_funding()
            return (funding is not None) and (days_to(funding.end_date) <= 30)
        else:
            return False

    def add_action_item(self):
        desc = u'Project awaits renewal. Funding period ends: %s' % self.project.latest_funding().end_date
        return super(ProjectWaitingRenewal, self).add_action_item(desc,self.project.latest_funding().end_date)

    class ProjectWaitingRenewalReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-waiting-renewal-strong.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s) renewal imminent' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectWaitingRenewalReminder ]

class ProjectWaitingRenewalGentle(ProjectDBInconsistent):
    """Check to see if the project is close to its funding
    end date. This is a more gentle reminder"""
    ai_type = ActionItem.t_12_PROJECT_AWAITS_RENEWAL_GENTLE

    def check(self):
        if self.project.status_int() == ProjectStatusUpdate.y_04_BOARD_APPROVED:
            funding = self.project.latest_funding()
            if funding is not None:
                days_to_funding_end_date = days_to(funding.end_date)
                return (days_to_funding_end_date < 30)# and (days_to_funding_end_date <= 60)
            else:
                return False
        else:
            return False

    def add_action_item(self):
        desc = u'Project awaits renewal. Funding period ends: %s' % self.project.latest_funding().end_date
        return super(ProjectWaitingRenewalGentle, self).add_action_item(desc, self.project.latest_funding().end_date)

    class ProjectWaitingRenewalGentleReminder(AlternateWeekReminder):
        message_template = 'projects/reminder-emails/project-waiting-renewal-gentle.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s) renewal imminent' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectWaitingRenewalGentleReminder ]

class ProjectDoesNotHaveBoardMeetingMinutes(ProjectDBInconsistent):
    STARTING_DATE = date(2008, 1, 1)
    ai_type = ActionItem.t_05_PROJECT_DOES_NOT_HAVE_BOARD_MINUTES

    def check(self):
        approval_count = self.project.projectstatusupdate_set.filter(status=ProjectStatusUpdate.y_04_BOARD_APPROVED, date__gte=self.STARTING_DATE).count()
        minutes_count = self.project.report_set.filter(report_type=Report.x15_BOARD_DECISION_MINUTES, report_date__gte=self.STARTING_DATE).count()
        return (approval_count != minutes_count)

    def add_action_item(self):
        desc = u'Project needs board minutes'
        return super(ProjectDoesNotHaveBoardMeetingMinutes, self).add_action_item(desc)

    class ProjectDoesNotHaveBoardMeetingMinutesReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-does-not-have-board-meeting-minutes.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): no board meeting minutes available' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectDoesNotHaveBoardMeetingMinutesReminder ]

class ProjectVisitDidNotHappen(ProjectDBInconsistent):
    """Check to see if a scheduled project visit did not
    take place."""
    ai_type = ActionItem.t_06_PROJECT_VISIT_DID_NOT_HAPPEN
    visit_scheduled_date = None

    def check(self):
        for visit in self.project.projectvisit_set.all():
            if in_the_past(visit.scheduled_date):
                if (visit.visit_date is None) or (visit.report is None):
                    self.visit_scheduled_date = visit.scheduled_date
                    return True
        return False

    def add_action_item(self):
        desc = u'Project visit has not happened. Visit was scheduled for %s' % (
                self.visit_scheduled_date)
        return super(ProjectVisitDidNotHappen, self).add_action_item(desc,self.visit_scheduled_date)

    class ProjectVisitDidNotHappenReminder(DailyReminder):
        message_template = 'projects/reminder-emails/project-visit-did-not-happen.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): project visit did not happen' % (
                    unicode(project), project.id3())

        def recipients(self):
            return [ self.action_item.owner.contact.email,
                    MONITORING_GROUP_CONTACT,
                    SELECTION_GROUP_CONTACT
                    ]

    reminder_classes = [ ProjectVisitDidNotHappenReminder ]

class ProjectVisitComingUp(ProjectDBInconsistent):
    """Reminder that a project visit is coming up"""
    ai_type = ActionItem.t_11_PROJECT_VISIT_COMING_UP
    visit_scheduled_date = None

    def check(self):
        for visit in self.project.projectvisit_set.all():
            days_to_visit = days_to(visit.scheduled_date)
            if days_to_visit < 30 and days_to_visit > -1:
                    self.visit_scheduled_date = visit.scheduled_date
                    return True
        return False

    def add_action_item(self):
        desc = u'Project visit is coming up. Visit is scheduled for %s' % (
                self.visit_scheduled_date)
        return super(ProjectVisitComingUp, self).add_action_item(desc,self.visit_scheduled_date)

    class ProjectVisitComingUp(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-visit-coming-up.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): project visit is coming up' % (
                    unicode(project), project.id3())

        def recipients(self):
            return [ self.action_item.owner.contact.email,
                    MONITORING_GROUP_CONTACT,
                    SELECTION_GROUP_CONTACT
                    ]

    reminder_classes = [ ProjectVisitComingUp ]

class SelectionTemplateNotPresent(ProjectDBInconsistent):
    ai_type = ActionItem.t_07_SELECTION_TEMPLATE_NOT_PRESENT

    def check(self):
        for psu in self.project.projectstatusupdate_set.all():
            if (psu.status in [ ProjectStatusUpdate.y_02_AC_APPROVED, ProjectStatusUpdate.y_03_NATIONAL_TEAM_APPROVED ]):
                if (psu.report is None) or (psu.report.report_type != Report.x12_PROJECT_SELECTION_TEMPLATE):
                    return True
        return False

    def add_action_item(self):
        desc = u'Project lacks selection template'
        return super(SelectionTemplateNotPresent, self).add_action_item(desc)

    class SelectionTemplateNotPresentReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/selection-template-not-present.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): selection template unavailable' % (
                    unicode(project), project.id3())

    reminder_classes = [ SelectionTemplateNotPresentReminder ]

class NationalTeamApprovedButNeedsInfo(ProjectDBInconsistent):
    """NATIONAL_TEAM_APPROVED should have NTT and no pending action items."""
    ai_type = ActionItem.t_08_NATIONAL_TEAM_APPROVED_BUT_NEEDS_INFO

    def check(self):
        status = self.project.status()
        if (status is not None) and (status.status == ProjectStatusUpdate.y_03_NATIONAL_TEAM_APPROVED):
            ntt_count = self.project.report_set.filter(report_type=Report.x13_NTT, report_date__gte=status.date).count()
            return (ntt_count != 1) or (self.project.pending_action_items().count() > 0)
        else:
            return False

    def add_action_item(self):
        desc = u'Project approved by national team, but, either lacks NTT, or has pending action items.'
        return super(NationalTeamApprovedButNeedsInfo, self).add_action_item(desc)

    class NationalTeamApprovedButNeedsInfoReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/national-team-approved-but-needs-info.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): one or more action items and/or NTT pending' % (
                    unicode(project), project.id3())

    reminder_classes = [ NationalTeamApprovedButNeedsInfoReminder ]

class NeedsHalfYearlyReport(ProjectDBInconsistent):
    """Approved project does not have half-yearly report."""
    ai_type = ActionItem.t_09_NEEDS_HALF_YEARLY_REPORT

    def check(self):
        self.status = self.project.status()
        if ((self.status is not None) and
                (self.status.status == ProjectStatusUpdate.y_04_BOARD_APPROVED) and
                days_from(self.status.date) > 150):
            funding_date = self.project.latest_funding().end_date

            report_count = self.project.report_set.filter(report_type=Report.x11_HALF_YEARLY_REPORT).filter(report_date__gt=self.status.date).count()
            return (report_count != 1)
        else:
            return False

    def add_action_item(self):
        desc = u'Project lacks half-yearly report.'
        return super(NeedsHalfYearlyReport, self).add_action_item(desc,self.status.date+timedelta(days=180))

    class NeedsHalfYearlyReportReminder(AlternateWeekReminder):
        message_template = 'projects/reminder-emails/needs-half-yearly-report.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): half yearly report needed' % (
                    unicode(project), project.id3())

    reminder_classes = [ NeedsHalfYearlyReportReminder ]


class AnnualReportDue(ProjectDBInconsistent):
    """An annual report is due for this project"""
    ai_type = ActionItem.t_13_ANNUAL_REPORT_DUE

    def check(self):
        self.status = self.project.status()
        if ((self.status is not None) and
                (self.status.status == ProjectStatusUpdate.y_04_BOARD_APPROVED) and
                days_from(self.status.date) > 360):
            funding_date = self.project.latest_funding().end_date

            report_count = self.project.report_set.filter(report_type=Report.x06_ANNUAL_REPORT).filter(report_date__gt=self.status.date).count()
            return (report_count != 1)
        else:
            return False

    def add_action_item(self):
        desc = u'Project annual report is due. Funding period ends: %s' % self.project.latest_funding().end_date
        return super(AnnualReportDue, self).add_action_item(desc, self.status.date+timedelta(days=365))

    class AnnualReportDueReminder(AlternateWeekReminder):
        message_template = 'projects/reminder-emails/annual-report-due-strong.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): Annual report due' % (
                    unicode(project), project.id3())

        def recipients(self):
            return [ self.action_item.owner.contact.email,
                    OFFICE_CONTACT,
                    TEST_CONTACT
                    ]

    reminder_classes = [ AnnualReportDueReminder ]

class AnnualReportDueGentle(ProjectDBInconsistent):
    """An annual report is due for this project"""
    ai_type = ActionItem.t_14_ANNUAL_REPORT_DUE_GENTLE

    def check(self):
        self.status = self.project.status()
        if ((self.status is not None) and
            (self.status.status == ProjectStatusUpdate.y_04_BOARD_APPROVED) and
            (days_from(self.status.date) >= 300) and days_from(self.status.date) < 330):
            funding_date = self.project.latest_funding().end_date
            
            report_count = self.project.report_set.filter(report_type=Report.x06_ANNUAL_REPORT, report_date__gte=self.status.date+timedelta(days=300)).count()
            return (report_count != 1)
        else:
            return False

    def add_action_item(self):
        desc = u'Project annual report is due. Funding period ends %s' % self.project.latest_funding().end_date
        return super(AnnualReportDueGentle, self).add_action_item(desc,self.status.date+timedelta(days=365))

    class AnnualReportDueGentleReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/annual-report-due-gentle.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): Annual report due' % (
                    unicode(project), project.id3())

        def recipients(self):
            return [ self.action_item.owner.contact.email,
                    OFFICE_CONTACT,
                    TEST_CONTACT
                    ]

    reminder_classes = [ AnnualReportDueGentleReminder ]


class ProjectUndecidedForLong(ProjectDBInconsistent):
    """Project is neither approved by the board, nor rejected, and it is 2
    months, since the proposal was first received."""
    ai_type = ActionItem.t_10_PROJECT_UNDECIDED_FOR_LONG

    def check(self):
        try:
            proposal = self.project.projectstatusupdate_set.filter(status=ProjectStatusUpdate.y_00_RECEIVED_PROPOSAL).latest(field_name='date')
        except ProjectStatusUpdate.DoesNotExist:
            return False
        if (days_from(proposal.date) >= 60):
            status = self.project.status_int()
            return (status != ProjectStatusUpdate.y_04_BOARD_APPROVED) and (status != ProjectStatusUpdate.y_05_REJECTED)
        else:
            return False

    def add_action_item(self):
        desc = u'Project undecided for a long time.'
        return super(ProjectUndecidedForLong, self).add_action_item(desc)

    class ProjectUndecidedForLongReminder(WeeklyReminder):
        message_template = 'projects/reminder-emails/project-undecided-for-long.txt'

        def subject(self):
            project = self.action_item.project
            return u'Project %s (id: %s): disposition one way or the other needed' % (
                    unicode(project), project.id3())

    reminder_classes = [ ProjectUndecidedForLongReminder ]


if __name__ == '__main__':
    for p in Project.objects.all():
        if p.id not in DUMMY_PROJECT_IDS:
            #ProjectHasNoStatus(p).do_all()
            #ProjectHasNoLead(p).do_all()
            #ProjectIdleForLong(p).do_all()
            #ProjectDoesNotHaveBoardMeetingMinutes(p).do_all()
            #RejectedProjectNeedsRejectionLetter(p).do_all()
            #ProjectWaitingRenewal(p).do_all()
            ProjectWaitingRenewalGentle(p).do_all()
            #SelectionTemplateNotPresent(p).do_all()
            AnnualReportDue(p).do_all()
            #AnnualReportDueGentle(p).do_all() No longer needed
            #ProjectVisitDidNotHappen(p).do_all()
            #ProjectVisitComingUp(p).do_all()
            NeedsHalfYearlyReport(p).do_all()

