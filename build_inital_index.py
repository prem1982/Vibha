#!/usr/bin/env python2.5

from django.core.management import setup_environ
import settings
setup_environ(settings)

from vibha.projects.models import Project
from vibha.donorportal.models import Campaign
from vibha.search.search_index import create_index, WHOOSH_SCHEMA

import os, sys
from whoosh import store, fields, index
from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT





#
# Method to create a new search index
#
def create_index_for_project():
    print 'Creating index for %s' % Project.objects.all().count()
    projects = Project.objects.filter(show_adopt_project=True)
    ix = index.create_in(settings.WHOOSH_INDEX, schema=WHOOSH_SCHEMA)
    writer = ix.writer()
    for project in projects:
        try:

            writer.add_document(title=unicode(project.name),
                                content=project.desc,
                                summary=project.summary,
                                pk = unicode(project.pk))
        except:
            pass#Dont do anything, as a single error mustnot stop index creation.
    writer.commit()
    print "Search index in %s rebuilt." % settings.WHOOSH_INDEX
    
def create_index_for_campaign():
    campaigns = Campaign.objects.all()
    ix = index.create_in(settings.WHOOSH_INDEX, schema=WHOOSH_SCHEMA)
    writer = ix.writer()
    for campaign in campaigns:
        try:
            writer.add_document(title=unicode(campaign), content=campaign.description,
                                pk = unicode(campaign.pk))
        except:
            pass#Dont do anything, as a single error mustnot stop index creation.
    writer.commit()



if __name__ == '__main__':
    create_index()
    create_index_for_project()
    #create_index_for_campaign()


