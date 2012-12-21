

from moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.savedargparse import SavedArgumentParser as ArgumentParser, Namespace
from types import ListType, StringTypes, DictType
from core.prettytable import PrettyTable
from core.vector import VectorsDict
from os import linesep


class Module:
    '''Generic class Module to inherit'''

    # self.args: variables related to current execution
    # self.stored_args: variables related to entire module life 

    def __init__(self, modhandler):
        

        self.modhandler = modhandler

        self.name = '.'.join(self.__module__.split('.')[-2:])

        self._init_vectors()
        self._init_args()
        
        self._set_vectors()
        self._set_args()
        
        self.__init_module_variables()
        self._init_module()
        
    def _init_vectors(self):
        self.vectors = VectorsDict(self.modhandler)
        self.support_vectors = VectorsDict(self.modhandler)

    def _init_args(self):
        self.argparser = ArgumentParser(prog=':%s' % self.name, description = self.__doc__)
        
        
    def _set_vectors(self):
        pass
    
    def _set_args(self):
        pass
        

    def run(self, arglist = []):
        
        self._result = ''
        self._output = ''

        try:
            self._check_args(arglist)
            self._prepare()
            self._probe()
            self._verify()
        except ProbeException, e:
            self.mprint('[!] Error: %s' % (e.error), 2, e.module) 
        except ProbeSucceed, e:
            self._stringify_result()
        except InitException, e:
            raise
        except ModuleException, e:
            module = self.name
            if e.module:
                module = e.module
            self.mprint('[!] Error: %s' % (e.error), 2, module) 
        else:
            self._stringify_result()
            
        
        return self._result, self._output

    def mprint(self, msg, msg_class = 3, module_name = None):
        
        if not self.modhandler.verbosity or msg_class <= self.modhandler.verbosity[-1]:
            if module_name == None:
                module_str = '[%s] ' % self.name
            elif module_name == '':
                module_str = ''
            else:
                module_str = '[%s] ' % module_name
                
            print module_str + str(msg)
        
            self.modhandler._last_warns += msg + linesep
            

    def _init_module(self):
        pass
    
    def __init_module_variables(self):
        self.stored_args = {}
    
    def _check_args(self, args):

        parsed_namespace, remaining_args = self.argparser.parse_known_stored_and_new_args(args=args, stored_args_dict = self.stored_args)
        self.args = vars(parsed_namespace)
        

    def _prepare(self):
        pass
    
    def _verify(self):
        pass    

    def _probe(self):
        pass

    def _stringify_result(self):
        
        
        # Empty outputs. False is probably a good output value 
        if self._result != False and not self._result:
            self._output = ''
        # List outputs.
        elif isinstance(self._result, ListType):
            
            if len(self._result) > 0:
                
                columns_num = 1
                if isinstance(self._result[0], ListType):
                    columns_num = len(self._result[0])
                
                table = PrettyTable(['']*(columns_num))
                table.align = 'l'
                table.header = False
                
                for row in self._result:
                    if isinstance(row, ListType):
                        table.add_row(row)
                    else:
                        table.add_row([ row ])
            
                self._output = table.get_string()
                
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
        
    def format_help(self, help = True, stored_args=True,  name = True, descr=True, usage=True, padding = 0):
        
        help_output = ''

        if help:
            help_output += '%s\n' % self.argparser.format_help()
        else:
            
            if name:
                help_output += '[%s]' % self.name
                
            if descr:
                if name: help_output += ' '
                help_output += '%s\n' %self.argparser.description
            
            if usage:
                help_output += '%s\n' % self.argparser.format_usage() 
    
        stored_args_help = self.get_stored_args_str()
        if stored_args and stored_args_help:
            help_output += 'stored arguments: %s\n' % stored_args_help
            
        help_output = ' '*padding + help_output.replace('\n', '\n' + ' '*(padding)).rstrip(' ') 
            
        return help_output
        
                
    def get_stored_args_str(self):
    
        stored_args_str = ''
        for argument in [ action.dest for action in self.argparser._actions if action.dest != 'help' ]:
            value = self.stored_args[argument] if argument in self.stored_args else ''
            stored_args_str += '%s=\'%s\' ' % (argument, value)
        return stored_args_str
        
    