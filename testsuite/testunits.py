#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
import core.terminal
from core.modulehandler import ModHandler
from core.moduleexception import ModuleException
from ConfigParser import ConfigParser
import unittest, shlex
import modules.shell.php
from string import Template, ascii_lowercase
from commands import getstatusoutput
from tempfile import NamedTemporaryFile
import pexpect, random

confpath = 'conf.ini'

configparser = ConfigParser()
configparser.read(confpath)
conf = configparser._sections['global']

class SimpleTestCase(unittest.TestCase):
    
    @classmethod  
    def setUpClass(cls):  
        
        cls.term = core.terminal.Terminal (ModHandler(conf['url'], conf['pwd']))
        cls._setenv()        

    @classmethod  
    def tearDownClass(cls):  
        cls._unsetenv()

    @classmethod  
    def _setenv(cls):  
        cls.basedir = os.path.join(conf['env_base_writable_web_dir'], ''.join(random.choice(ascii_lowercase) for x in range(4)))
        
    @classmethod     
    def _unsetenv(cls):  
        pass

    @classmethod
    def _run_test(cls, command, quiet=True):
        if quiet:
            stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')  
            
        #print '[>] %s' % command
        cls.term.run_cmd_line(shlex.split(command))
        
        if quiet: 
            sys.stdout = stdout
        

    def _outp(self, command):
        self.__class__._run_test(command)
        return self.term._last_output
 
    def _warn(self, command):
        self.__class__._run_test(command)
        return self.term.modhandler._last_warns

    def _res(self, command):
        self.__class__._run_test(command)
        return self.term._last_result

    @classmethod  
    def _run_cmd(cls, cmd):
        print '\n%s' % cmd,
        child = pexpect.spawn(cmd, timeout=1)
        idx = child.expect([pexpect.TIMEOUT, pexpect.EOF])
        if idx == 0: child.interact()
        

    @classmethod  
    def _env_mkdir(cls, relpath):
        abspath = os.path.join(cls.basedir, relpath)
        cmd = Template(conf['env_mkdir_command']).safe_substitute(path=abspath)
        cls._run_cmd(cmd)

        
    @classmethod  
    def _env_newfile(cls, relpath, content = '1', otheruser=False):
    
        file = NamedTemporaryFile()
        file.close()
        frompath = file.name
        
        f = open(frompath, 'w')
        f.write('1')
        f.close()
        
        abspath = os.path.join(cls.basedir, relpath)
        if not otheruser:
            cmd = Template(conf['env_cp_command']).safe_substitute(frompath=frompath, topath=abspath)
        else:
            cmd = Template(conf['env_cp_command_otheruser']).safe_substitute(frompath=frompath, topath=abspath)
            
        cls._run_cmd(cmd)



    @classmethod  
    def _env_chmod(cls, relpath, mode='744'):
        abspath = os.path.join(cls.basedir, relpath)
        cmd = Template(conf['env_chmod_command']).safe_substitute(path=abspath, mode=mode)

        cls._run_cmd(cmd)

    @classmethod  
    def _env_rm(cls, relpath = '', otheruser=False):
        abspath = os.path.join(cls.basedir, relpath)
        
        # Restore modes
        cls._env_chmod(cls.basedir)
        
        if cls.basedir.count('/') < 3:
            print 'Please check %s, not removing' % cls.basedir
            return
        
        if not otheruser:
            cmd = Template(conf['env_rm_command']).safe_substitute(path=abspath)
        else:
            cmd = Template(conf['env_rm_command_otheruser']).safe_substitute(path=abspath)

        cls._run_cmd(cmd)

class Shells(SimpleTestCase):


    def test_php(self):
        
        self.assertEqual(self._outp(':shell.php echo(1+1);'), '2')
        self.assertRegexpMatches(self._warn(':shell.php echo(1+1)'), '%s' % modules.shell.php.WARN_TRAILING_SEMICOLON )
        self.assertRegexpMatches(self._warn(':shell.php echo(1+1); -debug 1'), 'Request[\S\s]*Response' )
        self.assertEqual(self._outp(':shell.php print($_COOKIE);'), 'Array')   
        self.assertRegexpMatches(self._warn(':shell.php print($_COOKIE); -mode Referer'), modules.shell.php.WARN_NO_RESPONSE),
        # Check if wrongly do __slacky_probe at every req    
        self.assertRegexpMatches(self._warn(':shell.php echo(1); -debug 1'), 'Request[\S\s]*Response'),   
        self.assertEqual(self._outp(':shell.php echo(2); -precmd print(1);'), '12')  
        self.assertEqual(self._outp(':shell.php -post "{ \'FIELD\':\'VALUE\' }" echo($_POST[\'FIELD\']);'), 'VALUE') 

    def test_sh(self):
        self.assertEqual(self._outp(':shell.sh echo $((1+1))'), '2')
        self.assertEqual(self._outp('echo $((1+1))'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector shell_exec'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector system'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector exec'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector popen'), '2')
        #self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector python_eval'), '2')
        #self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector perl_system'), '2')
        self.assertEqual(self._outp(':shell.sh echo "$((1+1))" -vector proc_open'), '2')
        self.assertEqual(self._outp(':shell.sh \'(echo "VISIBLE" >&2)\' -stderr'), 'VISIBLE')
        self.assertEqual(self._outp(':shell.sh \'(echo "INVISIBLE" >&2)\''), '')
      
      
    def test_info(self):
        self.assertEqual(self._outp(':system.info os'), 'Linux')
        self.assertRegexpMatches(self._outp(':system.info'), 'safe_mode')
        

class FolderFSTestCase(SimpleTestCase):

    @classmethod
    def _setenv(cls):
        
        SimpleTestCase._setenv.im_func(cls)
        
        cls.dirs =  []
        newdirs = ['w1', 'w2', 'w3', 'w4']
        
        for i in range(1,len(newdirs)+1):
            folder = os.path.join(*newdirs[:i])
            cls.dirs.append(folder)
        
        cls._env_mkdir(os.path.join(*newdirs))

    @classmethod
    def _unsetenv(cls):
        SimpleTestCase._unsetenv.im_func(cls)
        cls._env_rm()        


    def _path(self, command):
        self.__class__._run_test(command)
        return self.term.modhandler.load('shell.php').stored_args['path']


class FolderFileFSTestCase(FolderFSTestCase):
    
    @classmethod
    def _setenv(cls):    
        FolderFSTestCase._setenv.im_func(cls)
        
        cls.filenames = []
        i=1
        for dir in cls.dirs:
            filename = os.path.join(dir, 'file-%d.txt' % i )
            cls._env_newfile(filename)
            cls.filenames.append(filename)
            i+=1

        # Restore modes
        cls._env_chmod(cls.basedir)


class ShellsFSBrowse(FolderFSTestCase):

        
    def test_ls(self):
        
        self.assertEqual(self._outp('ls %s' % self.basedir), self.dirs[0])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.dirs[0])), self.dirs[1].split('/')[-1])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.dirs[1])), self.dirs[2].split('/')[-1])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.dirs[2])), self.dirs[3].split('/')[-1])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.dirs[3])), '')
        self.assertEqual(self._outp('ls %s/.././/../..//////////////./../../%s/' % (self.basedir, self.basedir)), self.dirs[0])

    def test_cwd(self):
        
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,self.dirs[3])), os.path.join(self.basedir,self.dirs[3]))
        self.assertEqual(self._path('cd .'), os.path.join(self.basedir,self.dirs[3]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,self.dirs[2]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,self.dirs[1]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,self.dirs[0]))
        self.assertEqual(self._path('cd ..'), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,self.dirs[3])), os.path.join(self.basedir,self.dirs[3]))
        self.assertEqual(self._path('cd .././/../..//////////////./../%s/../' % self.dirs[0]), self.basedir)


class FSInteract(FolderFileFSTestCase):

    
    def test_check(self):
        
        self.assertEqual(self._outp(':file.check unexistant exists'), 'False')
        self.assertEqual(self._outp(':file.check %s read' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s exec' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % self.basedir), 'False')
        self.assertEqual(self._outp(':file.check %s exists' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % os.path.join(self.basedir,self.filenames[0])), 'True')
        self.assertEqual(self._outp(':file.check %s md5' % os.path.join(self.basedir,self.filenames[0])), 'c4ca4238a0b923820dcc509a6f75849b')

class FSFind(FolderFileFSTestCase):
    
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

        self.__class__._env_chmod(self.dirs[3], mode='555') # -xr
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
        self.__class__._env_newfile('%s-otheruser' % self.filenames[0],otheruser=True)
        self.assertRegexpMatches(self._warn(':file.rm %s' % os.path.join(self.basedir,'%s-otheruser' % self.filenames[0])), modules.file.rm.WARN_NO_SUCH_FILE)
        self.__class__._env_rm('%s-otheruser' % self.filenames[0],otheruser=True)
        


if __name__ == '__main__':
    unittest.main(verbosity=2)
#    suite = unittest.TestLoader().loadTestsFromTestCase(FSInteract)
#    unittest.TextTestRunner(verbosity=2).run(suite)



#            'cwd_safemode' : TG(conf,
#                [
#                TC([ 'cd unexistant' ], ERR_NO_SUCH_FILE),       
#                TC([ 'cd ..' ], ERR_NO_SUCH_FILE),       
#                ]),
#  
#            'ls_safemode' : TG(conf,
#                [
#                TC([ 'ls unexistant' ], ERR_NO_SUCH_FILE),       
#                TC([ 'ls /' ], ERR_NO_SUCH_FILE),    
#                TC([ 'ls /tmp/' ], ERR_NO_SUCH_FILE),    
#
#                ]),
