import os
from django.conf import settings
from whoosh import store, fields, index
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT
from vibha.projects.models import Project

WHOOSH_SCHEMA = fields.Schema(title=fields.TEXT(stored=True),
                              content=fields.TEXT(stored = True),
                              summary=fields.TEXT(stored=True),
                              pk = fields.ID(stored=True, unique=True),
                              )

def create_index(sender=None, **kwargs):
    #ipdb.set_trace()
    if not os.path.exists(settings.WHOOSH_INDEX):
        os.mkdir(settings.WHOOSH_INDEX)
    ix = index.create_in(settings.WHOOSH_INDEX, schema=WHOOSH_SCHEMA)
    ix.commit()


#This is called when any fields in this table are changed
def update_index_for_project(sender, instance, created, **kwargs):
    storage = FileStorage(settings.WHOOSH_INDEX)
    ix = index.create_in(settings.WHOOSH_INDEX, schema=WHOOSH_SCHEMA)
    writer = ix.writer()
    if created:
        writer.add_document(title=unicode(instance.name), content=instance.desc,
                            summary=instance.summary, pk = unicode(instance.pk))
        writer.commit()
    else:
        writer.update_document(title=unicode(instance.name), content=instance.desc,
                            summary=instance.summary, pk = unicode(instance.pk))
        writer.commit()

