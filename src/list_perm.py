# importing libraries
import subprocess
import os
  
# a function to list the files in
# the current directory and 
# parse the output.
def list_command(args = '-l'):
  
    # the ls command
    cmd = 'ls'
  
    # using the Popen function to execute the
    # command and store the result in temp.
    # it returns a tuple that contains the 
    # data and the error if any.
    temp = subprocess.Popen([cmd, args], stdout = subprocess.PIPE)
      
    # we use the communicate function
    # to fetch the output
    output = str(temp.communicate())
    
    # splitting the output so that
    # we can parse them line by line
    output = output.split("\n")
      
    output = output[0].split('\\')
  
    # a variable to store the output
    res = []
  
    # iterate through the output
    # line by line
    for line in output:
        res.append(line)
  
    # print the output
    for i in range(1, len(res) - 1):
        print(res[i])
  
    return res
  
# parse the output of the ls 
# command and fetch the permissions
# of the files and store them in 
# a text file .
def get_permissions():
  
    # get the output of the 
    # list command
    res = list_command('-l')
  
    permissions = {}
      
    # iterate through all the rows
    # and retrieve the name of the file
    # and its permission.
    for i in range(1, len(res) - 1):
        line = res[i]
  
        line = line.split(' ')
  
        folder_name = line[len(line) - 1]
        permission_value = line[0]
  
        permissions[folder_name] = permission_value
  
    # create a directory called
    # outputs to store the output files
    try:
        os.mkdir('outputs')
  
    except:
  
        pass
  
    os.chdir('outputs')
  
    # open the output file
    out = open('permissions.txt', 'w')
  
    out.write('Folder Name   Permissions\n\n')
  
    # write to the output file
    for folder in permissions:
  
        out.write(folder + ' : ' + permissions[folder] + '\n')
  
    os.chdir('..')
    return permissions
  
if __name__ == '__main__':
    list_command('-al')
