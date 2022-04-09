import clock_cli, clock_gui
from sys import argv

if __name__=="__main__":
    if len(argv) > 1 and argv[1] in ('c', 'cli'):
        clock_cli.main()
    else:
        clock_gui.main()

