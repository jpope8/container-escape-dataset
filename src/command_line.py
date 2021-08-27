"""
Utility to execute command line processes.
"""

import subprocess
import os
import sys
  
def execute( command ):
    """
    Convenience function for executing commands as though
    from the command line.  The command is executed and the
    results are returned as str list.  For example,
    command = "/usr/bin/git commit -m 'Fixes a bug.'".

    Parameters
    ----------
    command : str
        command with single space between terms
    
    Return
    ------ 
    list of the output : str
    """

    args = command.split()
  
    # using the Popen function to execute the
    # command and store the result in temp.
    # it returns a tuple that contains the 
    # data and the error if any.
    outputStreams = subprocess.Popen(args, stdout = subprocess.PIPE)
      
    # we use the communicate function
    # to fetch the output
    stdout_data, stderr_data = outputStreams.communicate()

    # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
    # communicate() returns a tuple (stdout_data, stderr_data)
    #print('stdout_data: ' + str( stdout_data ) )
    #print('stderr_data: ' + str( stderr_data ) )
      
    # splitting the output so that
    # we can parse them line by line
    output = stdout_data.split("\n")
  
    # a variable to store the output
    result = []
  
    # iterate through the output
    # line by line
    for line in output:
        #print('LINE: ' + line)
        result.append(line)
    
    return result

#
# Test main function
#
def main():
    command = sys.argv[1]

    result = execute(command)
    for line in result:
        print(line)


if __name__ == '__main__':
    main()
