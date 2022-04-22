import clock_cli, clock_gui
from sys import argv
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gui", action="store_true", help="launch gui app")
    #parser.add_argument("-c", "--cli", action="store_true" help="launch command line app")
    parser.add_argument("-u", "--username", help="username")
    #parser.add_argument('-d', "--default", help="set default name")
    args = parser.parse_args()
    
    if args.username:
        username = args.username            
    else:
        username = None

    if args.gui:
        clock_gui.main(username)
    else:
        clock_cli.main(username)
        
    

    
