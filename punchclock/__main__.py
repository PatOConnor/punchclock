import clock_cli, clock_gui
from sys import argv

if __name__=="__main__":
    if len(argv) > 1 and argv[1] in ('g', 'gui'):
        clock_gui.main()
    else:
        clock_cli.main()

