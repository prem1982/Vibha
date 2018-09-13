from django.db.models import signals

from search_index import Project, create_index, update_index_for_project

signals.post_syncdb.connect(create_index)
signals.post_save.connect(update_index_for_project, sender=Project)