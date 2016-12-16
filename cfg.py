import os
import json

class Config(object):
    def __init__(self):
        filePath = os.path.realpath(__file__)
        dirPath = os.path.dirname(filePath)
        baseDir = os.path.split(dirPath)[0]
        self.configDir = os.path.join(baseDir, 'config')
        env = os.environ['NODE_ENV']
        env = env if env in ['development', 'staging', 'production'] else 'development'
        configFilePath = '/node/config.json'
        self.configFile = os.path.join(self.configDir, envDir, configFilePath)

        with open(self.configFile) as configJSON:
            self.cfg = json.load(configJSON)

    def get(self, key=None):
        if key is None:
            return self.cfg
        if key in config:
            return self.cfg[key]
        return {}
