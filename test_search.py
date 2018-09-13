# ========================================================
#  test_search.py: whoosh search functionality
#  requires atleast python 2.5
# ========================================================
from django.core.management import setup_environ
import settings
setup_environ(settings)

import os, sys
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser



from vibha.search.search_index import WHOOSH_SCHEMA



SEARCH_STR = unicode( sys.argv[1] )

ix = index.open_dir(settings.WHOOSH_INDEX)
queryparser = MultifieldParser(['title', 'content'], schema=WHOOSH_SCHEMA)
q = queryparser.parse(SEARCH_STR)
searcher = ix.searcher()
results = searcher.search(q)
listingCount = len(results)


if listingCount > 0:

    for item in results:
        print item
            
