from modules.file.upload2web import Upload2web
from modules.file.upload import WARN_NO_SUCH_FILE
from core.moduleexception import ModuleException, ProbeException, ProbeSucceed
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
import re, os
from core.utils import randstr
from commands import getstatusoutput
from tempfile import mkdtemp
from urlparse import urlparse
from platform import machine

WARN_ERR_RUN_HTTPFS = 'Binary run failed'
WARN_ERR_GEN_PHP = 'HTTPfs PHP generation failed'
WARN_HTTPFS_OUTP = 'HTTPfs output debug'
WARN_HTTPFS_RUN = 'HTTPfs run failed'
WARN_FUSE_UMOUNT = 'Fusermount umount failed'
WARN_MOUNT = 'Mount call failed'
WARN_MOUNT_NOT_FOUND = 'No HTTPfs mount found'
WARN_HTTPFS_CHECK = 'Check HTTPfs configuration following \'https://github.com/cyrus-and/httpfs\' instructions'

class Mount(Upload2web):
    '''Mount remote filesystem using HTTPfs '''

    def _set_args(self):
        
        self.argparser.add_argument('-remote-mount', help='Mount remote folder, default: \'.\'', default = '.')
        self.argparser.add_argument('-local-mount', help='Mount in local mountpoint, default: temporary folder')
        
        self.argparser.add_argument('-rpath', help='Upload PHP agent as rpath', nargs='?')
        self.argparser.add_argument('-startpath', help='Upload PHP agent in first writable subdirectory', metavar='STARTPATH', default='.')

        
        self.argparser.add_argument('-just-mount', metavar='URL', help='Mount URL without install PHP agent')
        self.argparser.add_argument('-just-install', action='store_true', help="Install remote PHP agent without mount")
        self.argparser.add_argument('-umount-all', action='store_true', help='Umount all mounted HTTPfs filesystems')
        
        self.argparser.add_argument('-force', action='store_true', help=SUPPRESS)
        self.argparser.add_argument('-chunksize', type=int, default=1024, help=SUPPRESS)
        self.argparser.add_argument('-vector', choices = self.vectors.keys(), help=SUPPRESS)
        
    
    def _prepare_probe(self):

        httpfs_filename = 'httpfs.' + machine()
        self.httpfs_path = os.path.join(self.modhandler.path_modules, 'net', 'external', httpfs_filename)

        # If not umount or just-mount URL, try installation
        if not self.args['umount_all'] and not self.args['just_mount']:
            
            self.__generate_httpfs()
            
            Upload2web._prepare_probe(self)

        # If just mount, set remote url
        elif self.args['just_mount']:
            self.args['url'] = self.args['just_mount']



    def _probe(self):
        
        if self.args['umount_all']:
            # Umount all httpfs partitions
            self.__umount_all()
            raise ProbeSucceed(self.name, 'Unmounted partitions')
        
        if not self.args['just_mount']:
            # Upload remote
            try:    
                Upload2web._probe(self)
            except ProbeSucceed:
                self._result = True
                
        if not self.args['just_install']:
    
            if not self.args['local_mount']:
                self.args['local_mount'] = mkdtemp()
                
            cmd = '%s mount %s %s %s' % (self.httpfs_path, self.args['url'], self.args['local_mount'], self.args['remote_mount'])
    
            status, output = getstatusoutput(cmd)
            if status == 0:
                if output:
                    raise ProbeException(self.name,'%s\nCOMMAND:\n$ %s\nOUTPUT:\n> %s\n%s' % (WARN_HTTPFS_OUTP, cmd, output.replace('\n', '\n> '), WARN_HTTPFS_CHECK))
                    
            else:
                raise ProbeException(self.name,'%s\nCOMMAND:\n$ %s\nOUTPUT:\n> %s\n%s' % (WARN_HTTPFS_RUN, cmd, output.replace('\n', '\n> '), WARN_HTTPFS_CHECK))
                    

    def _verify_probe(self):
        # Verify Install
        if not self.args['umount_all'] and not self.args['just_mount']:
            Upload2web._verify_probe(self)
              
    def _output_result(self):


        self._result = [
                        self.args['url'] if 'url' in self.args else None, 
                        self.args['local_mount'], 
                        self.args['remote_mount']
                        ]

        # Verify Install
        if not self.args['umount_all'] and not self.args['just_mount'] and not self.args['just_install']:
            
            remoteuri = self.support_vectors.get('normalize').execute({ 'path' : self.args['remote_mount'] })
            urlparsed = urlparse(self.modhandler.url)
            if urlparsed.hostname:
                remoteuri = '%s:%s' % (urlparsed.hostname, remoteuri)
    
            rpath = ' '
            if self.args['rpath']:
                rpath = ' \'%s\' ' % self.args['rpath']
    
            self._output = """Mounted '%s' to local folder '%s'. 
Run ":net.mount -just-mount '%s'" to remount without reinstalling remote agent.
Umount using ':net.mount -umount %s'. When not needed anymore, remove%sremote agent.""" % ( remoteuri, self.args['local_mount'], self.args['url'], self.args['local_mount'], rpath )
                
                
    def __umount_all(self):
        
        status, output = getstatusoutput('mount')
        if status != 0 or not output:
            raise ProbeException(self.name, '%s: %s' % (WARN_FUSE_UMOUNT, output))     

        local_mountpoints = re.findall('(/[\S]+).+httpfs',output)
        if not local_mountpoints:
            raise ProbeException(self.name, WARN_MOUNT_NOT_FOUND)  
            
        for mountpoint in local_mountpoints:
        
            cmd = 'fusermount -u %s' % (mountpoint)
            status, output = getstatusoutput(cmd)
            if status != 0:
                raise ProbeException(self.name, '%s: %s' % (WARN_FUSE_UMOUNT, output))     
        
        self._result = True
        self.mprint('Umounted: \'%s\'' % '\', '.join(local_mountpoints))


    def __check_httpfs(self):
        
        if os.path.isfile(self.httpfs_path):
            status, output = getstatusoutput('%s --version' % self.httpfs_path)
            if status != 0 or not output:
                raise ProbeException(self.name, '\'%s\' %s' % (self.httpfs_path, WARN_ERR_RUN_HTTPFS))        

    def __generate_httpfs(self):
        
        status, php_bd_content = getstatusoutput('%s generate php' % (self.httpfs_path))
        if status != 0 or not php_bd_content:
            raise ProbeException(self.name, '\'%s\' %s' % (self.httpfs_path, WARN_ERR_GEN_PHP))

        self.args['lpath'] = randstr(4) + '.php'
        self.args['content'] = php_bd_content        
        