#!/usr/bin/env python2.5

from vibha.projects.models import ActionItem

ActionItem.objects.all().delete()
