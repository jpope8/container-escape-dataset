#!/usr/bin/env python3

# Above matters, we want to execute without pre-prepending python
# This python file needs to be executable also, i.e. chmod +x

import sys
import cpu
import logging
import time

def main():
    # We intend on this running forever
    delay = 15 # time delay in seconds
    while(True):
        try:
            cpu.main()
            time.sleep(delay) # Sleep for delay seconds
        except Exception as e:
            logging.error(traceback.format_exc())


if __name__ == '__main__':
    sys.exit(main())

