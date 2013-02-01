from baseclasses import SimpleTestCase
from tempfile import NamedTemporaryFile
from os import path
from core.utils import randstr
import os, sys
sys.path.append(os.path.abspath('..'))

import modules.file.edit

class Edit(SimpleTestCase):
    
    def test_edit(self):
        
        temp_filename = path.join('/tmp', randstr(4) )
        editor = "echo -n 1 >> "

        self.assertTrue(self._res(""":file.edit %s -editor "%s" """ % (temp_filename, editor)))
        self.assertTrue(self._res(""":file.edit %s -editor "%s" """ % (temp_filename, editor)))
        
        self.assertEqual(self._res(":file.read %s" % temp_filename), '11')
        
        self.assertRegexpMatches(self._warn(""":file.edit /tmp/non/existant -editor "%s" """ % (editor)), modules.file.edit.WARN_UPLOAD_FAILED)
        self.assertRegexpMatches(self._warn(""":file.edit /etc/protocols -editor "%s" """ % (editor)), modules.file.edit.WARN_UPLOAD_FAILED)
        self.assertRegexpMatches(self._warn(""":file.edit /etc/shadow -editor "%s" """ % (editor)), modules.file.edit.WARN_DOWNLOAD_FAILED)
        
        