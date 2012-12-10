from baseclasses import FolderFileFSTestCase
from tempfile import NamedTemporaryFile
import sys, os
sys.path.append(os.path.abspath('..'))
import modules


class FSDownload(FolderFileFSTestCase):

    def test_download(self):
        
        self.assertRegexpMatches(self._warn(':file.download /etc/gne /tmp/asd') , modules.file.download.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':file.download /etc/passwd /tmpsaddsaas/asd') , 'Errno')
        self.assertRegexpMatches(self._warn(':file.download /etc/shadow /tmp/asd') , modules.file.download.WARN_NO_SUCH_FILE)

        temp_path = NamedTemporaryFile(); temp_path.close(); 
        download_path = os.path.join(self.basedir, self.filenames[0])
        self.assertEqual(self._res(':file.download %s %s -vector file'  % (download_path, temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector fread'  % (download_path, temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector file_get_contents'  % (download_path, temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector base64'  % (download_path, temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector copy'  % (download_path, temp_path.name)), '1')
        self.assertEqual(self._res(':file.download %s %s -vector symlink'  % (download_path, temp_path.name)), '1')

    def test_read(self):
        
        self.assertRegexpMatches(self._warn(':file.read /etc/gne') , modules.file.download.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':file.read /etc/shadow') , modules.file.download.WARN_NO_SUCH_FILE)

        download_path = os.path.join(self.basedir, self.filenames[1])
        self.assertEqual(self._outp(':file.read %s -vector file'  % (download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector fread'  % (download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector file_get_contents'  % (download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector base64'  % (download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector copy'  % (download_path)), '1')
        self.assertEqual(self._outp(':file.read %s -vector symlink'  % (download_path)), '1')
        