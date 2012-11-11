#!/usr/bin/env python

from testclasses import TG, TC, TGproc, TCproc
from ConfigParser import ConfigParser
from random import choice
from string import ascii_lowercase


ERR_REQ_NO_BD_RESPONSE = 'No backdoor response from remote side'
ERR_NO_SUCH_FILE = 'no such file or directory or permission denied'
PROMPT_PHP_SH = '(?:(?:PHP >)|\$)'
JUST_PROMPT = '\r\n[\S\ ]+' + PROMPT_PHP_SH


testsuites = {
    
    'php' : [ 'php' ],
    'shells' : [ 'php', 'sh', 'info'],
#    'cwd_ls_safemode' : [ 'ls_safemode', 'cwd_safemode', 'ls', 'cwd' ],
    'cwd_ls' : [ 'mkdirs', 'ls', 'cwd' ],
    'checks' : [ 'mkdirs', 'create_file', 'checks' ],
    'rms' : [ 'mkdirs', 'create_file', 'rm' ],
    'finds' : [ 'mkdirs', 'create_file', 'perms_safemode', 'webdir' ],
    'download_read' : [ 'download', 'read' ],
    'upload' : [ 'upload' ],
    
}

class TestGroups:

    def __init__(self, confpath):
        
        config = ConfigParser()
        config.read(confpath)
        conf = config._sections['global']
        
        randomstring = ''.join(choice(ascii_lowercase) for x in range(4))

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
                TC([ 'ls %s' % conf['existant_base_dir'] ], '(?:\.\r\n\.\.\r\n)?%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[0], PROMPT_PHP_SH)),     
                TC([ 'cd %s' % conf['existant_base_dir'] ], '%s .*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % conf['existant_base_4_lvl_subdirs'].split('/')[0] ], '(?:\.\r\n\.\.\r\n)?%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[1], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:2]) ], '(?:\.\r\n\.\.\r\n)?%s.*%s' % (conf['existant_base_4_lvl_subdirs'].split('/')[2], PROMPT_PHP_SH)),     
                TC([ 'ls %s' % '/'.join(conf['existant_base_4_lvl_subdirs'].split('/')[:3]) ], '(?:\.\r\n\.\.\r\n)?.*%s' % (PROMPT_PHP_SH)),     
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
                TC([ ':file.check %s/newfile md5' % conf['existant_base_dir'] ], 'c4ca4238a0b923820dcc509a6f75849b'),
                
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
                TC([ ':file.check %s/%s/newfile exists' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], 'True'),
                TC([ ':file.check %s/%s/newfile write' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']) ], 'True'),

                TC([ ':shell.php file_put_contents(\\"%s/newfile\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/newfile exists' % (conf['existant_base_dir']) ], 'True'),
                
                TC([ ':shell.php file_put_contents(\\"%s/newfile1\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/newfile1 exists' % (conf['existant_base_dir']) ], 'True'),
                
                TC([ ':shell.php file_put_contents(\\"%s/newfile2\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/newfile2 exists' % (conf['existant_base_dir']) ], 'True'),

                TC([ ':shell.php file_put_contents(\\"%s/newfile3\\", \\"1\\");' % (conf['existant_base_dir']) ], PROMPT_PHP_SH),      
                TC([ ':file.check %s/newfile3 exists' % (conf['existant_base_dir']) ], 'True'),
                
                
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
                    
                # VECTORS
                TC([ ':set shell.php debug=1' ], PROMPT_PHP_SH),  
                
                # Delete with php_rmdir vector
                TC([ ':file.rm %s/newfile2 -vector php_rmdir' % (conf['existant_base_dir']) ], "function rrmdir"),
                TC([ ':file.check %s/newfile2 exists' % (conf['existant_base_dir']) ], 'False'),
                
                # Delete with rm vector
                TC([ ':file.rm %s/newfile3 -vector rm -recursive' % (conf['existant_base_dir']) ], 'rm -rf %s' % (conf['existant_base_dir'])),
                TC([ ':file.check %s/newfile3 exists' % (conf['existant_base_dir']) ], 'False'),
                               
                ]),


               'info' : TG(conf,
                [
                TC([ ':system.info' ], '\+-+\+.*safe_mode.*\+-+\+'),      
                TC([ ':system.info os' ], '%s\r\n.*%s' % (conf['remote_os'], PROMPT_PHP_SH)),     
                ]),



               'perms' : TG(conf,
                [
                TC([ ':find.perms' ], '%s.*%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),
                TC([ ':find.perms -vector find' ], '%s.*%s/newfile' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),         
                TC([ ':find.perms -vector php_recursive' ], '%s.*%s/newfile' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),         
                
                # Find only file
                TC([ ':find.perms -vector find -type f' ], '%s.*%s/newfile' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),         
                TC([ ':find.perms -vector php_recursive -type f' ], '%s.*%s/newfile' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),         
                
                ]),
                    
               'perms_safemode' : TG(conf,
                [
                TC([ ':find.perms writable' ], '\r\n%s/%s\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),
                TC([ ':find.perms -vector php_recursive writable' ], '\r\n%s/%s\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),         
                
                # Find first
                TC([ ':find.perms writable -first' ], '\r\n%s\r\n.*%s' % (conf['existant_base_dir'], PROMPT_PHP_SH)),
                
                
                # Find only file
                TC([ ':find.perms writable -type f' ], '\r\n%s/%s\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']), negate=True),   
                TC([ ':find.perms writable -type f' ], '\r\n%s/%s/newfile\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),   
                  
                # Find only dir
                TC([ ':find.perms writable -type d' ], '\r\n%s/%s\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),   
                TC([ ':find.perms writable -type d' ], '\r\n%s/%s/newfile\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs']), negate=True),   
                  
                  
                # Checking attributes (files are not readable)
                TC([ ':find.perms writable -executable -type f' ], '\r\n.*%s' % (PROMPT_PHP_SH)),   
                TC([ ':find.perms writable -readable -type f' ], '\r\n%s/%s/newfile\r\n' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'])),   
                                  
                ]),
                    
               'webdir' : TG(conf,
                [
                TC([ ':find.webdir' ], '/var/www/%s\r\nhttp://localhost/%s' % (conf['existant_base_dir'], conf['existant_base_dir'])),
                TC([ ':find.webdir -rpath writable/w1' ], '/var/www/%s/%s\r\nhttp://localhost/%s/%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0],  conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0])),
                TC([ ':find.webdir -rpath writable/w1/../../writable//w1/' ], '/var/www/%s/%s\r\nhttp://localhost/%s/%s' % (conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0],  conf['existant_base_dir'], conf['existant_base_4_lvl_subdirs'].split('/')[0])),

                ]),

               'download' : TG(conf,
                [
                TC([ ':file.download /etc/gne /tmp/asd' ], ERR_NO_SUCH_FILE),
                TC([ ':file.download /etc/passwd /tmpsakdsa/jhgsd' ], 'Errno'),
                TC([ ':file.download /etc/shadow /tmp/asd' ], ERR_NO_SUCH_FILE), 
                TC([ ':file.download /etc/passwd /tmp/passwd -vector file' ], JUST_PROMPT),
                TC([ ':file.download /etc/passwd /tmp/passwd -vector fread' ], JUST_PROMPT),
                TC([ ':file.download /etc/passwd /tmp/passwd -vector file_get_contents' ], JUST_PROMPT),
                TC([ ':file.download /etc/passwd /tmp/passwd -vector base64' ], JUST_PROMPT),
                TC([ ':file.download /etc/passwd /tmp/passwd -vector copy' ], JUST_PROMPT),
                TC([ ':file.download /etc/passwd /tmp/passwd -vector symlink' ], JUST_PROMPT),
                ]),
               
               'read' : TG(conf,
                [
                TC([ ':file.read /etc/gne' ], ERR_NO_SUCH_FILE),
                TC([ ':file.read /etc/shadow' ], ERR_NO_SUCH_FILE), 
                TC([ ':file.read /etc/passwd -vector file' ], 'root:x:0:0:root:/root:/bin/bash'),
                TC([ ':file.read /etc/passwd -vector fread' ], 'root:x:0:0:root:/root:/bin/bash'),
                TC([ ':file.read /etc/passwd -vector file_get_contents' ], 'root:x:0:0:root:/root:/bin/bash'),
                TC([ ':file.read /etc/passwd -vector base64' ], 'root:x:0:0:root:/root:/bin/bash'),
                TC([ ':file.read /etc/passwd -vector copy' ], 'root:x:0:0:root:/root:/bin/bash'),
                TC([ ':file.read /etc/passwd -vector symlink' ], 'root:x:0:0:root:/root:/bin/bash'),
                ]),

               'upload' : TG(conf,
                [
                TC([ ':file.upload /etc/protocols /tmp/%s1' % randomstring ], JUST_PROMPT),
                TC([ ':file.upload /etc/protocolsA /tmp/%s2' % randomstring ], ERR_NO_SUCH_FILE),
                TC([ ':file.upload /etc/protocols /tmpdsadsasad'  ], 'Error'),
                TC([ ':file.upload /bin/true /tmp/%s4' % randomstring ], 'Error', negate=True),
                ]),
                 
                 
                # TODO: test :set type different from strings are not correctly casted, use ast

        }
