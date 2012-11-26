from core.moduleprobeall import ModuleProbe
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser


class Suidsgid(ModuleProbe):
    '''Find files with superuser flags'''

    vectors = VectorList([
       Vector('shell.sh', "find" , "find $rpath $perm 2>/dev/null")
    ])
    
    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath', help='Remote starting path')
    argparser.add_argument('-suid', help='Find only suid', action='store_true')
    argparser.add_argument('-sgid', help='Find only sgid', action='store_true')
    
    
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
            