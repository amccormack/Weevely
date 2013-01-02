#!/usr/bin/env python
import sys, os, socket, unittest, shlex, random, pexpect
sys.path.append(os.path.abspath('..'))
import core.terminal
from core.modulehandler import ModHandler
from ConfigParser import ConfigParser
from string import ascii_lowercase, Template
from tempfile import NamedTemporaryFile
from PythonProxy import start_server, start_dummy_tcp_server  
from thread import start_new_thread    
from shutil import move
from time import sleep

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
        cls._env_mkdir(cls.basedir)
        
    @classmethod     
    def _unsetenv(cls):  
        cls._env_rm()        

    @classmethod
    def _run_test(cls, command, quiet=True):
        if quiet:
            stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')  
        else:
            print command
            
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
        #print '\n%s' % cmd,
        child = pexpect.spawn(cmd, timeout=int(conf['timeout']))
        idx = child.expect([pexpect.TIMEOUT, pexpect.EOF])
        #if idx == 0: child.interact()
        

    @classmethod  
    def _env_mkdir(cls, relpath):
        abspath = os.path.join(cls.basedir, relpath)
        cmd = Template(conf['env_mkdir_command']).safe_substitute(path=abspath)
        cls._run_cmd(cmd)

        
    @classmethod  
    def _env_newfile(cls, relpath, content = '1', currentuser=False):
    
        file = NamedTemporaryFile()
        file.close()
        frompath = file.name
        
        f = open(frompath, 'w')
        f.write(content)
        f.close()
        
        abspath = os.path.join(cls.basedir, relpath)
        if not currentuser:
            cmd = Template(conf['env_cp_command']).safe_substitute(frompath=frompath, topath=abspath)
        else:
            cmd = Template(conf['env_cp_command_currentuser']).safe_substitute(frompath=frompath, topath=abspath)
            
        cls._run_cmd(cmd)



    @classmethod  
    def _env_chmod(cls, relpath, mode='744', currentuser=False, recursion=False):
        abspath = os.path.join(cls.basedir, relpath)
        
        if not recursion:
            recursive = ''
        else:
            recursive = ' -R '
        
        if not currentuser:
            cmd = Template(conf['env_chmod_command']).safe_substitute(path=abspath, mode=mode, recursive=recursive)
        else:
            cmd = Template(conf['env_chmod_command_currentuser']).safe_substitute(path=abspath, mode=mode, recursive=recursive)
            

        cls._run_cmd(cmd)

    @classmethod  
    def _env_rm(cls, relpath = '', currentuser=False):
        abspath = os.path.join(cls.basedir, relpath)
        
        # Restore modes
        cls._env_chmod(cls.basedir, recursion=True)
        
        if cls.basedir.count('/') < 3:
            print 'Please check %s, not removing' % cls.basedir
            return
        
        if not currentuser:
            cmd = Template(conf['env_rm_command']).safe_substitute(path=abspath)
        else:
            cmd = Template(conf['env_rm_command_currentuser']).safe_substitute(path=abspath)

        cls._run_cmd(cmd)


    @classmethod  
    def _env_cp(cls, absfrompath, reltopath, currentuser=False):
        
        abstopath = os.path.join(cls.basedir, reltopath)
        if not currentuser:
            cmd = Template(conf['env_cp_command']).safe_substitute(frompath=absfrompath, topath=abstopath)
        else:
            cmd = Template(conf['env_cp_command_currentuser']).safe_substitute(frompath=absfrompath, topath=abstopath)
            
        cls._run_cmd(cmd)


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
        cls._env_chmod(cls.basedir, recursion=True)

class RcTestCase(SimpleTestCase):
    
    @classmethod
    def _setenv(cls):
        
        SimpleTestCase._setenv.im_func(cls)

        cls.rcpath = os.path.expanduser('~/.weevely/weevely.rc')
        cls.rcbackuppath = '%s_backup' % cls.rcpath

        move(cls.rcpath, cls.rcbackuppath)


    @classmethod
    def _unsetenv(cls):
        SimpleTestCase._unsetenv.im_func(cls)    
        move(cls.rcbackuppath, cls.rcpath)

    
class ProxyTestCase(RcTestCase):
    
    @classmethod
    def _setenv(cls):
        RcTestCase._setenv.im_func(cls)

        cls.proxyport = random.randint(50000,65000)
        start_new_thread(start_server, ('localhost', cls.proxyport))
        cls.dummyserverport = cls.proxyport+1
        start_new_thread(start_dummy_tcp_server, ('localhost', cls.dummyserverport))


    @classmethod
    def _unsetenv(cls):
        RcTestCase._unsetenv.im_func(cls)    
  
            
