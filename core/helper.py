from core.prettytable import PrettyTable



class Helper:
    
    def _format_presentation(self):
        
        presentation_output = banner + presentation 
        return presentation_output
    
    def _format_grouped_helps(self, oneline=False):
        
        table = PrettyTable(['module', 'description'])
        table.align = 'l'
        for groupname in self.modhandler.modules_names_by_group.keys():
            for module in self.modhandler.modules_names_by_group[groupname]:
                
                table.add_row([ ':%s' % self.modhandler.load(module).name, self.modhandler.load(module).argparser.description])
            
        return '%s\n' % table.get_string() 
        
    def _format_helps(self, modules = [], summary_type=0):
 
        if summary_type == 1:
            format_tuple = (False, False, True, True, True, 0)
        else:
            format_tuple = ()
                
        help_output = ''
        for modname in modules:
            help_output += self.modhandler.load(modname).format_help(*format_tuple)
        
        return help_output
    
    

banner = '''      ________                      __
     |  |  |  |-----.----.-.--.----'  |--.--.
     |  |  |  |  -__| -__| |  | -__|  |  |  |
     |________|_____|____|___/|____|__|___  | v1.0
                                      |_____|
              Stealth tiny web shell
'''

usage = '''
[+] Start ssh-like terminal session
    weevely <url> <password>

[+] Run command directly from command line
    weevely <url> <password> [ "<command> .." | :<module> .. ]  

[+] Generate PHP backdoor
    weevely generate <password> [ <path> ] ..

[+] Show credits
    weevely credits
'''

credits = '''
Website
                   http://epinna.github.com/Weevely/

Author
                   Emilio Pinna
                   http://disse.cting.org

Contributors
           Andrea Cardaci
           http://cyrus-and.github.com/
                   Raffaele Forte, Backbox Linux
                   http://www.backbox.org
                   Simone Margaritelli
                   http://www.evilsocket.net/
'''

presentation = '''
[+] Welcome to Weevely. Browse filesystem and execute system commands.
[+] Use ':help' to list available modules and run selected one.

'''