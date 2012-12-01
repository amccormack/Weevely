from baseclasses import FolderFSTestCase, conf
import os, urllib2
import os, sys
sys.path.append(os.path.abspath('..'))
import modules

class Proxies(FolderFSTestCase):
    
    @classmethod
    def _setenv(cls):    
        FolderFSTestCase._setenv.im_func(cls)
        cls._env_newfile('web_page4.html', content=conf['web_page4_content'])
    
    def __check_urlopen(self, result=None, url=None):
        
        if not url:
            self.assertEqual(len(result),2)
            self.assertTrue(result[1])
            url = result[1] 
            
        web_page4_relative_path = os.path.join(self.basedir.replace(conf['env_base_web_dir'],''), 'web_page4.html')        
        web_page4_url = '%s%s' %  (conf['env_base_web_url'], web_page4_relative_path)

        url += '?u=%s' % web_page4_url
        page = str(urllib2.urlopen(url).read())
        self.assertTrue(page)
        self.assertRegexpMatches(page.lower(), '')        
        
    
    def test_phpproxy(self):
        
        
        self.assertEqual(self._path('cd %s' % self.basedir), self.basedir)
        
        self.__check_urlopen(self._res(":net.phpproxy"))
        self.__check_urlopen(self._res(":net.phpproxy -startpath %s/.././%s/./" % (self.dirs[0], self.dirs[0])))
        
        self.assertRegexpMatches(self._warn(":net.phpproxy -startpath unexistant"), modules.file.upload2web.WARN_NOT_FOUND)
        self.assertRegexpMatches(self._warn(":net.phpproxy -startpath /tmp/"), modules.file.upload2web.WARN_NOT_WEBROOT_SUBFOLDER)
        self.assertRegexpMatches(self._warn(":net.phpproxy -startpath /unexistant"), modules.file.upload2web.WARN_NOT_FOUND)
        
        
        web_base_url = '%s%s' %  (conf['env_base_web_url'], self.basedir.replace(conf['env_base_web_dir'],''))
        
        self.__check_urlopen(self._res(":net.phpproxy %s/.././%s/./inte.php" % (self.dirs[0], self.dirs[0])),'%s/%s/inte.php' % (web_base_url, self.dirs[0]))

        self.assertRegexpMatches(self._warn(":net.phpproxy unexistant/unexistant"), modules.file.upload2web.WARN_NOT_FOUND)
        self.assertRegexpMatches(self._warn(":net.phpproxy /tmp/unexistant.php"), modules.file.upload2web.WARN_NOT_WEBROOT_SUBFOLDER)
        self.assertRegexpMatches(self._warn(":net.phpproxy /unexistant.php"), modules.file.upload2web.WARN_NOT_WEBROOT_SUBFOLDER)
        