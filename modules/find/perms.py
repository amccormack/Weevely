

from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import ModuleException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser


class Perms(ModuleProbeAll):
    '''Find files with write, read, execute permissions'''

    vectors = VectorList([
       Vector('shell.php', 'php_recursive', """$fdir='$rpath';$ftype='$type';$fattr='$attr';$fqty='$first';
swp($fdir, $fdir,$ftype,$fattr,$fqty); 
function ckprint($df,$t,$a) { if(cktp($df,$t)&&@ckattr($df,$a)) { print($df."\\n"); return True;}   }
function ckattr($df, $a) { $w=strstr($a,"w");$r=strstr($a,"r");$x=strstr($a,"x"); return ($a=='')||(!$w||is_writable($df))&&(!$r||is_readable($df))&&(!$x||is_executable($df)); }
function cktp($df, $t) { return ($t==''||($t=='f'&&@is_file($df))||($t=='d'&&@is_dir($df))); }
function swp($fdir, $d, $t, $a, $q){ 
if($d==$fdir && ckprint($d,$t,$a) && ($q!="")) return; 
$h=@opendir($d); while ($f = @readdir($h)) {
$df=join('/', array(trim($d, '/'), trim($f, '/')));
if(($f!='.')&&($f!='..')&&ckprint($df,$t,$a) && ($q!="")) return;
if(($f!='.')&&($f!='..')&&cktp($df,'d')){@swp($fdir, $df, $t, $a, $q);}
} closedir($h); }"""),
       Vector('shell.sh', "find" , "find $rpath $type $attr $first 2>/dev/null")
    ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath', help='Remote starting path', default ='.', nargs='?')
    argparser.add_argument('-first', help='Quit after first match', action='store_true')
    argparser.add_argument('-type', help='File type',  choices = ['f','d'])
    argparser.add_argument('-writable', help='Match writable files', action='store_true')
    argparser.add_argument('-readable', help='Matches redable files', action='store_true')
    argparser.add_argument('-executable', help='Matches executable files', action='store_true')
    argparser.add_argument('-vector', choices = vectors.get_names())

    def _prepare_vector(self):
        
        self.args_formats = { 'rpath' : self.args['rpath'] }
        
        if self.current_vector.name == 'find':
            
            # Set first
            self.args_formats['first'] = '-print -quit' if self.args['first'] else ''
            
            # Set type
            type = self.args['type'] if self.args['type'] else ''
            if type:
                type = '-type %s' % type
            self.args_formats['type'] = type
                    
            # Set attr
            self.args_formats['attr'] = '-writable' if self.args['writable'] else ''
            self.args_formats['attr'] += ' -readable' if self.args['readable'] else ''
            self.args_formats['attr'] += ' -executable' if self.args['executable'] else ''

        else:
            # Vector.name = php_find
            # Set first
            self.args_formats['first'] = '1' if self.args['first'] else ''
            
            # Set type
            self.args_formats['type']  = self.args['type'] if self.args['type'] else ''
            
            # Set attr
            self.args_formats['attr'] = 'w' if self.args['writable'] else ''
            self.args_formats['attr'] += 'r' if self.args['readable'] else ''
            self.args_formats['attr'] += 'x' if self.args['executable'] else ''
            
    def _verify_probe(self):
        
        # Listify output, to advantage other modules 
        self._output = self._output.split('\n')
