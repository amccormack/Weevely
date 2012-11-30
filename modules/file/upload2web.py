'''
Created on 23/set/2011

@author: norby
'''
from modules.file.upload import Upload
from core.moduleexception import  ModuleException, ExecutionException, ProbeException, ProbeSucceed
from core.vector import VectorList, Vector
from core.http.cmdrequest import CmdRequest, NoDataException
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
import os
from random import choice
from string import ascii_lowercase


WARN_WEBROOT_INFO = 'Error getting web enviroinment informations'
WARN_NOT_WEBROOT_SUBFOLDER = "is not a webroot subdirectory"
WARN_NOT_FOUND = 'Path not found'
WARN_WRITABLE_DIR_NOT_FOUND = "Writable web directory not found"

class WebEnv:
    
    def __init__(self, modhandler):
        
        self.modhandler = modhandler
        self.name = 'webenv'
        
#        script_folder_path = Vector('system.info', 'basedir', 'basedir' ).execute(self.modhandler)
#        script_file_url = self.modhandler.url
#        script_folder_url = os.path.join('/', *self.modhandler.url.split('/')[:-1]) 
        
        self.base_folder_path = Vector('system.info', 'document_root', 'document_root' ).execute(self.modhandler)
        self.base_folder_url = '/'.join(self.modhandler.url.split('/')[:3])
        if not self.base_folder_path:
            raise ProbeException(self.name, WARN_WEBROOT_INFO)
        
    def folder_map(self, relative_path_folder = '.'):
        
        absolute_path =  Vector('shell.php', 'normalize', 'print(realpath("$path"));').execute(self.modhandler, { 'path' : relative_path_folder })
        
        if not absolute_path:
            raise ProbeException(self.name, WARN_NOT_FOUND)
        
        if not absolute_path.startswith(self.base_folder_path):
            raise ProbeException(self.name, '\'%s\' %s' % (absolute_path, WARN_NOT_WEBROOT_SUBFOLDER) ) 
            
        relative_to_webroot_path = absolute_path.replace(self.base_folder_path,'')
        
        url_folder = '%s/%s' % ( self.base_folder_url.rstrip('/'), relative_to_webroot_path.lstrip('/') )
        
        return absolute_path, url_folder
    
    def file_map(self, relative_path_file):
        
        relative_path_folder = '/'.join(relative_path_file.split('/')[:-1])
        filename = relative_path_file.split('/')[-1]
        
        absolute_path_folder, url_folder = self.folder_map(relative_path_folder)
    
        absolute_path_file = os.path.join(absolute_path_folder, filename)
        url_file = os.path.join(url_folder, filename)
        
        return absolute_path_file, url_file
    

class Upload2web(Upload):
    '''Upload binary/ascii file to the web root, getting the corresponding url'''


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('lpath')
    argparser.add_argument('rpath', help='Optional, upload as rpath', nargs='?')
    
    argparser.add_argument('-startpath', help='Upload in first writable subdirectory', metavar='STARTPATH', default='.')
    argparser.add_argument('-chunksize', type=int, default=1024)
    argparser.add_argument('-content', help=SUPPRESS)
    argparser.add_argument('-vector', choices = Upload.vectors.get_names())
    argparser.add_argument('-force', action='store_true')

    
    def _prepare_probe(self):

        self._load_local_file()
        
        webenv = WebEnv(self.modhandler)
        if self.args['rpath']:
            # Check if remote file is actually in web root
            self.args['rpath'], self.args['url'] = webenv.file_map(self.args['rpath'])
        else:
            
            # Extract filename
            filename = self.args['lpath'].split('/')[-1]
            
            # Check if starting folder is actually in web root
            absolute_path_folder, url_folder = webenv.folder_map(self.args['startpath'])
            
            # Start find in selected folder
            writable_subdirs = Vector('find.perms', 'find_writable_dirs', '-type d -writable $path'.split(' ')).execute(self.modhandler, {'path' : absolute_path_folder})
            
            if not writable_subdirs:
                raise ProbeException(self.name, WARN_WRITABLE_DIR_NOT_FOUND)
                
            writable_folder, writable_folder_url = webenv.folder_map(writable_subdirs[0])
                
            self.args['rpath'] = os.path.join(writable_folder, filename)
            self.args['url'] = os.path.join(writable_folder_url, filename)        
            
        
        self._check_remote_file()                

    
    def _output_result(self):
        if self._result:
            self._result = [ self.args['rpath'], self.args['url'] ]
        else:
            self._result = [ None, None ]
        
        return Upload._output_result(self)
    