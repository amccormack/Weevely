from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
from ast import literal_eval
from core.prettytable import PrettyTable
import os


class Enum(ModuleProbe):
    '''Check remote files type, md5 and permission'''


    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('lpath', help='Local wordlist path')
    argparser.add_argument('-printall', help='Print also when not found', action='store_true')
    argparser.add_argument('-paths', help=SUPPRESS, type=literal_eval, default=[])

    support_vectors = VectorList([
       Vector('shell.php', 'getperms', "$f='$rpath'; if(file_exists($f)) { print('e'); if(is_readable($f)) print('r'); if(is_writable($f)) print('w'); if(is_executable($f)) print('x'); }"),
    ])


    def _prepare_probe(self):
        
        self._result = {}
        
        if not self.args['paths']:
            try:
                self.args['paths']=open(os.path.expanduser(self.args['lpath']),'r').read().splitlines()
            except:
                raise ProbeException(self.name,  "Error opening path list \'%s\'" % self.args['lpath'])
                

    def _probe(self):
        
        for entry in self.args['paths']:
            
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
        