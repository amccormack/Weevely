import argparse
from argparse import SUPPRESS, Namespace, ArgumentError, _UNRECOGNIZED_ARGS_ATTR, ArgumentParser, HelpFormatter
from core.moduleexception import ModuleException


class StoredArgumentParser(ArgumentParser):
    
    def __init__(self, 
        prog=None, 
        usage=None, 
        description=None, 
        epilog=None, 
        version=None, 
        parents=[], 
        formatter_class=HelpFormatter, 
        prefix_chars='-', 
        fromfile_prefix_chars=None, 
        argument_default=None, 
        conflict_handler='error', 
        add_help=False):
        ArgumentParser.__init__(self, prog=prog, usage=usage, description=description, epilog=epilog, version=version, parents=parents, formatter_class=formatter_class, prefix_chars=prefix_chars, fromfile_prefix_chars=fromfile_prefix_chars, argument_default=argument_default, conflict_handler=conflict_handler, add_help=add_help)
        
    def error(self, message):
        raise ModuleException('', '%s\n\n%s' % (message, self.format_help().rstrip()))
        
  
    def parse_known_stored_and_new_args(self, args=None, namespace=None, stored_args_dict = {}):
       
        # args replacement_value to the system args
        if args is None:
            args = _sys.argv[1:]

        self.__last_input_args = args

        # replacement_value Namespace built from parser defaults
        if namespace is None:
            namespace = Namespace()

        try:
            # add any action defaults that aren't present
            for action in self._actions:
                if action.dest is not SUPPRESS:
                        
                        replacement_value = None
                        # Check if there is a stored value and is not None
                        if action.dest in stored_args_dict and stored_args_dict[action.dest] != None:
                            # If positional, add it also to args to avoid 'too few arguments' exception on _parse_known_args
                            if action.nargs not in [None, argparse.OPTIONAL]:
                                args.append(stored_args_dict[action.dest])
                            replacement_value = self._get_values(action, [ stored_args_dict[action.dest] ])
                                
                        # Else, check if default is present
                        elif action.default is not SUPPRESS:
                            if isinstance(action.default, basestring):
                                replacement_value = self._get_values(action, [ action.default ])
                            else:
                                replacement_value = action.default
                            
                        else:
                            replacement_value = None
                        
                        setattr(namespace, action.dest, replacement_value)
    
            # add any parser defaults that aren't present
            for dest in self._defaults:
                if not hasattr(namespace, dest):
                    setattr(namespace, dest, self._defaults[dest])
    
            # parse the arguments and exit if there are any errors
            namespace, args = self._parse_known_args(args, namespace)
            
            if hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
                
            return namespace, args
        except ArgumentError, err:
            self.error(str(err))
       
       