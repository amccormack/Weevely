from modules.file.download import Download
from tempfile import NamedTemporaryFile
from core.savedargparse import SavedArgumentParser as ArgumentParser
from core.moduleguess import Module

class Read(Download):
    '''Read files from target filesystem'''


    def _set_args(self):
        self.argparser.add_argument('rpath')
        self.argparser.add_argument('-vector', choices = self.vectors.keys())

    def _verify_execution(self):

        file = NamedTemporaryFile()
        file.close()

        self.args['lpath'] = file.name
        
        return Download._verify_execution(self)
    
    def _output_result(self):
        return Module._output_result(self)
