from baseclasses import FolderFileFSTestCase
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

class FSRemove(FolderFileFSTestCase):

    def test_rm(self):
        
        # Delete a single file
        self.assertEqual(self._res(':file.rm %s' % os.path.join(self.basedir,self.filenames[1])), True)
        self.assertRegexpMatches(self._warn(':file.rm %s' % os.path.join(self.basedir,self.filenames[1])), modules.file.rm.WARN_NO_SUCH_FILE)
        
        # Delete a single file recursively
        self.assertEqual(self._res(':file.rm %s -recursive' % os.path.join(self.basedir,self.filenames[2])), True)
        self.assertRegexpMatches(self._warn(':file.rm %s -recursive' % os.path.join(self.basedir,self.filenames[2])), modules.file.rm.WARN_NO_SUCH_FILE)
        
        # Try to delete dir tree without recursion
        self.assertRegexpMatches(self._warn(':file.rm %s' % os.path.join(self.basedir,self.dirs[0])), modules.file.rm.WARN_DELETE_FAIL)
        
        # Delete dir tree with recursion
        self.assertEqual(self._res(':file.rm %s -recursive' % os.path.join(self.basedir,self.dirs[3])), True)
        
        # Vectors
        self.assertRegexpMatches(self._warn(':set shell.php debug=1'), 'debug=\'1\'')
        self.assertRegexpMatches(self._warn(':file.rm %s -recursive -vector php_rmdir' % os.path.join(self.basedir,self.dirs[2])), 'function rrmdir')

        # Vectors
        self.assertRegexpMatches(self._warn(':set shell.php debug=1'), 'debug=\'1\'')
        self.assertRegexpMatches(self._warn(':file.rm %s -recursive -vector rm' % os.path.join(self.basedir,self.dirs[1])), 'rm -rf %s' % os.path.join(self.basedir,self.dirs[1]) )
        
        # No permissions
        self.__class__._env_newfile('%s-currentuser' % self.filenames[0],currentuser=True)
        self.assertRegexpMatches(self._warn(':file.rm %s' % os.path.join(self.basedir,'%s-currentuser' % self.filenames[0])), modules.file.rm.WARN_NO_SUCH_FILE)
        self.__class__._env_rm('%s-currentuser' % self.filenames[0],currentuser=True)
        