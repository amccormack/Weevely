from baseclasses import FolderFSTestCase, conf
from core.utils import randstr
from tempfile import mkdtemp
import os, sys
from string import ascii_lowercase
sys.path.append(os.path.abspath('..'))
import modules
import modules.net.mount
import modules.file.upload2web
import modules.file.upload


class Mount(FolderFSTestCase):


    def test_mount_expected_behaviour(self):
        
        temp_filename = randstr(4) + '.php'
        env_writable_url = os.path.join(conf['env_base_web_url'], conf['env_base_writable_web_dir'].replace(conf['env_base_web_dir'],''))
        env_writable_baseurl = os.path.join(env_writable_url, os.path.split(self.basedir)[-1])
        
        temp_dir = mkdtemp()
        
        self._outp('cd %s' % self.basedir)
        
        res = self._res(':net.mount')
        self.assertTrue(res and res[0].startswith(env_writable_baseurl) and res[0].endswith('.php') and res[1].startswith('/tmp/tmp') and res[2] == '.' )
        
        res = self._res(':net.mount -remote-mount /tmp/')
        self.assertTrue(res and res[0].startswith(env_writable_baseurl) and res[0].endswith('.php') and res[1].startswith('/tmp/tmp') and res[2] == '/tmp/')

        res = self._res(':net.mount -local-mount %s' % temp_dir)
        self.assertTrue(res and res[0].startswith(env_writable_baseurl) and res[0].endswith('.php') and res[1] == temp_dir and res[2] == '.')

        self.assertTrue(self._res(':net.mount -umount-all'))

        res = self._res(':net.mount -local-mount %s -rpath %s' % (temp_dir, temp_filename))
        self.assertTrue(res and res[0] == os.path.join(env_writable_baseurl, temp_filename) and res[1] == temp_dir and res[2] == '.')
        
        res = self._res(':net.mount -rpath %s -force' % (temp_filename))
        self.assertTrue(res and res[0] == os.path.join(env_writable_baseurl, temp_filename) and res[1].startswith('/tmp/tmp') and res[2] == '.')
        
        res = self._res(':net.mount -startpath %s' % (self.dirs[0]))
        self.assertTrue(res and res[0].startswith(os.path.join(env_writable_baseurl,self.dirs[0])) and res[0].endswith('.php') and res[1].startswith('/tmp/tmp') and res[2] == '.')

        res = self._res(':net.mount -just-mount %s ' % os.path.join(env_writable_baseurl, temp_filename))
        self.assertTrue(res and res[0] == os.path.join(env_writable_baseurl, temp_filename) and res[1].startswith('/tmp/tmp') and res[2] == '.')
        
        res = self._res(':net.mount -just-install')
        self.assertTrue(res and res[0].startswith(env_writable_baseurl) and res[0].endswith('.php') and res[1] == None and res[2] == '.' )


        self.assertTrue(self._res(':net.mount -umount-all'))
        self.assertRegexpMatches(self._warn(':net.mount -umount-all'), modules.net.mount.WARN_MOUNT_NOT_FOUND)

    def test_mount_errors(self):
        
        temp_filename = randstr(4) + '.php'
        env_writable_url = os.path.join(conf['env_base_web_url'], conf['env_base_writable_web_dir'].replace(conf['env_base_web_dir'],''))
        env_writable_baseurl = os.path.join(env_writable_url, os.path.split(self.basedir)[-1])
        
        temp_dir = mkdtemp()
        
        self._outp('cd %s' % self.basedir)

        self.assertRegexpMatches(self._warn(':net.mount -remote-mount /nonexistant/'),modules.net.mount.WARN_HTTPFS_OUTP)

        self.assertRegexpMatches(self._warn(':net.mount -local-mount /nonexistant/'),modules.net.mount.WARN_HTTPFS_OUTP)


        self.assertRegexpMatches(self._warn(':net.mount -rpath /notinwebroot'), modules.file.upload2web.WARN_NOT_WEBROOT_SUBFOLDER)
        self.assertRegexpMatches(self._warn(':net.mount -rpath ./unexistant/path'), modules.file.upload2web.WARN_NOT_FOUND)
        res = self._res(':net.mount -just-install -rpath %s' % (temp_filename))
        self.assertRegexpMatches(self._warn(':net.mount -just-install -rpath %s' % (temp_filename)), modules.file.upload.WARN_FILE_EXISTS)

        self.assertRegexpMatches(self._warn(':net.mount -startpath /notinwebroot'), modules.file.upload2web.WARN_NOT_FOUND)
        self.assertRegexpMatches(self._warn(':net.mount -startpath ./unexistant/path'), modules.file.upload2web.WARN_NOT_FOUND)

        #self.assertRegexpMatches(self._warn(':net.mount -just-mount nonexistanthost'),modules.net.mount.WARN_HTTPFS_OUTP)
        self.assertRegexpMatches(self._warn(':net.mount -just-mount %s/nonexistant' % env_writable_baseurl),modules.net.mount.WARN_HTTPFS_OUTP)
