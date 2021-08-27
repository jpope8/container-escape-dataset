"""
Utility functions to automate docker volume maintenance.
"""

import sys
import command_line
import re

def remove( volumeid ):
    result = command_line.execute('sudo docker volume rm ' + volumeid)
    print('RM VOL ' + volumeid)

def removeAll():
    """
    Removes all volumes from docker.  First lists volumes under
    the /var/lib/docket/volume directory and then removes each
    one individually.  All commands are through docker.
    """
    # sudo docker volume ls
    # DRIVER    VOLUME NAME
    # local     562b5d9767842aa8ab9a0974eac4bd2e0cd5df649065688ba18f9d655b6adaaf
    # local     6707f40824093e099e1c0d8de6940ec060c3154b8e9b5cd568e52aeb528cf512
    result = command_line.execute('sudo docker volume ls')
    for volume_listing in result:
        tokens = re.split(' +', volume_listing)
        if(len(tokens) > 1 and 'local' in tokens[0]):
            volumeid = tokens[1]
            remove(volumeid)
#
# Main function
#
def main():
    removeAll()

if __name__ == '__main__':
    main()
