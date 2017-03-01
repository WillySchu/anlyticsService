import subprocess

def git(*args):
    return subprocess.check_output(['git'] + list(args))
