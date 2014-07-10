#Taku Ito
#05/19/2014
#Main objects for pypreproc
from run_shell_cmd import run_shell_cmd

class Command():
    """
    The building block of this framework.  
    This object interfaces with the command line and runs it's input to the terminal.
    """
    def __init__(self, input=None, output=None, logname=None, pwd=None):
        self.input = input
        self.output = output
        self.logname = logname
        self.pwd = pwd

    def input(self, input):
        self.input = input
        return self.input

    def output(self, output):
        self.output
        return self.output

    def changeLogname(self, logname):
        self.logname = logname
        return self.logname

    def run(self):
        print 'Running:', self.input
        run_shell_cmd(self.input, self.logname, cwd=self.pwd)


class ExecuteBlock():
    def __init__(self, commands = [], comments = []):
        self.commands = commands
        # self.name = name #name of the execute block (e.g., Preparing MPRAGES)

    def showCommands(self):
        commands = {}
        for num in range(len(self.commands)):
            commands[num] =  self.commands[num].input
        return commands

    def addCommand(self, command):
        self.commands.extend(command)
        return self.commands

    def delCommand(self, commandIndex):
        del self.commands[commandIndex]
        return self.commands

    def run(self):
        for command in self.commands:
            command.run()


class Pipeline():
    def __init__(self, blocks=[], name=None):
        self.blocks = blocks #list of blocks
        self.name = name #string

    def addBlock(self, block):
        self.blocks.extend(block)
        return self.blocks

    def delBlock(self, blockIndex):
        del self.blocks[blockIndex]
        return self.blocks

    def run(self):
        for block in self.blocks:
            block.run()







