

from moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.storedargparse import StoredArgumentParser as ArgumentParser, Namespace
from types import ListType, StringTypes, DictType
from core.prettytable import PrettyTable
from core.vector import VectorsDict
from os import linesep
from core.modulebase import ModuleBase

class Module(ModuleBase):
    '''Generic Module class to inherit.
    
    To create new module, define MyModule class into python file "modules/group/mymodule.py". 
    Class name needs to be equal to the module file name with first letter capitalized.
    
    Following methods are called only at first module execution by Module.__init__()
        
        . Module._set_args() To declare argparse arguments [Optional]
        . Module._set_vectors() To declare vector to use during run  [Optional]
        . Module._init_module() For anything needed at module construction [Optional]
    
    Following methods are called at every run by Module.run() 
    
        . Module._prepare() Prepare vector and enviroinment for the probe [Optional]
        . Module._probe() Effective vector run. [Mandatory]
        . Module._verify() Verify if probe works [Optional]
    
    A basic Module declare at least arguments parameters in Module._set_args(), vectors 
    declaration in Module._set_vectors(), and internal probe logic in Module._probe(). Read usage
    details written in methods documentations. 
    
    Example of a basic module that download files from web into target, situated in "modules/net/webdownload.py":
    
        from core.module import Module
        from core.moduleexception import ProbeException
    
        class Webdownload(Module):
        
            def _set_args(self):
                
                # Declare accepted module parameters. Passed parameters are stored in self.args dictionary.
                
                self.argparser.add_argument('rpath', help='Remote path')
                self.argparser.add_argument('lpath', help='Local path where save file')
                
            def _set_vectors(self):
                
                # Declare vectors to execute. First one contains code to call wget using 'shell.sh' system 
                # shell interpreter module, second one calls 'file.check' existing module to verify
                # downloaded file. Template fields like '$rpath' are replaced at vector execution.
                
                self.support_vectors.add_vector(name='wget', interpreter='shell.sh', payloads = [ 'wget', '$rpath', '-O', '$lpath' ])
                self.support_vectors.add_vector(name='check_download', interpreter='file.check', payloads = [ '$rpath', 'exists' ])
                
            def _probe(self):
            
                # Start download calling 'wget' vector, formatting it with passed options in self.args dictionary.
            
                self.support_vectors.get('wget').execute(self.args)
            
            def _verify(self):
            
                # Verify downloaded file. Save vector return value in self._result and eventually raise 
                # ProbeException to stop module execution and print error message.
     
                self._result = self.support_vectors.get('check_download').execute({ 'rpath' : self.args['rpath'] })
                if self._result == False:
                    raise ProbeException(self.name, 'Downloaded file not found')
       
       
       
        
    '''

        
    def _set_vectors(self):
        """Inherit this method to add vectors in self.vectors and self.support_vectors lists, easily
        callable in _probe() function. This method is called by module constructor. 
        Example of vector declaration:
        
        > self.support_vectors.add_vector(name='vector_name', interpreter='module_name', payloads = [ 'module_param1', '$module_param2', .. ])
        
        Template fields like '$rpath' are replaced at vector execution.
        
        """
        
        pass
    
    def _set_args(self):
        """Inherit this method to set self.argparser arguments. Set new arguments following
        official python argparse documentation like. This method is called by module constructor.
        Arguments passed at module runs are stored in Module.args dictionary.
        """
        
        pass
        
    def _init_module(self):
        """Inherit this method to set eventual additional variables. Called by module constructor.
        """
    
    def _prepare(self):
        """Inherit this method to prepare vectors and enviroinment for the probe, using declared
        vectors. 
        
        This method is called at every module run. Throws ModuleException, ProbeException.
        """
        
        pass

    def _probe(self):
        """Inherit this method to execute main tasks. Vector declared before are used to call
        other modules and execute shell and php statements. This method is mandatory to execute tasks. 
        
        Example of vector selection and execution:
        
        > self.support_vectors.get('vector_name').execute({ '$module_param2' : self.args['arg2']})
        
        Vector is selected with VectorList.get(name=''), and launched by Vector.execute(templated_params={}), that
        replace template variables and run it.
        
        Results that moudule execution returns should be stored in self._result. 
        This method is called at every module run. Throws ModuleException, ProbeException, ProbeSucceed. 
        
        """
        pass

    
    def _verify(self):
        """Inherit this method to prepare vectors and enviroinment for the probe, using declared
        vectors.
        
        Results to print and return after moudule execution should be stored in self._result.
        It is called at every module run. Throws ModuleException, ProbeException, ProbeSucceed.         
        """
        pass    

