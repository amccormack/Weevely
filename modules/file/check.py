from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser

class Check(ModuleProbe):
    '''Check remote files type, md5 and permission'''


    vectors = VectorList([
       Vector('shell.php', 'exists', "$f='$rpath'; if(file_exists($f) || is_readable($f) || is_writable($f) || is_file($f) || is_dir($f)) print(1); else print(2);"),
       Vector('shell.php', "isdir" , "if(is_dir('$rpath')) print(1); else print(2);"),
       Vector('shell.php', "md5" , "print(md5_file('$rpath'));"),
       Vector('shell.php',  "read", "if(is_readable('$rpath')) print(1); else print(2);"),
       Vector('shell.php', "write", "if(is_writable('$rpath')) print(1); else print(2);"),
       Vector('shell.php',  "exec", "if(is_executable('$rpath')) print(1); else print(2);"),
       Vector('shell.php', "isfile", "if(is_file('$rpath')) print(1); else print(2);")
        ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath', help='Remote path')
    argparser.add_argument('attr', help='Attribute to check',  choices = vectors.get_names())


    def _probe(self):
        
        value = self.vectors.get(self.args['attr']).execute(self.modhandler, self.args)
        if value == '1':
            self._output = True
        elif value == '2':
            self._output = False
        elif self.args['attr'] == 'md5' and value:
            self._output = value
        else:
             raise ModuleException(self.name, "Error returned value: '%s'" % (value))
            