from core.module import Module
from core.moduleexception import ModuleException, ProbeException, ExecutionException

class ModuleGuessBase(Module):

    def _probe(self):
        
        vectors = []
        
        if 'vector' in self.args and self.args['vector']:
            selected_vector = self.vectors.get(self.args['vector'])
            if selected_vector:
                vectors = { self.args['vector'] : selected_vector }
        else:
            vectors = self.vectors
            
            
        try:
            for vector in vectors.values():
                
                try:
                    self.current_vector = vector
                    self.formatted_args = {}
                    
                    self._prepare_vector()
                    self._execute_vector()
                    self._verify_vector_execution()
                    
                except ExecutionException:
                    pass

        except ProbeException, e:
            raise ModuleException(self.name,  e.error)
        
        
    

