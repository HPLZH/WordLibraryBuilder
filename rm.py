import os
import shutil
import sys


def rm(path: str):
    if os.path.exists(path):
        try:
            if os.path.islink(path) or os.path.isfile(path):
                os.remove(path)
                print("Removed file: " + path, file=sys.stderr)
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print("Removed dir: " + path, file=sys.stderr)
        except Exception as ex:
            print("Failed: " + path, file=sys.stderr)
            print(ex, file=sys.stderr)
    else:
        print("Not found: " + path, file=sys.stderr)


if __name__ == "__main__":
    [rm(p) for p in sys.argv[1:]]
