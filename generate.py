from simple_generator import SimpleGenerator

import sys


if __name__ == "__main__":
    print(SimpleGenerator.FromArgs(int(sys.argv[1]), sys.argv[2:]).code)
