from baseclasses import SimpleTestCase, FolderFSTestCase, conf
import os, sys
sys.path.append(os.path.abspath('..'))
import modules


class WebMap(SimpleTestCase):
    
    
    @classmethod
    def _setenv(cls):    
        FolderFSTestCase._setenv.im_func(cls)
        
        cls._env_newfile('web_page1.html', content=conf['web_page1_content'])
        cls._env_newfile('web_page2.html', content=conf['web_page2_content'])
        cls._env_newfile('web_page3.html', content=conf['web_page3_content'])

    def test_mapweb(self):
        
        web_page1_relative_path = os.path.join(self.basedir.replace(conf['env_base_web_dir'],''), 'web_page1.html')
        web_page1_url = '%s%s' %  (conf['env_base_web_url'], web_page1_relative_path)
        web_base_url = '%s%s' %  (conf['env_base_web_url'], self.basedir.replace(conf['env_base_web_dir'],''))
        
        webmap = {
                  os.path.join(self.basedir, 'web_page1.html'): ['exists', 'readable', 'writable', ''],
                  os.path.join(self.basedir, 'web_page2.html'): ['exists', 'readable', 'writable', ''],
                  os.path.join(self.basedir, 'web_page3.html'): ['exists', 'readable', 'writable', ''],
                  }



        self.assertEqual(self._res(':audit.mapwebfiles %s %s %s' % (web_page1_url, web_base_url, self.basedir)), webmap)
        self.assertRegexpMatches(self._warn(':audit.mapwebfiles %s_unexistant.html %s %s' % (web_page1_url, web_base_url, self.basedir)), modules.audit.mapwebfiles.WARN_CRAWLER_NO_URLS)

        web_page1_badurl = 'http://localhost:90/%s' %  (web_page1_relative_path)
        self.assertRegexpMatches(self._warn(':audit.mapwebfiles %s %s %s' % (web_page1_badurl, web_base_url, self.basedir)), modules.audit.mapwebfiles.WARN_CRAWLER_NO_URLS)

