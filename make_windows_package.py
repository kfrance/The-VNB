import os
import shutil

os.system("python setup.py py2exe")
shutil.copytree(r"c:\gtk\share\themes", r'dist\share\themes')
shutil.copytree(r"c:\gtk\lib\gtk-2.0\2.10.0\engines", r'dist\lib\gtk-2.0\2.10.0\engines')
shutil.copyfile(r"c:\gtk\gtk2_prefs.exe", r'dist\gtk2_prefs.exe')
