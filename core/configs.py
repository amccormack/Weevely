import os
import core.terminal
import atexit
<<<<<<< HEAD
from urlparse import urlparse, urlsplit
=======
from urlparse import urlparse
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
from ConfigParser import ConfigParser

try:
        import readline
except ImportError:
    try:
        import pyreadline as readline
    except ImportError: 
        print '[!] Error, readline or pyreadline python module required. In Ubuntu linux run\n[!] sudo apt-get install python-readline'
        sys.exit(1)

dirpath = '.weevely'
rcfilepath = 'weevely.rc'
<<<<<<< HEAD
cfgext = '.conf'
=======
cfgfile = 'weevely.conf'
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
cfgfilepath = 'sessions'
historyfilepath = 'weevely_history'

class Configs():

<<<<<<< HEAD
    def _read_cfg(self, sessionfile):
        #sessionfile = os.path.join(cfgfilepath, sessionfile)
=======
    def _read_cfg(self, session):
        sessionfile = os.path.join(cfgfilepath, session, cfgfile)
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
        parser = ConfigParser()

        try:
          with open(sessionfile):
            parser.read(sessionfile)
            for key, value in parser.items('global'):
              setattr(self, key, value)
<<<<<<< HEAD
            print("[+] Reading session file '%s'\n" % sessionfile)
            return self.url, self.password

=======
            self._tprint("[+] Reading session file '%s'\n" % sessionfile)
            return self.url, self.password          
              
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
        except (IOError, Exception) as e:
          print( "[!] Error: %s" % e)
	  raise
          #self._tprint( "[!] Error opening '%s' file.\n" % sessionfile)

    def _write_cfg(self, url, configDict):

<<<<<<< HEAD
        hostname = urlparse(url).hostname
        weevname =  os.path.splitext(os.path.basename(urlsplit(url).path))[0]
        sessionfile = os.path.join(cfgfilepath, hostname, weevname + cfgext)
        parser = ConfigParser()

        try:
          if not os.path.exists(os.path.join(cfgfilepath, hostname)):
             os.makedirs(os.path.join(cfgfilepath, hostname))
=======
        session = urlparse(url).hostname
        sessionfile = os.path.join(cfgfilepath, session, cfgfile)
        parser = ConfigParser()

        try:
          if not os.path.exists(os.path.join(cfgfilepath, session)):
             os.makedirs(os.path.join(cfgfilepath, session))

>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
          writer = open(sessionfile, 'w')
          parser.add_section('global')
          parser.set('global', 'url', url)
          for k, v in configDict.iteritems():
<<<<<<< HEAD
              parser.set('global', k, v)
=======
              parser.set('global', k, v)    
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd
          parser.write(writer)

          print("[+] Writing session file '%s'\n" % sessionfile)

        except (IOError, Exception) as e:
          #print( "[!] Error: %s" % e)
          print( "[!] Error writing '%s' file: \n" % sessionfile)
<<<<<<< HEAD

=======
	 
>>>>>>> 465030c40dd69818a10c18d9509bd72622b524dd

    def _read_rc(self, rcpath):

        try:
            rcfile = open(rcpath, 'r')
        except Exception, e:
            self._tprint( "[!] Error opening '%s' file." % rcpath)
        else:
            return [c.strip() for c in rcfile.read().split('\n') if c.strip() and c[0] != '#']

        return []

    def _historyfile(self):
        return os.path.join(self.dirpath, historyfilepath)

    def _make_home_folder(self):

        self.dirpath = os.path.join(os.path.expanduser('~'),dirpath)
        
        if not os.path.exists(self.dirpath):
            os.mkdir(self.dirpath)


    def _init_completion(self):

    
            self.historyfile = self._historyfile()

            self.matching_words =  [':%s' % m for m in self.modhandler.modules_classes.keys()] + [core.terminal.help_string, core.terminal.load_string, core.terminal.set_string]
        
            try:
                readline.set_history_length(100)
                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind( 'tab: complete' )
                readline.set_completer( self._complete )
                readline.read_history_file( self.historyfile )

            except IOError:
                pass
            atexit.register( readline.write_history_file, self.historyfile )



    def _complete(self, text, state):
        """Generic readline completion entry point."""

        try:
            buffer = readline.get_line_buffer()
            line = readline.get_line_buffer().split()

            if ' ' in buffer:
                return []

            # show all commandspath
            if not line:
                all_cmnds = [c + ' ' for c in self.matching_words]
                if len(all_cmnds) > state:
                    return all_cmnds[state]
                else:
                    return []


            cmd = line[0].strip()

            if cmd in self.matching_words:
                return [cmd + ' '][state]

            results = [c + ' ' for c in self.matching_words if c.startswith(cmd)] + [None]
            if len(results) == 2:
                if results[state]:
                    return results[state].split()[0] + ' '
                else:
                    return []
            return results[state]

        except Exception, e:
            self._tprint('[!] Completion error: %s' % e)
