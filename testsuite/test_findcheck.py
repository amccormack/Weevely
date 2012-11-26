from baseclasses import FolderFileFSTestCase, conf
import os

class FSFindCheck(FolderFileFSTestCase):

    def test_check(self):
        
        self.assertEqual(self._outp(':file.check unexistant exists'), 'False')
        self.assertEqual(self._outp(':file.check %s read' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s exec' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % self.basedir), 'False')
        self.assertEqual(self._outp(':file.check %s exists' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % os.path.join(self.basedir,self.filenames[0])), 'True')
        self.assertEqual(self._outp(':file.check %s md5' % os.path.join(self.basedir,self.filenames[0])), 'c4ca4238a0b923820dcc509a6f75849b')

    
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

    
    def test_webdir(self):
        self.__class__._unsetenv()
        self.__class__._setenv()
        
        self.assertEqual(self._res(':find.webdir -rpath %s' % self.basedir), [ self.basedir, 'http://localhost/%s' % (self.basedir.replace(conf['env_base_web_dir'],'')) ])
        folder_abs_path = os.path.join(self.basedir,self.dirs[0])
        folder_rel_path = os.path.join(self.basedir.replace(conf['env_base_web_dir'],''),self.dirs[0])
        self.assertEqual(self._res(':find.webdir -rpath %s' % folder_rel_path), [ folder_abs_path, '%s%s' % (conf['env_base_web_url'], folder_abs_path.replace(conf['env_base_web_dir'],'')) ])
        folder_rel_path_deepness = folder_rel_path.count('/')+1
        self.assertEqual(self._res(':find.webdir -rpath %s%s./%s' % (folder_rel_path, '/../'*folder_rel_path_deepness, folder_rel_path)), [ folder_abs_path, 'http://localhost/%s' % folder_abs_path.replace(conf['env_base_web_dir'],'') ])
        

    def test_suidsgid(self):
        result = self._res(':find.suidsgid -suid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' in result and not '/usr/bin/wall' in result , True)
        result = self._res(':find.suidsgid -sgid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' not in result and '/usr/bin/wall' in result , True)
        result = self._res(':find.suidsgid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' in result and '/usr/bin/wall' in result , True)

