from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from vibha.search.search_index import WHOOSH_SCHEMA

from django.conf import settings
dirname = settings.WHOOSH_INDEX
queryparser = MultifieldParser(['title', 'summary', 'content'], schema=WHOOSH_SCHEMA)


def search_whoosh(q=None):
    q=queryparser.parse(unicode(q))
    ix = index.open_dir(dirname)
    r = ix.searcher().search(q)
    return r
