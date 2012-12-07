from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from ast import literal_eval
from core.utils import join_abs_paths
import os


class Userfiles(ModuleProbe):
    '''Enumerate common users restricted files'''



    def _init_vectors(self):
        self.support_vectors = VectorList([
           Vector('file.enum', 'enum', ["asd", "-pathlist", "$pathlist"]),
           Vector('audit.etcpasswd', 'users', ["-real"]),
        ])
    
    def _init_args(self):
        self.argparser.add_argument('-auto-web', help='Enumerate common files in /home/*', action='store_true')
        self.argparser.add_argument('-auto-home', help='Enumerate common files in /home/*/public_html/', action='store_true')
        self.argparser.add_argument('-pathfile', help='Enumerate paths in PATHLIST in /home/*')
        self.argparser.add_argument('-pathlist', help='Enumerate path written as [\'path1\', \'path2\',] in /home/*', type=literal_eval, default=[])



    common_files = {

                    "home" : [ ".bashrc",
                              ".bash_history",
                              ".profile",
                              ".ssh",
                              ".ssh/authorized_keys",
                              ".ssh/known_hosts",
                              ".ssh/id_rsa",
                              ".ssh/id_rsa.pub",
                              ".mysql_history",
                              ".bash_logout",
                              ],
                    "web" : [ "public_html/",
                             "public_html/wp-config.php", # wordpress
                             "public_html/config.php",
                             "public_html/uploads",
                             "public_html/configuration.php", # joomla
                             "public_html/sites/default/settings.php", # drupal
                             "public_html/.htaccess" ]

                    }

    def _prepare_probe(self):
        
        self._result = {}
        
        if self.args['pathfile']:
            try:
                filelist=open(os.path.expanduser(self.args['pathfile']),'r').read().splitlines()
            except:
                raise ProbeException(self.name,  "Error opening path list \'%s\'" % self.args['pathfile'])
        elif self.args['pathlist']:
            filelist = self.args['pathlist']
        elif self.args['auto_home']:
            filelist = self.common_files['home']   
        elif self.args['auto_web']:
            filelist = self.common_files['web']
        else:
            filelist = self.common_files['web'] + self.common_files['home']   
             

        result = self.support_vectors.get('users').execute(self.modhandler)
        if not result:
            raise ProbeException(self.name, 'Cant extract system users')
        
        
        self.args['paths'] = []
        for u in result:
            for f in filelist:
                self.args['paths'].append('/' + join_abs_paths([result[u].home, f]) )
                

    def _probe(self):
        result = self.support_vectors.get('enum').execute(self.modhandler, {'pathlist' : str(self.args['paths']) })
        for user in result:
            if result[user] != ['', '', '', '']:
                self._result[user] = result[user]
        
            