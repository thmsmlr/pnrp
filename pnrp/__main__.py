import sys
import riri

if __name__ == '__main__':
    [_, fpath, *args] = sys.argv
    riri.cli(fpath, args)
