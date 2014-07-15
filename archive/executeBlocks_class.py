# Example of what the pipeline would like with nodes as classes, rather than functions
# 07/10/2014

from run_shell_cmd import run_shell_cmd

class Block():
    """
    A general purpose pipeline node, that can consist of a group of commands (typically in AFNI) or even just a single command.
    Parameters:
        - a config file (i.e., a YAML file)
        - a text file (or maybe a bash script) that consists of the AFNI commands (and comments, if needed) in plain text (no Python overhead)
    """

    # Class constructor
    def __init__(self, conf, file, strcommand=False):
        # Make the conf file an object attribute
        self.conf = conf

        if strcommand==True:
            self.commands = file
        else:
            # Parse the txt file into a list of commands
            newtext = open(file, 'r')
            self.commands = newtext.readlines()

    def run(self):
        # Function to run the block
        for line in self.commands:
            if not line.startswith('#'):
                run_shell_cmd(line, conf.logname)


class Pipeline():
    """
    A general purpose pipline, where you can add/remove blocks as needed
    """

    # Class constructor
    def __init__(self, conf, blocks):
        # Note, 'blocks' is a list of 'Block' class objects.
        self.conf = conf
        self.blocks = blocks
        # note, since self.blocks is a list, no need for add/remove methods for this class since you can just use native add/remove methods on lists.
    

    def runAll(self):
        # runs all blocks serially (for each subj, ideally)
        for block in self.blocks:
            block.run()

3dresample = Block(conf, '3drresample -op')
3dressample.run()
# NOTE! Would need one more class one level more abstract than 'Pipeline' class, to handle parallel processing of all subjects.  this abstracted class would instantiate all subject pipelines (given the config file) and run them in parallel using multiprocessing package.

# Example case:


"""
Things to  consider (and potential problems) regarding this approach:
    1. Would variables be written/indicated in bash or Python?
    2. If written in bash, how would the config file detect the variables (aside from parsing out '$' signs in the lines)?
    3. Other potential pitfalls?

    4. One of the things I was considering with this approach is that rather than trying to make certain pipeline blocks (such as 'prepareMPRAGE') more flexible/intuitive to use for different data sets with various parameters is that this would side-step the issue entirely, and require users to know exactly what commands they'd be using. (or they can use templates of previous code, e.g., the original/current activation pipeline)


Possible Advantages:
    1. In terms of overhead code, this is all the code there is (in essence).  We could instantiate certain 'standard' pipelines, that automatically run given a .yaml file.  Otherwise, for special pipelines/preprocessing, you can just create your own customized txt files and write a simple script that puts all the blocks together.
