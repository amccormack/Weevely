#!/usr/bin/env python

from testclasses import TG, TC, TGproc, TCproc
from ConfigParser import ConfigParser


ERR_REQ_NO_BD_RESPONSE = 'No backdoor response from remote side'
PROMPT_PHP_SH = '[$>] '
ERR_NO_SUCH_FILE = 'no such file or directory or permission denied'

testsuites = {
    
    'php' : [ 'php' ],
    'shells' : [ 'php', 'sh'],
    'cwd_ls_safemode' : [ 'ls_safemode', 'cwd_safemode', 'ls', 'cwd' ],
    'cwd_ls' : [ 'ls', 'cwd' ],
    'checks' : [ 'checks' ],
    'rms' : [ 'mkdirs', 'create_file', 'rm' ],
    
}

class TestGroups:

    def __init__(self, confpath):
        
        config = ConfigParser()
        config.read(confpath)
        conf = config._sections['global']
        
        self.TGs = {
        
            'php' : TG(conf,
                [
                TC([ ':shell.php echo(1+1);' ], '2'),
                TC([ ':shell.php echo(1+1)' ], 'trailing semicolon'),
                TC([ ':shell.php echo(1+1); -debug 1' ],'Request.*Response'), 
                TC([ ':shell.php print($_COOKIE);' ],'Array'),            
                TC([ ':shell.php print($_COOKIE); -mode Cookie' ],'Array'),  
                TC([ ':shell.php print($_COOKIE); -mode Referer' ], ERR_REQ_NO_BD_RESPONSE),   
                TC([ ':shell.php echo(1); -debug 1' ], 'print', negate=True), # Check if wrongly do __slacky_probe at every req   
                TC([ ':shell.php echo(2); -precmd print(1);' ],'12'),     
                TC([ ':shell.php -post "{ \'FIELD\':\'VALUE\' }" echo($_POST[\'FIELD\']);' ],'VALUE'),   
                ]),

            'sh' : TG(conf,
                [
                TC([ ':shell.sh echo $((1+1))' ], '2'),
                TC([ 'echo $((1+1))' ], '2'),
                TC([ ':shell.sh "echo $((1+1))" -vector shell_exec' ], '2'),
                TC([ ':shell.sh \'(echo "VISIBLE" >&2)\' -stderr' ], 'VISIBLE\r\n'),
                TC([ ':shell.sh \'(echo "INVISIBLE" >&2)\'' ], 'INVISIBLE\r\n', negate=True),
                
                ]),

  
            'cwd_safemode' : TG(conf,
                [
                TC([ 'cd unexistant' ], ERR_NO_SUCH_FILE),       
                TC([ 'cd ..' ], ERR_NO_SUCH_FILE),       
                ]),
  
            'ls_safemode' : TG(conf,
                [
                TC([ 'ls unexistant' ], ERR_NO_SUCH_FILE),       
                TC([ 'ls /' ], ERR_NO_SUCH_FILE),    
                TC([ 'ls /tmp/' ], ERR_NO_SUCH_FILE),    

                ]),
                    

            'cwd' : TG(conf,
                [    

                TC([ 'cd %s' % conf['existant_base_dir'] ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),     
                TC([ 'cd %s' % conf['existant_base_4_lvl_subdirs'] ], '%s/%s .*%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'], PROMPT_PHP_SH)),       
                TC([ 'cd ..' ], '%s/%s .*%s' % (conf['existant_base_dir'], '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:-1]), PROMPT_PHP_SH)),       
                TC([ 'cd ..' ], '%s/%s .*%s' % (conf['existant_base_dir'], '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:-2]), PROMPT_PHP_SH)),       
                TC([ 'cd ..' ], '%s/%s .*%s' % (conf['existant_base_dir'], '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:-3]), PROMPT_PHP_SH)),       
                TC([ 'cd ..' ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),      

                TC([ 'cd %s' % conf['existant_base_dir'] ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),     
                TC([ 'cd %s' % conf['existant_base_4_lvl_subdirs'] ], '%s/%s .*%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'], PROMPT_PHP_SH)),       
                TC([ 'cd .././/../..//////////////./../../%s/' % conf['existant_base_dir'] ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),       

                
                ]),
  
            'ls' : TG(conf,
                [
                TC([ 'ls %s' % conf['existant_base_dir'] ], '\.\r\n\.\.\r\n%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[0], PROMPT_PHP_SH)),     
                TC([ 'cd %s' % conf['existant_base_dir'] ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % conf['existant_base_4_lvl_subdirs'].split('/')[0] ], '\.\r\n\.\.\r\n%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[1], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:2]) ], '\.\r\n\.\.\r\n%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[2], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:3]) ], '\.\r\n\.\.\r\n.*%s' % (PROMPT_PHP_SH)),     
                TC([ 'ls %s/.././/../..//////////////./../../%s/' % (conf['existant_base_4_lvl_subdirs'], conf['existant_base_4_lvl_subdirs'].split('/')[0])  ],  '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),     

                ]),

                    
                'checks' : TG(conf,
                [
                TC([ ':file.check unexistant exists' ], 'False'),
                TC([ ':file.check %s read' % conf['existant_base_dir'] ], 'True'),
                TC([ ':file.check %s exec' % conf['existant_base_dir'] ], 'True'),
                TC([ ':file.check %s isfile' % conf['existant_base_dir'] ], 'False'),
                TC([ ':file.check %s exists' % conf['existant_base_dir'] ], 'True'),
                TC([ ':file.check %s' % conf['existant_base_dir'] ], 'usage'),
                ]),


               'mkdirs' : TG(conf,
                [
                TC([ 'mkdir -p %s/%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/%s isdir' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], 'True'),      
                ]),


               'create_file' : TG(conf,
                [
                TC([ ':set shell.php debug=1' ], PROMPT_PHP_SH),      
                TC([ ':shell.php file_put_contents(\\"%s/%s/newfile\\", \\"1\\");' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], PROMPT_PHP_SH),      
                TC([ ':shell.php file_put_contents(\\"%s/newfile\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':shell.php file_put_contents(\\"%s/newfile1\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/%s/newfile exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], 'True'),
                TC([ ':file.check %s/newfile exists' % (conf['existant_base_dir']) ], 'True'),
                TC([ ':file.check %s/newfile1 exists' % (conf['existant_base_dir']) ], 'True'),
                TC([ ':file.check %s/%s/newfile write' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], 'True'),
                TC([ ':file.check %s/newfile1 write' % (conf['existant_base_dir']) ], 'True'),
                ]),
                    
                    
                'rm' : TG(conf,
                [
                TC([ ':file.rm unexistant' ], ERR_NO_SUCH_FILE),
                # Delete a single file
                TC([ ':file.rm %s/newfile' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
                TC([ ':file.check %s/newfile exists' % (conf['existant_base_dir']) ], 'False'),
                
                # Delete a single file recursively
                TC([ ':file.rm %s/newfile1 -recursive' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),
                TC([ ':file.check %s/newfile1 exists' % (conf['existant_base_dir']) ], 'False'),               
                
                # Try to delete dir tree without recursion
                TC([ ':file.rm %s/%s ' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'True'), 
                
                # Delete dir tree with recursion
                
                TC([ ':file.rm %s/%s -recursive' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], PROMPT_PHP_SH),
                TC([ ':file.check %s/%s exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0]) ], 'False'), 
                                
                ]),
                
                # TODO: il set stderr shell.sh non sta funzionado
                # differenziare il _output (e' sempre il valore di ritorno o anche l'output di errore? differenziarli
  
        }
