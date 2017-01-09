import os
import json

# Config class gets access to proper config information
# it makes it 'gettable' by defining the standard __getitem__ method
class Config(object):
    # finds path to config repo on init and gets appropriate config file
    # for the environment
    def __init__(self):
        filePath = os.path.realpath(__file__)
        dirPath = os.path.dirname(filePath)
        baseDir = os.path.split(dirPath)[0]
        self.configDir = os.path.join(baseDir, 'config')
        env = os.environ['NODE_ENV']
        env = env if env in ['development', 'staging', 'production'] else 'development'
        configFilePath = 'node/config.json'
        self.configFile = os.path.join(self.configDir, env, configFilePath)

        with open(self.configFile) as configJSON:
            self.cfg = json.load(configJSON)['env'][env]

    def __getitem__(self, key):
        if key in self.cfg:
            return self.cfg[key]
        return {}
