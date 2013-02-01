from baseclasses import FolderFileFSTestCase
from tempfile import NamedTemporaryFile
import sys, os
sys.path.append(os.path.abspath('..'))
import modules
from unittest import skipIf
from test import conf


class FSDownload(FolderFileFSTestCase):

    def setUp(self):
        self.temp_path = NamedTemporaryFile(); self.temp_path.close(); 
        self.download_path = os.path.join(self.basedir, self.filenames[0])
        

    def test_download(self):
        
        self.assertRegexpMatches(self._warn(':file.download /etc/gne /tmp/asd') , modules.file.download.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':file.download /etc/passwd /tmpsaddsaas/asd') , 'Errno')
        self.assertRegexpMatches(self._warn(':file.download /etc/shadow /tmp/asd') , modules.file.download.WARN_NO_SUCH_FILE)


        self.assertEqual(self._res(':file.download %s %s -vector file'  % (self.download_path, self.temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector fread'  % (self.download_path, self.temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector file_get_contents'  % (self.download_path, self.temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector copy'  % (self.download_path, self.temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector symlink'  % (self.download_path, self.temp_path.name)), '1')

    @skipIf(not conf['shell_sh'], "Skipping shell.sh dependent tests")
    def test_download_sh(self):
        self.assertEqual(self._res(':file.download %s %s -vector base64'  % (self.download_path, self.temp_path.name)), '1')
        
    def test_read(self):
        
        self.assertRegexpMatches(self._warn(':file.read /etc/gne') , modules.file.download.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':file.read /etc/shadow') , modules.file.download.WARN_NO_SUCH_FILE)

        self.assertEqual(self._outp(':file.read %s -vector file'  % (self.download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector fread'  % (self.download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector file_get_contents'  % (self.download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector copy'  % (self.download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector symlink'  % (self.download_path)), '1')
        
    @skipIf(not conf['shell_sh'], "Skipping shell.sh dependent tests")
    def test_read_sh(self):
        self.assertEqual(self._outp(':file.read %s -vector base64'  % (self.download_path)), '1')
        