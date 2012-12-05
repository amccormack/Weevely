from baseclasses import SimpleTestCase, conf
from tempfile import NamedTemporaryFile
import random, string
import sys, os
sys.path.append(os.path.abspath('..'))
import modules
from unittest import skipIf

class MySql(SimpleTestCase):
    
    @skipIf(conf['test_only_dbms'] == 'postgres', "Skipping mysql tests")
    def test_query(self):

        
        user = conf['mysql_sql_user']
        pwd = conf['mysql_sql_pwd']
        default_user = conf['mysql_sql_default_user']
        
        self.assertEqual(self._res(':sql.console %s %s -query "SELECT USER();"' % ( user, pwd ) ), [['%s@localhost' % user ]])
        
        self.assertRegexpMatches(self._warn(':sql.console %s wrongpass -query "SELECT USER();"' % ( user) ), modules.sql.console.WARN_FALLBACK)
        self.assertEqual(self._res(':sql.console %s wrongpass -query "SELECT USER();"' % ( user ) ), [['%s@localhost' % default_user ]])
        
        self.assertEqual(self._res(':sql.console %s %s -host notreachable -query "SELECT USER();"' % ( user, pwd ) ), [['%s@localhost' % default_user ]])

        self.assertEqual(self._res(':sql.console %s %s -query "SELECT USER();"' % ( user, pwd ) ), [['%s@localhost' % user ]])
        

        self._res(':sql.console %s %s -query "create database asd;"' % ( user, pwd ))
        
        databases = self._res(':sql.console %s %s -query "show databases;" ' % ( user, pwd ))          
        self.assertTrue(['asd'] in databases and ['information_schema'] in databases )
      
        self._res(':sql.console %s %s -query "drop database asd;" ' % ( user, pwd ))
                      

    @skipIf(conf['test_only_dbms'] == 'postgres', "Skipping mysql tests")
    def test_dump(self):

        user = conf['mysql_sql_user']
        pwd = conf['mysql_sql_pwd']
        
        
        # Standard test
        self.assertRegexpMatches(self._res(':sql.dump %s %s information_schema' % ( user, pwd ) ), "-- Dumping data for table `COLUMNS`")
        self.assertRegexpMatches(self._warn(':sql.dump %s wrongpwd information_schema' % ( user ) ), modules.sql.dump.WARN_NO_DUMP)
             
        # table
        self.assertRegexpMatches(self._res(':sql.dump %s %s information_schema -table TABLES' % ( user, pwd ) ), "-- Dumping data for table `TABLES`")
         
        # vectors
        self.assertRegexpMatches(self._res(':sql.dump %s %s information_schema -vector mysqldump -table TABLES' % ( user, pwd ) ), "-- Dumping data for table `TABLES`")
        self.assertRegexpMatches(self._warn(':sql.dump %s wrongpwd information_schema  -vector mysqldump -table TABLES' % ( user ) ), modules.sql.dump.WARN_NO_DUMP)
             
        self.assertRegexpMatches(self._res(':sql.dump %s %s information_schema -vector mysqlphpdump -table TABLES' % ( user, pwd ) ), "-- Dumping data for table `TABLES`")
        self.assertRegexpMatches(self._warn(':sql.dump %s wrongpwd information_schema  -vector mysqlphpdump -table TABLES' % ( user ) ), modules.sql.dump.WARN_DUMP_INCOMPLETE)

        # lpath
        self.assertRegexpMatches(self._warn(':sql.dump %s %s information_schema -table TABLES -ldump /wrongpath' % ( user, pwd ) ), modules.sql.dump.WARN_DUMP_ERR_SAVING)

        # host
        self.assertRegexpMatches(self._warn(':sql.dump %s %s information_schema -table TABLES -host wronghost' % ( user, pwd ) ), modules.sql.dump.WARN_NO_DUMP)
        

class PGSql(SimpleTestCase):
    
    
    @skipIf(conf['test_only_dbms'] == 'mysql', "Skipping postgres tests")
    def test_query(self):
            
        user = conf['pg_sql_user']
        pwd = conf['pg_sql_pwd']

        self.assertEqual(self._res(':sql.console %s %s -query "SELECT USER;" -dbms postgres' % ( user, pwd ) ), [[ user ]])
        self.assertRegexpMatches(self._warn(':sql.console %s wrongpass -query "SELECT USER();" -dbms postgres' % ( user) ), modules.sql.console.WARN_CHECK_CRED)
    
        self.assertRegexpMatches(self._warn(':sql.console %s %s -host notreachable -query "SELECT USER;" -dbms postgres' % ( user, pwd ) ), modules.sql.console.WARN_CHECK_CRED)
        
        self._res(':sql.console %s %s -query "create database asd;" -dbms postgres' % ( user, pwd ))
        
        databases = self._res(':sql.console %s %s -query "SELECT datname FROM pg_database;" -dbms postgres' % ( user, pwd ))          
        self.assertTrue(['asd'] in databases and ['postgres'] in databases )
      
        self._res(':sql.console %s %s -query "drop database asd;" -dbms postgres' % ( user, pwd ))
                  
                  
                      