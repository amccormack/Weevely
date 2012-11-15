from modules.file.download import Download
from tempfile import NamedTemporaryFile
from core.savedargparse import SavedArgumentParser as ArgumentParser
from core.moduleprobeall import ModuleProbe

class Read(Download):
    '''Read files from target filesystem
:file.read <remote path> 
    '''

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath')
    argparser.add_argument('-vector', choices = Download.vectors.get_names())

    def _verify_execution(self):

        file = NamedTemporaryFile()
        file.close()

        self.args['lpath'] = file.name
        
        return Download._verify_execution(self)
    
    def _output_result(self):
        return ModuleProbe._output_result(self)
