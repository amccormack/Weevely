from baseclasses import FolderFileFSTestCase, conf
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

class FSFindCheck(FolderFileFSTestCase):

    
    def test_suidsgid(self):
        result = self._res(':find.suidsgid -suid -rpath /usr/bin')
        self.assertTrue('/usr/bin/sudo' in result and not '/usr/bin/wall' in result)
        result = self._res(':find.suidsgid -sgid -rpath /usr/bin')
        self.assertTrue('/usr/bin/sudo' not in result and '/usr/bin/wall' in result)
        result = self._res(':find.suidsgid -rpath /usr/bin')
        self.assertTrue('/usr/bin/sudo' in result and '/usr/bin/wall' in result)


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
        
        self.assertEqual(sorted(self._res(':find.name fIle- -case')), [])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -case')), [])
        self.assertEqual(sorted(self._res(':find.name ile-1.txt -equal')), [])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath w1/w2 -equal')), [])   
        self.assertEqual(sorted(self._res(':find.name 2.txt -rpath /asdsad -equal')), [])  

        self.assertEqual(sorted(self._res(':find.name FILE- w1 -no-recursion')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name file- w1 -case -no-recursion')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -no-recursion')),  ['./w1'])   
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case -no-recursion')), ['./w1'])       

        self.assertEqual(sorted(self._res(':find.name FILE- w1 -no-recursion -vector find')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name file- w1 -case -no-recursion  -vector find')), ['w1/file-1.txt'])
        self.assertEqual(sorted(self._res(':find.name W[0-9] -no-recursion  -vector find')),  ['./w1'])   
        self.assertEqual(sorted(self._res(':find.name w[0-9] -case -no-recursion  -vector find')), ['./w1'])           
        
        