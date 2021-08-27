import sys
import pnrp

if __name__ == '__main__':
    [_, fpath, *args] = sys.argv
    pnrp.cli(fpath, args)
