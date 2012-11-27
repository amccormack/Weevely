from baseclasses import FolderFSTestCase, conf
import os, urllib2
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

class FSEnum(FolderFSTestCase):
    
    def __check_urlopen(self, result=None, url=None):
        if not url:
            self.assertTrue(result)
            self.assertTrue(result[1])
            url = result[1] 
            
        url += '?u=http://www.google.com'
        page = str(urllib2.urlopen(url).read())
        self.assertTrue(page)
        self.assertRegexpMatches(page.lower(), '<title>[\s]*google[\s]*</title>')        
        
    
    def test_phpproxy(self):
        
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        
        self.__check_urlopen(self._res(":net.phpproxy"))
        self.__check_urlopen(self._res(":net.phpproxy -find %s/.././%s/./" % (self.dirs[0], self.dirs[0])))
        
        self.assertRegexpMatches(self._warn(":net.phpproxy -find unexistant"), modules.net.phpproxy.WARN_NOT_FOUND)
        self.assertRegexpMatches(self._warn(":net.phpproxy -find /tmp/"), modules.net.phpproxy.WARN_NOT_WEBROOT_SUBFOLDER)
        self.assertRegexpMatches(self._warn(":net.phpproxy -find /unexistant"), modules.net.phpproxy.WARN_NOT_FOUND)
        
        
        web_base_url = '%s%s' %  (conf['env_base_web_url'], self.basedir.replace(conf['env_base_web_dir'],''))
        
        self.__check_urlopen(self._res(":net.phpproxy -install %s/.././%s/./inte.php" % (self.dirs[0], self.dirs[0])),'%s/%s/inte.php' % (web_base_url, self.dirs[0]))

        self.assertRegexpMatches(self._warn(":net.phpproxy -install unexistant"), modules.net.phpproxy.WARN_FILE_EXT)
        self.assertRegexpMatches(self._warn(":net.phpproxy -install /tmp/unexistant.php"), modules.net.phpproxy.WARN_NOT_WEBROOT_SUBFOLDER)
        self.assertRegexpMatches(self._warn(":net.phpproxy -install /unexistant.php"), modules.net.phpproxy.WARN_UPLOAD_FAIL)
        
        
    @classmethod     
    def _unsetenv(cls):  
        pass