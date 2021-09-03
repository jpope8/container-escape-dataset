"""
Utility to execute command line processes.
"""

import subprocess
import os
import sys
import re
  
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
    #print( 'COMMAND_LINE: ' + str( type(stdout_data) ) )
    #output = stdout_data.split("\n")
    # Issue: python2 stdout_data is a str (or str-like)
    #        python3 stdout_data is bytes and cnnot be directly split
    # Solution: convert to str using decode, check type instead of version check
    # NB: If not done correctly the system logging fails and pollutes the audit log!!!
    #     type=SYSCALL msg=audit(1630261099.364:78511): arch=40000003 syscall=295 success=no exit=-13
    #         ... comm="python3" exe="/usr/bin/python3.7" subj==unconfined key="access"
    #     type=CWD msg=audit(1630261099.364:78511): cwd="/home/pi/container-escape-dataset/src"
    # 
    #output = re.split('\n', str(stdout_data) )
    output = None
    #print( 'COMMAND_LINE: ' + str(type(stdout_data)) )
    if( isinstance(stdout_data, str) ):
        # this is python2 behaviour, stdout_data is str
        output = stdout_data.split("\n")
    else:
        # this is python3 behaviour, stdout_data is bytes
        output = re.split('\n', stdout_data.decode('utf-8') )
  
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
