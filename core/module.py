

from moduleexception import ModuleException, ProbeException, ProbeSucceed, InitException
from core.storedargparse import StoredArgumentParser as ArgumentParser, Namespace
from types import ListType, StringTypes, DictType
from core.prettytable import PrettyTable
from core.vector import VectorsDict
from os import linesep
from core.modulebase import ModuleBase

class Module(ModuleBase):
    '''Generic Module class to inherit.
    
    Module object is a dynamically loaded Weevely extension that executes automatic
    tasks on remote target. Vector objects contains the code to run on remote target.
    
    To create a new module, define an object that inherit Module (e.g. 'class MyModule(Module)')
    into python file situated in 'modules/mygroup/mymodule.py'. Class needs the same name of the
    python file, with first capital letter.
    
    At first run (e.g. running ':mymgroup.mymodule' from terminal for the first time), module 
    constructor executes following main tasks:
        
        A) Defines module arguments (method _set_args(), inherition is recommended) 
        B) Defines module vectors (method _set_vectors(), inherition is recommended)
    
    At every call (e.g. at every ':mymgroup.mymodule' run) run() method parse passed
    arguments and execute following main tasks:
    
        1) Optionally prepares the enviroinment or formats the passed arguments to simplify vector run 
           (method _prepare(), inherition is optional)
        2) Runs vectors and saves results  (method _probe(), inherition is mandatory)
        3) Optionally verifies probe execution (method _verify(), inherition is optional)
    
    Example of a basic module that download files from web into target:

    ==================================== webdownload.py ===================================

    from core.module import Module
    from core.moduleexception import ProbeException, ProbeSucceed
    
    WARN_DOWNLOAD_FAIL = 'Downloaded failed'
    
    class Webdownload(Module):
        
        def _set_args(self):
            
            # Declare accepted module parameters. Parameters passed at run are stored in self.args dictionary.
            
            self.argparser.add_argument('url')
            self.argparser.add_argument('rpath')
    
        def _set_vectors(self):

            # Declare vectors to execute. Vector named 'wget' use module 'shell.sh', that execute
            # shells commands, to run wget. Other vector named 'check_download' use other module
            # 'file.check' included in Weevely to verify downloaded file. Payload variable fields 
            # '$path' and '$url' are replaced at vector execution with self.args values.
            
            self.support_vectors.add_vector(name='wget', interpreter='shell.sh', payloads = [ 'wget $url -O $rpath' ])
            self.support_vectors.add_vector(name='check_download', interpreter='file.check', payloads = [ '$rpath', 'exists' ])
            
        def _probe(self):
       
           # Start download calling 'wget' vector, formatting it with passed options in self.args dictionary.
           self.support_vectors.get('wget').execute(self.args)
       
        def _verify(self):
       
           # Verify downloaded file. Save vector return value in self._result and eventually raise 
           # ProbeException to stop module execution and print error message.
    
           self._result = self.support_vectors.get('check_download').execute({ 'rpath' : self.args['rpath'] })
           if self._result == False:
               raise ProbeException(self.name, WARN_DOWNLOAD_FAIL)
           

    =======================================================================================

       
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
        
        Probe results should be stored in self._result. 
        This method is called at every module run. Throws ModuleException, ProbeException, ProbeSucceed. 
        
        """
        pass

    
    def _verify(self):
        """Inherit this method to check probe result.
        
        Results to print and return after moudule execution should be stored in self._result.
        It is called at every module run. Throws ModuleException, ProbeException, ProbeSucceed.         
        """
        pass    

