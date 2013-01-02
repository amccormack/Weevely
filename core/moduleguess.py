from core.moduleguessbase import ModuleGuessBase
from core.moduleexception import ModuleException, ProbeException, ExecutionException, ProbeSucceed

class ModuleGuess(ModuleGuessBase):


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
        

    def _prepare_vector(self):
        self.formatted_args = self.args
        
    def _execute_vector(self):
        self._result = self.current_vector.execute(self.formatted_args)
    
    def _verify_vector_execution(self):
        # If self._result is set. False is probably a good return value.
        if self._result or self._result == False:
            raise ProbeSucceed(self.name,'Command succeeded')
     
