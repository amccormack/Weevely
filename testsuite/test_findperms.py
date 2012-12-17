from baseclasses import FolderFileFSTestCase, conf
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

class FSFindCheck(FolderFileFSTestCase):

    def test_perms(self):
        
        sorted_files = sorted(['./%s' % x for x in self.filenames])
        sorted_folders = sorted(['./%s' % x for x in self.dirs] + ['.'])
        sorted_files_and_folders = sorted(sorted_files + sorted_folders)

        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(sorted(self._outp(':find.perms').split('\n')), sorted_files_and_folders)
        self.assertEqual(sorted(self._outp(':find.perms -vector find').split('\n')), sorted_files_and_folders)
        self.assertEqual(sorted(self._outp(':find.perms -vector php_recursive').split('\n')), sorted_files_and_folders)
        self.assertEqual(sorted(self._outp(':find.perms -vector find -type f').split('\n')), sorted_files)
        self.assertEqual(sorted(self._outp(':find.perms -vector php_recursive -type f').split('\n')), sorted_files)
        self.assertEqual(sorted(self._outp(':find.perms -vector find -type d').split('\n')), sorted_folders)
        self.assertEqual(sorted(self._outp(':find.perms -vector php_recursive -type d').split('\n')), sorted_folders)


    def test_specific_perms(self):
        
        sorted_files = sorted(['./%s' % x for x in self.filenames])
        sorted_folders = sorted(['./%s' % x for x in self.dirs] + ['.'])
        sorted_files_and_folders = sorted(sorted_files + sorted_folders)

        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.__class__._env_chmod(self.dirs[3], mode='555', recursion=True) # -xr
        self.assertEqual(self._outp(':find.perms %s -vector find -writable' % self.dirs[3]), '')
        self.assertEqual(sorted(self._outp(':find.perms %s -vector find -executable' % self.dirs[3]).split('\n')), [self.dirs[3], self.filenames[3]])
        self.assertEqual(sorted(self._outp(':find.perms %s -vector find -readable' % self.dirs[3]).split('\n')), [self.dirs[3], self.filenames[3]])
 

        self.__class__._env_chmod(self.filenames[3], mode='111') #--x 
        self.assertRegexpMatches(self._outp(':find.perms %s -vector php_recursive -executable' % self.dirs[3]), self.filenames[3])
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -writable' % self.dirs[3]), self.filenames[3])
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -readable' % self.dirs[3]), self.filenames[3])
        self.__class__._env_chmod(self.filenames[3], mode='222') #-w-
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -executable' % self.dirs[3]), self.filenames[3])
        self.assertRegexpMatches(self._outp(':find.perms %s -vector php_recursive -writable' % self.dirs[3]), self.filenames[3])
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -readable' % self.dirs[3]), self.filenames[3])
        self.__class__._env_chmod(self.filenames[3], mode='444') #r--
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -executable' % self.dirs[3]), self.filenames[3])
        self.assertNotRegexpMatches(self._outp(':find.perms %s -vector php_recursive -writable' % self.dirs[3]), self.filenames[3])
        self.assertRegexpMatches(self._outp(':find.perms %s -vector php_recursive -readable' % self.dirs[3]), self.filenames[3])

    def test_no_recursion(self):


        sorted_files = sorted(['./%s' % x for x in self.filenames])
        sorted_folders = sorted(['./%s' % x for x in self.dirs] + ['.'])
        sorted_files_and_folders = sorted(sorted_files + sorted_folders)

        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(sorted(self._res(':find.perms -no-recursion')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._res(':find.perms -vector find -no-recursion')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._res(':find.perms -vector php_recursive -no-recursion')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._res(':find.perms -vector find -type f -no-recursion')), [])
        self.assertEqual(sorted(self._res(':find.perms -vector find -type d -no-recursion')), sorted_folders[:2])


    