from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from ast import literal_eval
from core.prettytable import PrettyTable
import os


class Enum(ModuleProbe):
    '''Check remote files type, md5 and permission'''


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('pathfile', help='Enuemrate paths written in PATHFILE')
    argparser.add_argument('-printall', help='Print also paths not found', action='store_true')
    argparser.add_argument('-pathlist', help='Enumerate paths written as [\'/path/1\', \'/path/2\',]', type=literal_eval, default=[])

    support_vectors = VectorList([
       Vector('shell.php', 'getperms', "$f='$rpath'; if(file_exists($f)) { print('e'); if(is_readable($f)) print('r'); if(is_writable($f)) print('w'); if(is_executable($f)) print('x'); }"),
    ])


    def _prepare_probe(self):
        
        self._result = {}
        
        if not self.args['pathlist']:
            try:
                self.args['pathlist']=open(os.path.expanduser(self.args['pathfile']),'r').read().splitlines()
            except:
                raise ProbeException(self.name,  "Error opening path list \'%s\'" % self.args['pathfile'])
                

    def _probe(self):
        
        for entry in self.args['pathlist']:
            
            perms = self.support_vectors.get('getperms').execute(self.modhandler, {'rpath' : entry})
            if perms or perms == '' and self.args['printall']:
                self._result[entry] = ['', '', '', '']
                if 'e' in perms: self._result[entry][0] = 'exists'
                if 'r' in perms: self._result[entry][1] = 'readable'
                if 'w' in perms: self._result[entry][2] = 'writable'
                if 'x' in perms: self._result[entry][3] = 'executable'
                
    def _output_result(self, stringify):
        
        if self._result:
            
            table = PrettyTable(['Field', 'Exists', 'Readable', 'Writable', 'Executable'])
            table.align = 'l'
            table.header = False
            
            for entry in self._result:
                table.add_row([entry] + self._result[entry])
                
            self._output = table.get_string()   
                 
        return self._output
        