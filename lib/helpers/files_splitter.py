import os 

separator = '\n'

class FilesSplitter():
    split = '/split_'
    
    def __init__(self, file, processes):
        self.file = file
        self.filename = os.path.basename(file)
        self.dir = os.path.dirname(self.file)
        self.size = os.path.getsize(self.file) / processes + 1

    def fplit(self):
        self.splitted_files = []
        f = open(self.file, "r")
        number = 0
        actual = 0 
        while 1:
            prec = actual
            f.seek(self.size, os.SEEK_CUR)
            s = f.readline()
            while s and s != separator:
                s = f.readline()
            actual = f.tell()
            temp = open(self.file, "r")
            temp.seek(prec)
            copy = temp.read(actual - prec)
            temp.close()
            new_file = self.dir + self.split + self.filename + str(number)
            self.splitted_files.append(new_file)
            open(new_file, 'w').write(copy)
            number +=1 
            if not s:
                break


if __name__ == "__main__":
    import sys
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read("../../etc/bgp-ranking.conf")
    file = '/home/raphael/bgp-ranking/var/raw_data/bgp/bview'
    fs = FilesSplitter(file, int(config.get('routing','processes_push')))
    fs.fplit()
