'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.savedargparse import SavedArgumentParser as ArgumentParser
from core.vector import VectorsDict

import argparse

from re import compile

re_distroline = compile('([^=:\n"]+(?:[0-9]\.?)*[^=:\n"\\\\]+)')

class Info(ModuleProbe):
    """Collect system informations"""

    def _set_vectors(self):
            self.support_vectors.add_vector('document_root', 'shell.php', "@print($_SERVER['DOCUMENT_ROOT']);"),
            self.support_vectors.add_vector('whoami', 'shell.php', "@print(get_current_user());"),
            self.support_vectors.add_vector('hostname', 'shell.php', "@print(gethostname());"),
            self.support_vectors.add_vector('basedir', 'shell.php', "@print(getcwd());"),
            self.support_vectors.add_vector('safe_mode', 'shell.php', "(ini_get('safe_mode') && print(1)) || print(0);"),
            self.support_vectors.add_vector('script', 'shell.php', "@print($_SERVER['SCRIPT_NAME']);"),
            self.support_vectors.add_vector('uname', 'shell.php', "@print(php_uname());"),
            self.support_vectors.add_vector('os', 'shell.php', "@print(PHP_OS);"),
            self.support_vectors.add_vector('client_ip', 'shell.php', "@print($_SERVER['REMOTE_ADDR']);"),
            self.support_vectors.add_vector('max_execution_time', 'shell.php', '@print(ini_get("max_execution_time"));'),
            self.support_vectors.add_vector('php_self', 'shell.php', '@print($_SERVER["PHP_SELF"]);')
            self.support_vectors.add_vector('dir_sep' , 'shell.php',  '@print(DIRECTORY_SEPARATOR);')
    
    
            self.release_support_vectors = VectorsDict(self.modhandler)
            self.release_support_vectors.add_vector('lsb_release' , 'shell.sh',  'lsb_release -d')
            self.release_support_vectors.add_vector('find_rel' , 'find.name',  'release /etc/ -no-recursion'.split(' '))
            self.release_support_vectors.add_vector('find_issue' , 'find.name',  'issue /etc/ -no-recursion'.split(' '))
    
    def _set_args(self):
        additional_args = ['all', 'release']
        self.argparser.add_argument('info', help='Information',  choices = self.support_vectors.keys() + additional_args, default='all', nargs='?')



    def __guess_release(self):
        
        lsb_release_output = self.release_support_vectors.get('lsb_release').execute().strip()
        if lsb_release_output: 
            rel = re_distroline.findall(lsb_release_output)
            if rel: return max(rel, key=len)
            
        release_files = self.release_support_vectors.get('find_rel').execute()
        for path in release_files:
            with open(path) as f:
                data = f.read()
                rel = re_distroline.findall(data)
                if rel: return max(rel, key=len)
            
        issue_files = self.release_support_vectors.get('find_issue').execute()
        for path in issue_files:
            with open(path) as f:
                data = f.read()
                rel = re_distroline.findall(data)
                if rel: return max(rel, key=len) 
        
        return ''

    def _probe(self):
        
        if self.args['info'] == 'release':
            self._result = self.__guess_release().strip()
        elif self.args['info'] != 'all':
            self._result = self.support_vectors.get(self.args['info']).execute()
        else:
            
            self._result = {}

            for vect in self.support_vectors.values():
                self._result[vect.name] = vect.execute()
                
            self._result['release'] = self.__guess_release()
                
                    
        