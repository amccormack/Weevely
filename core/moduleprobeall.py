from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException, ProbeException, ExecutionException, ProbeSucceed

class ModuleProbeAll(ModuleProbe):


    # self.args: variables related to current execution
    # self.args['vector'] user input vector name
    # self.stored_args: variables related to entire module life 
    # self.stored_args['vector'] saved vector name
    
    # self.current_vector effective current vector object

    def _init_module(self):
        ModuleProbe._init_module(self)
        self.current_vector = None
        
        
    def __init_vector_variables(self, vector):
        
        self.args_formats = {}
        self.current_vector = vector
        
    def _prepare_vector(self):
        pass
        
    def _execute_vector(self):
        self._result = self.current_vector.execute(self.modhandler, self.args_formats)
    
    def _verify_execution(self):
        # If self._result is set. False is probably a good return value.
        if self._result or self._result == False:
            raise ProbeSucceed(self.name,'Command succeeded')
     

    def _probe(self):
        
        
        
        vectors = []
        
        if 'vector' in self.args and self.args['vector']:
            selected_vector = self.vectors.get(self.args['vector'])
            if selected_vector:
                vectors = [ selected_vector ]
        else:
            vectors = self.vectors


        try:
            for vector in vectors:
    
                try:
                    self.__init_vector_variables(vector)
                    self._prepare_vector()
                    self._execute_vector()
                    self._verify_execution()
                    
                except ExecutionException:
                    pass
                
        except ProbeSucceed:
            # Execution succeed
            pass
        except ProbeException, e:
            raise ModuleException(self.name,  e.error)
        
        
    

