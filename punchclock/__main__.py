from email.policy import default
import clock_cli, clock_gui
from sys import argv
import argparse
from os import path

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gui", action="store_true", help="launch gui app")
    parser.add_argument("-c", "--cli", action="store_true", help="launch command line app")
    parser.add_argument("-u", "--username", help="username")
    parser.add_argument('-d', "--default", help="set default name")
    args = parser.parse_args()
    
    if args.default:
        with open(path.dirname(__file__) + '/punchconfig.py','w') as f:
            #sanitizing input
            default_name = ''.join([x for x in args.default if x != "'"])
            f.write('DEFAULT_NAME = "{}"'.format(default_name))
            f.close()
        print(f"Default name has been set to {default_name}")


    if args.username:
        username = args.username            
    else:
        username = None

    if args.gui and not args.cli:
        clock_gui.main(username)
            
    else:
        clock_cli.main(username)
        
    

    
