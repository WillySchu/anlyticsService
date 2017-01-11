from setuptools import setup

setup(name='analyticsService',
    version='0.0',
    description='A python data analytics service.',
    url='http://github.com/willyschu/anlyticsService',
    author='WillySchu',
    author_email='willjschumacher@gmail.com',
    packages=['analytics'],
    install_requires=['arrow', 'pytest', 'redis'])
