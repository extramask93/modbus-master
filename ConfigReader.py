import configparser as ConfigParser

class ConfigReader:
    def __init__(self,file):
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(file)
    def GetSectionMap(self,section): 
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
            except:
                print("exception on %s" % option)
                dict1[option] = None
        return dict1
    
