from baseclasses import SimpleTestCase
import random, os, sys
from string import ascii_lowercase
sys.path.append(os.path.abspath('..'))
import modules


class FSUpload(SimpleTestCase):
    
    
    def test_upload(self):
        
        filename_rand = ''.join(random.choice(ascii_lowercase) for x in range(4))
        filepath_rand = os.path.join(self.basedir, filename_rand)
        
        
        self.assertEqual(self._res(':file.upload /etc/protocols %s0'  % filepath_rand), True)
        self.assertRegexpMatches(self._warn(':file.upload /etc/protocolsA %s1'  % filepath_rand), modules.file.upload.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':file.upload /etc/protocols /notwritable' ), modules.file.upload.WARN_UPLOAD_FAIL)
        self.assertEqual(self._res(':file.upload /bin/true %s2'  % filepath_rand), True)
        self.assertEqual(self._res(':file.upload /bin/true %s3 -vector file_put_contents'  % filepath_rand), True)   
        self.assertEqual(self._res(':file.upload /bin/true %s4 -vector fwrite'  % filepath_rand), True)        
        self.assertEqual(self._res(':file.upload /bin/true %s5 -chunksize 2048'  % filepath_rand), True)       
        self.assertEqual(self._res(':file.upload /bin/true %s6 -content MYTEXT'  % filepath_rand), True)   
        self.assertEqual(self._outp(':file.read %s6'  % (filepath_rand)), 'MYTEXT')     
    