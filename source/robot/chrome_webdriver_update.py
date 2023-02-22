from genericpath import isfile
import sys
import os
import urllib.request
from sys import platform
from pathlib import Path


def get_platform_filename():
    filename = ''
    is_64bits = sys.maxsize > 2**32
    if platform == "linux" or platform == "linux2":
        # linux
        filename += 'linux'
        filename += '64' if is_64bits else '32'
    elif platform == "darwin":
        # OS X
        filename += 'mac64'
    elif platform == "win32":
        # Windows...
        filename += 'win32'
    filename += '.zip'
    return filename

def extract_version(output):
    try:
        google_version = ''
        for letter in output[output.rindex('DisplayVersion    REG_SZ') + 24:]:
            if letter != '\n':
                google_version += letter
            else:
                break
        return(google_version.strip())
    except TypeError:
        return

def get_chrome_version():
    version = None
    install_path = None
    try:
        if platform == "linux" or platform == "linux2":
            # linux
            install_path = "/usr/bin/google-chrome"
        elif platform == "darwin":
            # OS X
            install_path = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
        elif platform == "win32":
            # Windows...
            stream = os.popen('reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"')
            output = stream.read()
            version = extract_version(output)
    except Exception as ex:
        print(ex)
    version = os.popen(f"{install_path} --version").read().strip('Google Chrome ').strip() if install_path else version
    return version


chrome_version = get_chrome_version() 
cwd = os.getcwd()
cache_path = os.path.join(cwd, r'c:\chromedriver', str(chrome_version.split('.')[0]))
cache_name = os.path.join(cache_path, r'chromedriver.exe' )

def clear_cache(): 
    os.remove(cache_name)

def download_driver(repo_url):
    try:
        if isfile(cache_name):
            return cache_name
        Path(cache_path).mkdir(parents=True, exist_ok=True)
        driver_url = repo_url.format(version=chrome_version.split('.')[0])
        print('Downloading ' + driver_url)
        urllib.request.urlretrieve(driver_url, cache_name)
        return cache_name
    except Exception as e:
        print('Unable to locate driver binary or dowload the file')
        raise e        