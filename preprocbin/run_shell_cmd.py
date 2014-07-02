"""
utility functions to run shell commands
Adapted from Russell Poldrack's (poldrack/python) GitHub repository
"""

import subprocess

def run_shell_cmd(cmd,filename,echo=True,cwd=[]):

    """ run a command in the shell using Popen
    """
    stdout_holder=[]
    if cwd:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,cwd=cwd)
    else:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    # Taku addition, write out to file:
    newtext = open(filename, 'a')
    for line in process.stdout:
        newtext.write(line.strip() + '\n')
        if echo:
            print line.strip()
        stdout_holder.append(line.strip())
    newtext.close()
    process.wait()
    return stdout_holder

def run_logged_cmd(cmd,cmdfile):
        outfile=open(cmdfile,'a')
        subcode=cmdfile.split('/')[-2]
        outfile.write('\n%s: Running:'%subcode+cmd+'\n')
        p = subprocess.Popen(cmd.split(' '),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, errors = p.communicate()
        outfile.write('%s: Output: '%subcode+output+'\n')
        if errors:
            outfile.write('%s: ERROR: '%subcode+errors+'\n')
            print '%s: ERROR: '%subcode+errors
        outfile.close()
