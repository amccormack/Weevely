

from moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.savedargparse import SavedArgumentParser as ArgumentParser, Namespace
from types import ListType, StringTypes, DictType
from core.prettytable import PrettyTable
from os import linesep


class ModuleProbe:
    '''Generic class Module to inherit'''

    # self.args: variables related to current execution
    # self.stored_args: variables related to entire module life 

    def __init__(self, modhandler):
        

        self.modhandler = modhandler

        self.name = '.'.join(self.__module__.split('.')[-2:])
        
        self.__init_module_variables()
        self._init_module()
        

    def run(self, arglist = []):
        
        self._result = ''
        self._output = ''
        
        
        try:
            self._check_args(arglist)
            self._prepare_probe()
            self._probe()
            self._verify_probe()
        except ProbeException, e:
            self.mprint('[!] Error: %s' % (e.error), 2, e.module) 
        except ProbeSucceed, e:
            self._output_result()
        except InitException, e:
            raise
        except ModuleException, e:
            module = self.name
            if e.module:
                module = e.module
            self.mprint('[!] Error: %s' % (e.error), 2, module) 
        else:
            self._output_result()
            
        return self._result, self._output

    def mprint(self, str, msg_class = 3, module_name = None):
        
        if not self.modhandler.verbosity or msg_class <= self.modhandler.verbosity[-1]:
            if not module_name:
                module_name = self.name
                
            print '[%s] %s' % (module_name, str)
        
            self.modhandler._last_warns += str + linesep
            

    def _init_module(self):
        pass
    
    def __init_module_variables(self):
        self.stored_args = {}
    
    def _check_args(self, args):

        parsed_namespace, remaining_args = self.argparser.parse_known_stored_and_new_args(args=args, stored_args_dict = self.stored_args)
        self.args = vars(parsed_namespace)
        

    def _prepare_probe(self):
        pass
    
    def _verify_probe(self):
        pass    

    def _probe(self):
        pass

    def _output_result(self):
        
        
        # Empty outputs. False is probably a good output value 
        if self._result != False and not self._result:
            self._output = ''
        # List outputs.
        elif isinstance(self._result, ListType):
            self._output = '\n'.join(self._result)
        # Dict outputs are display as tables
        elif isinstance(self._result, DictType) and self._result:

            # Populate the rows
            randomitem = next(self._result.itervalues())
            if isinstance(randomitem, ListType):
                table = PrettyTable(['']*(len(randomitem)+1))
                table.align = 'l'
                table.header = False
                
                for field in self._result:
                    table.add_row([field] + self._result[field])
                
            else:
                table = PrettyTable(['']*2)
                table.align = 'l'
                table.header = False
                
                for field in self._result:
                    table.add_row([field, str(self._result[field])])
                

                
            self._output = table.get_string()
        # Else, try to stringify
        else:
            self._output = str(self._result)
        
        
    def save_args(self, args):

        for argument in args:
            if '=' in argument:
                key, value = argument.split('=')
                
                # Reset value
                if value == '':
                    value = None
                
                self.stored_args[key] = value
        
                
    def get_stored_args_str(self):
    
        stored_args_str = ''
        for argument in [ action.dest for action in self.argparser._actions if action.dest != 'help' ]:
            value = self.stored_args[argument] if argument in self.stored_args else ''
            stored_args_str += '%s=\'%s\' ' % (argument, value)
        return stored_args_str
        
    