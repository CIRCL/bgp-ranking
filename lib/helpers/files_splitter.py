import os 

class FilesSplitter():
    """
    This class split a file into a certain number of files. 
    If necessary, it uses a separator to split at the right place 
    and not in the middle of a block.
    
    The splitted are prefixed with split_ and postfixed with their number.
    
    A table of filenames is retourned by "fsplit" 
    """
    split = '/split_'
    
    def __init__(self, file, number_of_files, separator = '\n'):
        """
        Needs a filename to split and the number of file to generate. 
        If the separator between the blocks is not a '\n', you have to 
        give it as argument too.
        """
        self.file = file
        self.separator = separator
        self.filename = os.path.basename(file)
        self.dir = os.path.dirname(self.file)
        self.size = os.path.getsize(self.file) / number_of_files + 1

    def fplit(self):
        """
        Split the file and return the list of filenames.
        """
        self.splitted_files = []
        f = open(self.file, "r")
        number = 0
        actual = 0 
        while 1:
            prec = actual
            # Jump of "size" from the current place in the file
            f.seek(self.size, os.SEEK_CUR)
            s = f.readline()
            while s and s != self.separator:
                # find the next separator
                s = f.readline()
            # Get the current place
            actual = f.tell()
            # Create the new file
            temp = open(self.file, "r")
            temp.seek(prec)
            # Get the text we want to put in the new file
            copy = temp.read(actual - prec)
            temp.close()
            new_file = self.dir + self.split + self.filename + str(number)
            self.splitted_files.append(new_file)
            # Write the new file
            open(new_file, 'w').write(copy)
            number +=1 
            if not s:
                # End of file
                break
        return self.splitted_files


if __name__ == "__main__":
    import sys
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read("../../etc/bgp-ranking.conf")
    file = '/home/raphael/bgp-ranking/var/raw_data/bgp/bview'
    fs = FilesSplitter(file, int(config.get('routing','processes_push')))
    print fs.fplit()
