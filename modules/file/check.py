from core.moduleprobe import ModuleProbe
from core.moduleexception import ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser

class Check(ModuleProbe):
    '''Check remote files type, md5 and permission'''


    def _init_vectors(self):

        self.vectors = VectorList([
           Vector('shell.php', 'exists', "$f='$rpath'; if(file_exists($f) || is_readable($f) || is_writable($f) || is_file($f) || is_dir($f)) print(1); else print(0);"),
           Vector('shell.php', "isdir" , "(is_dir('$rpath') && print(1)) || print(0);"),
           Vector('shell.php', "md5" , "print(md5_file('$rpath'));"),
           Vector('shell.php',  "read", "(is_readable('$rpath') && print(1)) || print(0);"),
           Vector('shell.php', "write", "(is_writable('$rpath') && print(1))|| print(0);"),
           Vector('shell.php',  "exec", "(is_executable('$rpath') && print(1)) || print(0);"),
           Vector('shell.php', "isfile", "(is_file('$rpath') && print(1)) || print(0);")
            ])
    
    def _init_args(self):
        self.argparser.add_argument('rpath', help='Remote path')
        self.argparser.add_argument('attr', help='Attribute to check',  choices = self.vectors.get_names())

        

    def _probe(self):
        
        value = self.vectors.get(self.args['attr']).execute(self.modhandler, self.args)
        if value == '1':
            self._result = True
        elif value == '0':
            self._result = False
        elif self.args['attr'] == 'md5' and value:
            self._result = value
        else:
             raise ProbeException(self.name, "Incorrect returned value: '%s'" % (value))
            