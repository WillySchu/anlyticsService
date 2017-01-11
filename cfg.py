import os
import json

# Config class gets access to proper config information
# it makes it 'gettable' by defining the standard __getitem__ method
class Config(object):
    # finds path to config repo on init and gets appropriate config file
    # for the environment
    def __init__(self):
        try:
            env = os.environ['NODE_ENV']
        except:
            env = 'development'
        self.env = env if env in ['development', 'staging', 'production'] else 'development'

        if self.env == 'development':
            configDir = '/home/ubuntu/Dropbox/code/local/config'
        else:
            configDir = '/home/ubuntu/config'

        configFilePath = 'node/config.json'
        self.configFile = os.path.join(configDir, self.env, configFilePath)

        with open(self.configFile) as configJSON:
            self.cfg = json.load(configJSON)['env'][self.env]

    def __getitem__(self, key):
        if key in self.cfg:
            return self.cfg[key]
        return {}
