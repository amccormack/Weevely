from baseclasses import SimpleTestCase, conf
from tempfile import NamedTemporaryFile
import random, string
import sys, os
sys.path.append(os.path.abspath('..'))
import modules

class BruteSQL(SimpleTestCase):
    
    def _generate_wordlist(self, insert_word = ''):
        wordlist = [''.join(random.choice(string.ascii_lowercase) for x in range(random.randint(1,100))) for x in range(random.randint(1,200)) ]
        if insert_word:
            wordlist[random.randint(0,len(wordlist)-1)] = insert_word
        return wordlist
        
    
    def test_brutesql(self):

        expected_match = [ conf['sql_user'], conf['sql_pwd'] ]
        dbms = conf['sql_dbms']
        self.assertEqual(self._res(':bruteforce.sql %s -wordlist "%s" -dbms %s' % (conf['sql_user'], str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        
        temp_path = NamedTemporaryFile(); 
        temp_path.write('\n'.join(self._generate_wordlist(conf['sql_pwd'])))
        temp_path.flush() 
        
        self.assertEqual(self._res(':bruteforce.sql %s -wordfile "%s" -dbms %s' % (conf['sql_user'], temp_path.name, dbms)), expected_match)
        self.assertRegexpMatches(self._warn(':bruteforce.sql %s -wordfile "%sunexistant" -dbms %s' % (conf['sql_user'], temp_path.name, dbms)), modules.bruteforce.sql.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':bruteforce.sql %s' % (conf['sql_user'])), modules.bruteforce.sql.WARN_NO_WORDLIST)
        
        self.assertEqual(self._res(':bruteforce.sql %s -chunksize 1 -wordlist "%s" -dbms %s' % (conf['sql_user'], str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        self.assertEqual(self._res(':bruteforce.sql %s -chunksize 100000 -wordlist "%s" -dbms %s' % (conf['sql_user'], str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        self.assertEqual(self._res(':bruteforce.sql %s -chunksize 0 -wordlist "%s" -dbms %s' % (conf['sql_user'], str(self._generate_wordlist(conf['sql_pwd'])),dbms)), expected_match)
        
        wordlist = self._generate_wordlist() + [ conf['sql_pwd'] ]
        self.assertEqual(self._res(':bruteforce.sql %s -wordlist "%s" -dbms %s -startline %i' % (conf['sql_user'], str(wordlist), dbms, len(wordlist)-1)), expected_match)
        self.assertRegexpMatches(self._warn(':bruteforce.sql %s -wordlist "%s" -dbms %s -startline %i' % (conf['sql_user'], str(wordlist), dbms, len(wordlist)+1)), modules.bruteforce.sql.WARN_STARTLINE)
        
        
        temp_path.close()

    def test_brutesqlusers(self):

        expected_match = { conf['sql_user'] : conf['sql_pwd'] }
        dbms = conf['sql_dbms']
        self.assertEqual(self._res(':bruteforce.sqlusers -wordlist "%s" -dbms %s' % ( str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        
        temp_path = NamedTemporaryFile(); 
        temp_path.write('\n'.join(self._generate_wordlist(conf['sql_pwd'])))
        temp_path.flush() 
        
        self.assertEqual(self._res(':bruteforce.sqlusers -wordfile "%s" -dbms %s' % ( temp_path.name, dbms)), expected_match)
        self.assertRegexpMatches(self._warn(':bruteforce.sqlusers -wordfile "%sunexistant" -dbms %s' % ( temp_path.name, dbms)), modules.bruteforce.sql.WARN_NO_SUCH_FILE)
        self.assertRegexpMatches(self._warn(':bruteforce.sqlusers '), modules.bruteforce.sql.WARN_NO_WORDLIST)
        
        self.assertEqual(self._res(':bruteforce.sqlusers -chunksize 1 -wordlist "%s" -dbms %s' % ( str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        self.assertEqual(self._res(':bruteforce.sqlusers -chunksize 100000 -wordlist "%s" -dbms %s' % ( str(self._generate_wordlist(conf['sql_pwd'])), dbms)), expected_match)
        self.assertEqual(self._res(':bruteforce.sqlusers -chunksize 0 -wordlist "%s" -dbms %s' % ( str(self._generate_wordlist(conf['sql_pwd'])),dbms)), expected_match)
        
        wordlist = self._generate_wordlist() + [ conf['sql_pwd'] ]
        self.assertEqual(self._res(':bruteforce.sqlusers -wordlist "%s" -dbms %s -startline %i' % ( str(wordlist), dbms, len(wordlist)-1)), expected_match)
        self.assertRegexpMatches(self._warn(':bruteforce.sqlusers  -wordlist "%s" -dbms %s -startline %i' % ( str(wordlist), dbms, len(wordlist)+1)), modules.bruteforce.sql.WARN_STARTLINE)
        
        
        temp_path.close()
        
        