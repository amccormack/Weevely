'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleexception import ModuleException
from core.configs import Configs, dirpath, rcfilepath
from core.vector import Vector
import os, re, shlex, readline, atexit

module_trigger = ':'
help_string = ':help'
set_string = ':set'
load_string = ':load'
gen_string = ':generator'


class Terminal:

    def __init__( self, modhandler):

        self.modhandler = modhandler

        self.configs = Configs()
        self.__load_rcfile(dirpath + rcfilepath, default_rcfile=True)
        self.__init_completion()
        
        
        
    def loop(self):

        username, hostname = self.__env_init()
        self.__cwd_handler()
        
        while self.modhandler.interpreter:

            prompt = '{user}@{host}:{path} {prompt} '.format(
                                                             user=username, 
                                                             host=hostname, 
                                                             path=self.modhandler.load('shell.php').stored_args['path'], 
                                                             prompt = 'PHP>' if (self.modhandler.interpreter == 'shell.php') else '$' )

            try:
                cmd = shlex.split(raw_input( prompt ).strip())
            except ValueError:
                continue
            if not cmd:
                continue

            self.run_cmd_line(cmd)


    def __tprint(self, msg):
        self.modhandler._last_warns += msg + os.linesep
        print msg,
        

    def run_cmd_line(self, command, clear_last_output = True):

        if clear_last_output:
            self._last_output = ''
            self.modhandler._last_warns = ''
            self._last_result = None
        
        try:
    
            ## Help call
            if command[0] == help_string:
                if len(command) == 2:
                    help_output = '%s\nStored arguments:\n  %s\n\n' % (self.modhandler.load(command[1]).argparser.format_help(), self.modhandler.load(command[1]).get_stored_args_str())
                    self.__tprint(help_output)
                else:
                    pass
                    # PRINT SUMMARY
    
            ## Set call if ":set module" or ":set module param value"
            elif command[0] == set_string and len(command) > 1: 
                    self.modhandler.load(command[1]).save_args(command[2:])
                    self.__tprint(self.modhandler.load(command[1]).get_stored_args_str())

            ## Load call
            elif command[0] == load_string and len(command) == 2:
                self.__load_rcfile(command[1])

            elif command[0] == 'cd':
                self.__cwd_handler(command)
                
            else:
                    
                ## Module call
                if command[0][0] == module_trigger:
                    interpreter = command[0][1:]
                    cmd = command[1:]
                ## Raw command call. Command is re-joined to be considered as single command
                else:
                    # If interpreter is not set yet, try to probe automatically best one
                    if not self.modhandler.interpreter:
                        self.__guess_best_interpreter()
                    
                    interpreter = self.modhandler.interpreter
                    cmd = [ ' '.join(command) ] 
                
                res, out = self.modhandler.load(interpreter).run(cmd)
                if out != '': self._last_output += out
                if res != None: self._last_result = res
                
        except KeyboardInterrupt:
            self.__tprint('[!] Stopped execution')
        except ModuleException, e:
            self.__tprint('[!] [%s] Error: %s%s' % (e.module, e.error, os.linesep))
        
        if self._last_output:
            print self._last_output
        

    def __guess_best_interpreter(self):
        if Vector('shell.sh', "" , ['-just-probe', 'sh']).execute(self.modhandler):
            self.modhandler.interpreter = 'shell.sh'
        elif Vector('shell.php', "" , ['-just-probe', 'php']).execute(self.modhandler):
            self.modhandler.interpreter = 'shell.php'
        else:
            raise Exception('A InitException should be raised here')
        

    def __load_rcfile(self, path, default_rcfile=False):

        path = os.path.expanduser(path)

        if default_rcfile:
            
            if not os.path.exists(path):

                try:
                    rcfile = open(path, 'w').close()
                except Exception, e:
                    raise ModuleException("Creation '%s' rc file failed%s" % (path, os.linesep))
                else:
                    return []

        for cmd in self.configs.read_rc(path):

            cmd       = cmd.strip()

            if cmd:
                self.__tprint('[RC exec] %s%s' % (cmd, os.linesep))

                self.run_cmd_line(shlex.split(cmd), clear_last_output=False)

    def __cwd_handler (self, cmd = None):

        if cmd == None or len(cmd) ==1:
            cwd_new = Vector('system.info', '', 'basedir').execute(self.modhandler)
        elif len(cmd) == 2:
            cwd_new = Vector('shell.php', '', 'chdir("$path") && print(getcwd());').execute(self.modhandler, { 'path' : cmd[1] })
            if not cwd_new:
                self.__tprint("[!] Folder '%s' change failed, no such file or directory or permission denied" % cmd[1])                
            
        self.modhandler.load('shell.php').stored_args['path'] = cwd_new
        

    def __env_init(self):
        
        print "[+] Starting terminal, shell probe may take a while"
        
        # At terminal start, try to probe automatically best interpreter
        self.__guess_best_interpreter()
        
        username =  Vector('system.info', "" , "whoami").execute(self.modhandler)
        hostname =  Vector('system.info', "" , "hostname").execute(self.modhandler)
        
        if Vector('system.info', "" , "safe_mode").execute(self.modhandler) == '1':
            self.__tprint('[!] PHP Safe mode enabled')
            
        
        return username, hostname


    def __init_completion(self):

            self.matching_words =  [':%s' % m for m in self.modhandler.modules_classes.keys()] + [help_string, load_string, set_string]
        
            try:
                readline.set_history_length(100)
                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind( 'tab: complete' )
                readline.set_completer( self.__complete )
                readline.read_history_file( self.configs.historyfile )

            except IOError:
                pass
            atexit.register( readline.write_history_file, self.configs.historyfile )



    def __complete(self, text, state):
        """Generic readline completion entry point."""

        try:
            buffer = readline.get_line_buffer()
            line = readline.get_line_buffer().split()

            if ' ' in buffer:
                return []

            # show all commandspath
            if not line:
                all_cmnds = [c + ' ' for c in self.matching_words]
                if len(all_cmnds) > state:
                    return all_cmnds[state]
                else:
                    return []


            cmd = line[0].strip()

            if cmd in self.matching_words:
                return [cmd + ' '][state]

            results = [c + ' ' for c in self.matching_words if c.startswith(cmd)] + [None]
            if len(results) == 2:
                if results[state]:
                    return results[state].split()[0] + ' '
                else:
                    return []
            return results[state]

        except Exception, e:
            self.__tprint('[!] Completion error: %s' % e)
