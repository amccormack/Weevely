from core.module import Module
from core.moduleexception import ModuleException, ProbeException
from core.storedargparse import StoredArgumentParser as ArgumentParser
import re

WARN_NO_DATA = 'No data returned'
WARN_CHECK_CRED = 'check credentials and dbms availability'
WARN_FALLBACK = 'bad credentials, falling back to default ones'

class Console(Module):
    '''Run SQL console or execute single queries'''
    
    def _set_vectors(self):
        
        self.support_vectors.add_vector('mysql', 'shell.php', ["""if(mysql_connect("$host","$user","$pass")){
$result = mysql_query("$query"); if($result) {
while ($content = mysql_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
mysql_close();}""" ])
        self.support_vectors.add_vector('mysql_fallback', 'shell.php', [ """$result = mysql_query("$query");
if($result) {
while ($content = mysql_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}"""]),
        self.support_vectors.add_vector('pg', 'shell.php', ["""if(pg_connect("host=$host user=$user password=$pass")){
$result = pg_query("$query"); if($result) {
while ($content = pg_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
pg_close();}""" ]),
        self.support_vectors.add_vector('pg_fallback', 'shell.php', [ """$result = pg_query("$query");
if($result) {
while ($content = pg_fetch_row($result)) {
foreach($content as $key => $value){echo $value . "|";} echo "\n";}}
pg_close();"""])
                                                
                             
    

    def _set_args(self):
        self.argparser.add_argument('user', help='SQL username')
        self.argparser.add_argument('pass', help='SQL password')
        self.argparser.add_argument('-host', help='DBMS host or host:port', default='127.0.0.1')
        self.argparser.add_argument('-dbms', help='DBMS', choices = ['mysql', 'postgres'], default='mysql')
        self.argparser.add_argument('-query', help='Execute single query')

    def _init_module(self):
        self.stored_args['vector'] = None
        self.stored_args['prompt'] = 'SQL> '
        
    def _query(self, query):
        
        # Does not re-use fallback vectors
        if self.stored_args['vector'] and not self.stored_args['vector'].endswith('_fallback'):
            vector = self.stored_args['vector']
        else:
            vector = self.args['dbms']
        
        result = self.support_vectors.get(vector).execute({ 'host' : self.args['host'], 'user' : self.args['user'], 'pass' : self.args['pass'], 'query' : query })
        
        if not result:
            
            vector = self.args['dbms'] + '_fallback'
            
            result = self.support_vectors.get(vector).execute({ 'query' : query })
      
            if result:
                
                # First fallback call. Set console
                
                get_current_user = 'SELECT USER;' if self.args['dbms'] == 'postgres' else 'SELECT USER();'
                
                user = self.support_vectors.get(vector).execute({ 'query' : get_current_user })
                
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
                    self._stringify_result()
                    
                print self._output
                    
                
        else:
            self._result = self._query(self.args['query'])

            if self._result == None:
                self.mprint('%s %s' % (WARN_NO_DATA, WARN_CHECK_CRED))