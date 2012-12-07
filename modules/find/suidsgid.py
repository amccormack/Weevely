from core.moduleprobeall import ModuleProbe
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser


class Suidsgid(ModuleProbe):
    '''Find files with superuser flags'''
    def _init_vectors(self):
        self.vectors = VectorList([
           Vector('shell.sh', "find" , "find $rpath $perm 2>/dev/null")
        ])
    
    
    def _init_args(self):
        self.argparser.add_argument('rpath', help='Remote starting path')
        self.argparser.add_argument('-suid', help='Find only suid', action='store_true')
        self.argparser.add_argument('-sgid', help='Find only sgid', action='store_true')
        
    
    def _probe(self):
        
        if self.args['suid']:
            self.args['perm'] = '-perm -04000'
        elif self.args['sgid']:
            self.args['perm'] = '-perm -02000'
        else:
            self.args['perm'] = '-perm -04000 -o -perm -02000'
            
        result = self.vectors.get('find').execute(self.modhandler, self.args)
        if result:
            self._result = result
            