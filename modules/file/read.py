from modules.file.download import Download
from tempfile import NamedTemporaryFile
from core.storedargparse import StoredArgumentParser as ArgumentParser
from core.moduleguess import ModuleGuess

class Read(Download):
    '''Read remote file'''


    def _set_args(self):
        self.argparser.add_argument('rpath')
        self.argparser.add_argument('-vector', choices = self.vectors.keys())

    def _verify_vector_execution(self):

        file = NamedTemporaryFile()
        file.close()

        self.args['lpath'] = file.name
        
        return Download._verify_vector_execution(self)
    
    def _stringify_result(self):
        return ModuleGuess._stringify_result(self)
