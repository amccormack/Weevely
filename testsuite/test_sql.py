from baseclasses import SimpleTestCase, conf
from tempfile import NamedTemporaryFile
import random, string
import sys, os
sys.path.append(os.path.abspath('..'))
import modules

class MySql(SimpleTestCase):
    
    
    def test_query(self):

        dbms = conf['test_only_dbms']

        if dbms == 'mysql' or not dbms:
            
            user = conf['mysql_sql_user']
            pwd = conf['mysql_sql_pwd']
            default_user = conf['mysql_sql_default_user']
            
            self.assertEqual(self._res(':sql.console %s %s -query "SELECT USER();"' % ( user, pwd ) ), [['%s@localhost' % user ]])
            
            # First this, warning is printed only first time
            self.assertRegexpMatches(self._warn(':sql.console %s wrongpass -query "SELECT USER();"' % ( user) ), modules.sql.console.WARN_FALLBACK)
            self.assertEqual(self._res(':sql.console %s wrongpass -query "SELECT USER();"' % ( user ) ), [['%s@localhost' % default_user ]])
            
            self.assertEqual(self._res(':sql.console %s %s -host notreachable -query "SELECT USER();"' % ( user, pwd ) ), [['%s@localhost' % default_user ]])


class PGSql(SimpleTestCase):
    
    def test_query(self):
            
        dbms = conf['test_only_dbms']
        
        if dbms == 'postgres' or not dbms:
            
            user = conf['pg_sql_user']
            pwd = conf['pg_sql_pwd']

            self.assertEqual(self._res(':sql.console %s %s -query "SELECT USER;" -dbms postgres' % ( user, pwd ) ), [[ user ]])
            self.assertRegexpMatches(self._warn(':sql.console %s wrongpass -query "SELECT USER();" -dbms postgres' % ( user) ), modules.sql.console.WARN_CHECK_CRED)
        
            self.assertRegexpMatches(self._warn(':sql.console %s %s -host notreachable -query "SELECT USER;" -dbms postgres' % ( user, pwd ) ), modules.sql.console.WARN_CHECK_CRED)
            
            self._res(':sql.console %s %s -query "create database asd;" -dbms postgres' % ( user, pwd ))
            
            databases = self._res(':sql.console %s %s -query "SELECT datname FROM pg_database;" -dbms postgres' % ( user, pwd ))          
            self.assertTrue(['asd'] in databases and ['postgres'] in databases )
          
            self._res(':sql.console %s %s -query "drop database asd;" -dbms postgres' % ( user, pwd ))
                      
                      
                      