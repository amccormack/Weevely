

from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import ModuleException, ProbeException
from core.savedargparse import SavedArgumentParser as ArgumentParser


class Name(ModuleProbeAll):
    '''Find files with matching name'''


    def _set_vectors(self):
        self.vectors.add_vector('php_recursive', 'shell.php', """@swp('$rpath','$mode','$string');
function ckdir($df, $f) { return ($f!='.')&&($f!='..')&&@is_dir($df); }
function match($f, $s, $m) { return preg_match(str_replace("%%STRING%%",$s,$m),$f); }
function swp($d, $m, $s){ $h = @opendir($d);
while ($f = readdir($h)) { $df=$d.'/'.$f; if(($f!='.')&&($f!='..')&&match($f,$s,$m)) print($df."\n"); if(@ckdir($df,$f)) @swp($df, $m, $s); }
@closedir($h); }""")
        self.vectors.add_vector("find" , 'shell.sh', "find $rpath $mode \"$string\" 2>/dev/null")
    
    def _set_args(self):
        self.argparser.add_argument('string', help='String to match')
        self.argparser.add_argument('rpath', help='Remote starting path', default ='.', nargs='?')
        self.argparser.add_argument('-equal', help='Match if name is exactly equal (default: match if contains)', action='store_true', default=False)
        self.argparser.add_argument('-case', help='Case sensitive match (default: insenstive)', action='store_true', default=False)
        self.argparser.add_argument('-vector', choices = self.vectors.keys())


    def _prepare_vector(self):
        
        self.args_formats = { 'rpath' : self.args['rpath'] }
            
        if self.current_vector.name == 'find':

            if not self.args['equal']:
                self.args_formats['string'] = '*%s*' % self.args['string']
            else:
                self.args_formats['string'] = self.args['string']
            
            if not self.args['case']:
                self.args_formats['mode'] = '-iname'
            else:
                self.args_formats['mode'] = '-name'

        elif self.current_vector.name == 'php_recursive':
            
            self.args_formats['string'] = self.args['string']

            if not self.args['equal']:
                self.args_formats['mode'] = '/%%STRING%%/'
            else:
                self.args_formats['mode'] = '/^%%STRING%%$/'
                
            if not self.args['case']:
                self.args_formats['mode'] += 'i'

            
    def _output_result(self):
        
        # Listify output, to advantage other modules 
        self._output = self._result
        self._result = self._result.split('\n')
