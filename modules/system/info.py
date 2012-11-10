'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser

import argparse

classname = 'Info'

class Info(ModuleProbe):
    """Collect system informations
    :system.info <info>
    """


    vectors = VectorList([
        Vector('shell.php', 'document_root', "@print($_SERVER['DOCUMENT_ROOT']);"),
        Vector('shell.php', 'whoami', "@print(get_current_user());"),
        Vector('shell.php', 'hostname', "@print(gethostname());"),
        Vector('shell.php', 'basedir', "@print(getcwd());"),
        Vector('shell.php', 'safe_mode', "(ini_get('safe_mode') && print(1)) || print(0);"),
        Vector('shell.php', 'script', "@print($_SERVER['SCRIPT_NAME']);"),
        Vector('shell.php', 'uname', "@print(php_uname());"),
        Vector('shell.php', 'os', "@print(PHP_OS);"),
        Vector('shell.php', 'client_ip', "@print($_SERVER['REMOTE_ADDR']);"),
        Vector('shell.php', 'max_execution_time', '@print(ini_get("max_execution_time"));'),
        Vector('shell.php', 'php_self', '@print($_SERVER["PHP_SELF"]);'),
        Vector('shell.php', 'document_root', '@print($_SERVER["DOCUMENT_ROOT"]);'),
        Vector('shell.php', 'dir_sep', '@print(DIRECTORY_SEPARATOR);')
        ])
    
    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('info', help='Information',  choices = vectors.get_names() + ['all'], default='all', nargs='?')



    def _probe(self):
        
        if self.args['info'] != 'all':
            self._result = self.vectors.get(self.args['info']).execute(self.modhandler)
        else:
            
            self._result = {}

            for vect in self.vectors:
                self._result[vect.name] = vect.execute(self.modhandler)
                
                    
        