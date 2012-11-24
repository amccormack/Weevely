from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from external.crawler import Crawler
from ast import literal_eval
from core.prettytable import PrettyTable
import os
from modules.find.webdir import join_abs_paths

WARN_CRAWLER_EXCEPT = 'Crawler exception'
WARN_CRAWLER_NO_URLS = "No sub URLs crawled. Check URL."


class Mapwebfiles(ModuleProbe):
    '''Enumerate webroot files properties '''


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('url', help='HTTP URL where start crawling (es. http://host/path/page.html)')
    argparser.add_argument('baseurl', help='HTTP base url (es. http://host/path/)')
    argparser.add_argument('rpath', help='Remote web root corresponding to crawled path (es. /var/www/path)', type=str)
    argparser.add_argument('-deep', help='Crawl deepness', type=int, default=3)

    support_vectors = VectorList([
       Vector('file.enum', 'enum', ["asd", "-pathlist", "$pathlist"]),
    ])

    def _prepare_probe(self):
    
        url = self.args['url']    
        baseurl = self.args['baseurl']
        rpath = self.args['rpath']
        
        urls = []
    
        try:
            crawler = Crawler(url, self.args['deep'], '', '')
            crawler.crawl()
        except Exception, e:
            raise ProbeException(self.name, "%s: %s" % (ERR_CRAWLER_EXCEPT, str(e)))
        else:
            urls = set(crawler.visited_links.union(crawler.urls_seen))
            
            # If no url, or the only one is the specified one
            
            if not urls or (urls and len(urls) == 1 and list(urls)[0] == url):
                raise ProbeException(self.name, WARN_CRAWLER_NO_URLS )
        
        
            self.args['paths'] = []
            for path in urls:
                self.args['paths'].append('/' + join_abs_paths([rpath, path[len(baseurl):]]))
                


    def _probe(self):

        self._result = self.support_vectors.get('enum').execute(self.modhandler, {'pathlist' : str(self.args['paths']) })