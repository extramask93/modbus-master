from Slave import Slave

class SlaveLoader:
    def __init__(self):
        pass
    def LoadFromFile(self, filename):
        addresses = []
        names = []
        delays = []
        slaves = []
        with open(filename) as f:
            lines = f.read().splitlines()
        for line in lines:
            if(line[0] == '|'): #header
                continue
            values = [x.strip() for x in line.split('|')]
            if(len(values)<3):
                print("Error during loading file: %s. Not enaugh parameters in line:\n %s"%(filename,line))
                break
            try:
                if(int(values[0],0) in addresses):
                    print("Error during loading file: %s. Device already exists:\n%s"%(filename,line))
                    break
                addresses.append(int(values[0],0))
                names.append(values[1])
                delays.append(int(values[2]))
            except ValueError:
                print("Error during loading file. Value not convertible to int in line: %s"%(line,))
        for i in range(0,len(addresses)):
            slaves.append(Slave(addresses[i],names[i],delays[i]))
        return slaves
