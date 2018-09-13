
# $Id: sitemap.py 172 2006-12-08 22:09:00Z suriya $

from django.contrib.sitemaps import Sitemap
from vibha.projects.models import Project

class ProjectsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.modified_date

# vim:ts=4:sw=4:et:
