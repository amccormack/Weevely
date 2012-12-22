from core.module import Module
from core.moduleexception import ProbeException
from core.storedargparse import StoredArgumentParser as ArgumentParser

class Check(Module):
    '''Check remote files type, md5 and permission'''


    def _set_vectors(self):

        self.support_vectors.add_vector('exists', 'shell.php',  "$f='$rpath'; if(file_exists($f) || is_readable($f) || is_writable($f) || is_file($f) || is_dir($f)) print(1); else print(0);")
        self.support_vectors.add_vector("md5" ,'shell.php', "print(md5_file('$rpath'));")
        self.support_vectors.add_vector("read", 'shell.php',  "(is_readable('$rpath') && print(1)) || print(0);")
        self.support_vectors.add_vector("write", 'shell.php', "(is_writable('$rpath') && print(1))|| print(0);")
        self.support_vectors.add_vector("exec", 'shell.php', "(is_executable('$rpath') && print(1)) || print(0);")
        self.support_vectors.add_vector("isfile", 'shell.php', "(is_file('$rpath') && print(1)) || print(0);")
    
    def _set_args(self):
        self.argparser.add_argument('rpath', help='Remote path')
        self.argparser.add_argument('attr', help='Attribute to check',  choices = self.support_vectors.keys())

        

    def _probe(self):
        
        value = self.support_vectors.get(self.args['attr']).execute(self.args)
        
        if value == '1':
            self._result = True
        elif value == '0':
            self._result = False
        elif self.args['attr'] == 'md5' and value:
            self._result = value
        else:
             raise ProbeException(self.name, "Incorrect returned value: '%s'" % (value))
            