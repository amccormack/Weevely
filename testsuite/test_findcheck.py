from baseclasses import FolderFileFSTestCase, conf
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

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


        self.assertEqual(sorted(self._outp(':find.perms -no-recursion').split('\n')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._outp(':find.perms -vector find -no-recursion').split('\n')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._outp(':find.perms -vector php_recursive -no-recursion').split('\n')), sorted_files_and_folders[:2])
        self.assertEqual(sorted(self._outp(':find.perms -vector find -type f -no-recursion').split('\n')), [''])
        self.assertEqual(sorted(self._outp(':find.perms -vector find -type d -no-recursion').split('\n')), sorted_folders[:2])


    
    def test_suidsgid(self):
        result = self._res(':find.suidsgid -suid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' in result and not '/usr/bin/wall' in result , True)
        result = self._res(':find.suidsgid -sgid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' not in result and '/usr/bin/wall' in result , True)
        result = self._res(':find.suidsgid -rpath /usr/bin')
        self.assertEqual('/usr/bin/sudo' in result and '/usr/bin/wall' in result , True)


    def test_name(self):
        
        sorted_files = sorted(['./%s' % x for x in self.filenames])
        sorted_folders = sorted(['./%s' % x for x in self.dirs])
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(sorted(self._res(':find.name FILE-')), sorted_files)
        self.assertEqual(sorted(self._res(':find.name file- -case')), sorted_files)
        self.assertEqual(sorted(self._res(':find.name W[0-9]')), sorted_folders)     
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case')), sorted_folders)
        self.assertEqual(sorted(self._res(':find.name file-1.txt -equal')), ['./w1/file-1.txt'])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath w1/w2')), ['./w1/w2/file-2.txt'])   
        
        self.assertEqual(sorted(self._res(':find.name FILE- -vector find')), sorted_files)
        self.assertEqual(sorted(self._res(':find.name file- -case -vector find')), sorted_files)
        self.assertEqual(sorted(self._res(':find.name W[0-9] -vector find')), sorted_folders)     
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case -vector find')), sorted_folders)
        self.assertEqual(sorted(self._res(':find.name file-1.txt -equal -vector find')), ['./w1/file-1.txt'])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath w1/w2 -vector find')), ['./w1/w2/file-2.txt'])   
        
        self.assertEqual(sorted(self._res(':find.name fIle- -case')), [''])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -case')), [''])
        self.assertEqual(sorted(self._res(':find.name ile-1.txt -equal')), [''])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath w1/w2 -equal')), [''])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath /asdsad -equal')), [''])  

        self.assertEqual(sorted(self._res(':find.name FILE- w1 -no-recursion')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name file- w1 -case -no-recursion')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -no-recursion')),  ['./w1'])   
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case -no-recursion')), ['./w1'])       

        self.assertEqual(sorted(self._res(':find.name FILE- w1 -no-recursion -vector find')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name file- w1 -case -no-recursion  -vector find')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -no-recursion  -vector find')),  ['./w1'])   
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case -no-recursion  -vector find')), ['./w1'])           
        
        