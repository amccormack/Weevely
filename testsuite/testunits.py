#!/usr/bin/env python
import sys, os
sys.path.append(os.path.abspath('..'))
import core.terminal
from core.modulehandler import ModHandler
from core.moduleexception import ModuleException
from ConfigParser import ConfigParser
import unittest, shlex
import modules.shell.php
from string import Template
from commands import getstatusoutput
from tempfile import NamedTemporaryFile
import pexpect

confpath = 'conf.ini'

configparser = ConfigParser()
configparser.read(confpath)
conf = configparser._sections['global']

class SimpleTestCase(unittest.TestCase):
    
    @classmethod  
    def setUpClass(cls):  
        cls._setenv()        
        cls.term = core.terminal.Terminal (ModHandler(conf['url'], conf['pwd']))

    @classmethod  
    def tearDownClass(cls):  
        cls._unsetenv()

    @classmethod  
    def _setenv(cls):  
        pass
    
    @classmethod     
    def _unsetenv(cls):  
        pass


    def _run_test(self, command, quiet=True):
        if quiet:
            stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')  
            
        #print '[>] %s' % command
        self.term.run_cmd_line(shlex.split(command))
        
        if quiet: 
            sys.stdout = stdout
        

    def _outp(self, command):
        self._run_test(command)
        return self.term._last_output
 
    def _warn(self, command):
        self._run_test(command)
        return self.term._last_warns
    

    @classmethod  
    def _run_cmd(cls, cmd):
        #print '\n[env] %s' % cmd,
        child = pexpect.spawn(cmd, timeout=1)
        idx = child.expect([pexpect.TIMEOUT, pexpect.EOF])
        if idx == 0: child.interact()
        

    @classmethod  
    def _env_mkdir(cls, relpath):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_mkdir_command']).safe_substitute(path=abspath)
        cls._run_cmd(cmd)

        
    @classmethod  
    def _env_newfile(cls, relpath, content = '1'):
    
        file = NamedTemporaryFile()
        file.close()
        frompath = file.name
        
        f = open(frompath, 'w')
        f.write('1')
        f.close()
        
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_cp_command']).safe_substitute(frompath=frompath, topath=abspath)
        cls._run_cmd(cmd)

    @classmethod  
    def _env_chmod(cls, relpath, mode='644'):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        cmd = Template(conf['env_chmod_command']).safe_substitute(path=abspath, mode=mode)
        cls._run_cmd(cmd)

    @classmethod  
    def _env_rm(cls, relpath):
        abspath = os.path.join(conf['env_base_writable_web_dir'], relpath)
        
        if conf['env_base_writable_web_dir'].count('/') < 3:
            print 'Please check %s, not removing' % conf['env_base_writable_web_dir']
            return
        
        cmd = Template(conf['env_rm_command']).safe_substitute(path=abspath)
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
        

class ShellsFSBrowse(SimpleTestCase):



    @classmethod
    def _setenv(cls):
        
        cls.basedir = conf['env_base_writable_web_dir']
        cls.newdirs = ['w1', 'w2', 'w3', 'w4']
        cls._env_rm(cls.newdirs[0])   
        cls._env_mkdir(os.path.join(*cls.newdirs))

    @classmethod
    def _unsetenv(cls):
        cls._env_rm(cls.newdirs[0])        
        
    def test_ls(self):
        
        self.assertEqual(self._outp('ls %s' % self.basedir), self.newdirs[0])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,self.newdirs[0])), self.newdirs[1])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:2])), self.newdirs[2])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:3])), self.newdirs[3])
        self.assertEqual(self._outp('ls %s' % os.path.join(self.basedir,*self.newdirs[:4])), '')
        self.assertEqual(self._outp('ls %s/.././/../..//////////////./../../%s/' % (self.basedir, self.basedir)), self.newdirs[0])


    def _path(self, command):
        self._run_test(command)
        return self.term.modhandler.load('shell.php').stored_args['path']

    def test_cwd(self):
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,*self.newdirs[:4])), os.path.join(self.basedir,*self.newdirs[:4]))
        self.assertEqual(self._path('cd .'), os.path.join(self.basedir,*self.newdirs[:4]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:3]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:2]))
        self.assertEqual(self._path('cd ..'), os.path.join(self.basedir,*self.newdirs[:1]))
        self.assertEqual(self._path('cd ..'), self.basedir)
        self.assertEqual(self._path('cd %s' % os.path.join(self.basedir,*self.newdirs)), os.path.join(self.basedir,*self.newdirs))
        self.assertEqual(self._path('cd .././/../..//////////////./../%s/../' % self.newdirs[0]), self.basedir)


class FSInteract(SimpleTestCase):

    @classmethod
    def _setenv(cls):
        
        cls.basedir = conf['env_base_writable_web_dir']
        cls.newdirs = ['w1', 'w2', 'w3', 'w4']
        cls.filenames = []
        cls._env_mkdir(os.path.join(*cls.newdirs))
        
        i=1
        for i in range(len(cls.newdirs)):
            pathlist = cls.newdirs[:i] + [ 'file-%s.txt' % cls.newdirs[i] ]
            filename = os.path.join(*pathlist)
            cls._env_newfile(filename)
            cls.filenames.append(filename)
            i+=1

        
    @classmethod
    def _unsetenv(cls):
        cls._env_rm(cls.newdirs[0])   
        for path in cls.filenames:
            cls._env_rm(path)   
            
        
    
    def test_check(self):
        
        self.assertEqual(self._outp(':file.check unexistant exists'), 'False')
        self.assertEqual(self._outp(':file.check %s read' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s exec' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % self.basedir), 'False')
        self.assertEqual(self._outp(':file.check %s exists' % self.basedir), 'True')
        self.assertEqual(self._outp(':file.check %s isfile' % os.path.join(self.basedir,self.filenames[0])), 'True')
        self.assertEqual(self._outp(':file.check %s md5' % os.path.join(self.basedir,self.filenames[0])), 'c4ca4238a0b923820dcc509a6f75849b')


    def test_rm(self):
        pass
        
        
#                        'rm' : TG(conf,
#                [
#                TC([ ':file.rm unexistant' ], ERR_NO_SUCH_FILE),
#                # Delete a single file
#                TC([ ':file.rm %s/newfile' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/newfile exists' % (conf['existant_base_dir']) ], 'False'),
#                
#                # Delete a single file recursively
#                TC([ ':file.rm %s/newfile1 -recursive' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/newfile1 exists' % (conf['existant_base_dir']) ], 'False'),               
#                
#                # Try to delete dir tree without recursion
#                TC([ ':file.rm %s/%s ' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'True'), 
#                
#                # Delete dir tree with recursion
#                TC([ ':file.rm %s/%s -recursive' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
#                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'False'), 
#                    
#                # VECTORS
#                TC([ ':set shell.php debug=1' ], PROMPT_PHP_SH),  
#                
#                # Delete with php_rmdir vector
#                TC([ ':file.rm %s/newfile2 -vector php_rmdir' % (conf['existant_base_dir']) ], "function rrmdir"),
#                TC([ ':file.check %s/newfile2 exists' % (conf['existant_base_dir']) ], 'False'),
#                
#                # Delete with rm vector
#                TC([ ':file.rm %s/newfile3 -vector rm -recursive' % (conf['existant_base_dir']) ], 'rm -rf %s' % (conf['existant_base_dir'])),
#                TC([ ':file.check %s/newfile3 exists' % (conf['existant_base_dir']) ], 'False'),
#                               
#                ]),


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
