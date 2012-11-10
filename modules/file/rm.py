

from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import ModuleException, ProbeSucceed, ProbeException, ExecutionException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser


class Rm(ModuleProbeAll):
    '''Remove remote files and folders'''

    vectors = VectorList([
        Vector('shell.php', 'php_rmdir', """
function rmfile($dir) {
if (is_dir("$dir")) rmdir("$dir");
else { unlink("$dir"); }
}
function exists($path) {
return (file_exists("$path") || is_link("$path"));
}
function rrmdir($recurs,$dir) {
    if($recurs=="1") {
        if (is_dir("$dir")) {
            $objects = scandir("$dir");
            foreach ($objects as $object) {
            if ($object != "." && $object != "..") {
            if (filetype($dir."/".$object) == "dir") rrmdir($recurs, $dir."/".$object); else unlink($dir."/".$object);
            }
            }
            reset($objects);
            rmdir("$dir");
        }
        else rmfile("$dir");
    }
    else rmfile("$dir");
}
$recurs="$recursive"; $path="$rpath";
if(exists("$path")) 
rrmdir("$recurs", "$path");"""),
              Vector('shell.sh', 'rm', "rm $recursive $rpath")
    ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath', help='Remote starting path')
    argparser.add_argument('-recursive', help='Remove recursively', action='store_true')
    argparser.add_argument('-vector', choices = vectors.get_names())


    def _prepare_probe(self):
        
        self.modhandler.load('file.check').run([ self.args['rpath'], 'exists' ])
        if not self.modhandler.load('file.check')._result:
            raise ProbeException(self.name, '\'%s\' no such file or directory or permission denied' % self.args['rpath'])        


    def _prepare_vector(self):
        
        self.args_formats = { 'rpath' : self.args['rpath'] }
        
        if self.current_vector.name == 'rm':
            self.args_formats['recursive'] = '-rf' if self.args['recursive'] else ''
        else:
            self.args_formats['recursive'] = '1' if self.args['recursive'] else ''
            
            
    def _verify_execution(self):
        self.modhandler.load('file.check').run([ self.args['rpath'], 'exists' ])
        self._result = self.modhandler.load('file.check')._result
        
        if not self._result:
            raise ProbeSucceed(self.name,'Command succeeded')
        else:
            raise ExecutionException(self.name, 'File \'%s\' delete fail, check permissions' % self.args['rpath'])
     
