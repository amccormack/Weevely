'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.savedargparse import SavedArgumentParser as ArgumentParser

import argparse

class Info(ModuleProbe):
    """Collect system informations
    :system.info <info>
    """

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
            self.support_vectors.add_vector('php_self', 'shell.php', '@print($_SERVER["PHP_SELF"]);'),
            self.support_vectors.add_vector('dir_sep' , 'shell.php',  '@print(DIRECTORY_SEPARATOR);')
    
    def _set_args(self):
        self.argparser.add_argument('info', help='Information',  choices = self.support_vectors.keys() + ['all'], default='all', nargs='?')


    def _probe(self):
        
        if self.args['info'] != 'all':
            self._result = self.support_vectors.get(self.args['info']).execute()
        else:
            
            self._result = {}

            for vect in self.support_vectors.values():
                self._result[vect.name] = vect.execute()
                
                    
        