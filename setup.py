#!/usr/bin/env python

from distutils.core import setup

import sys
import os
import shutil

command = sys.argv[1] if len(sys.argv) >= 2 else ""
is_build = command.startswith("build") or command.startswith("install") or command.startswith("bdist")

version="3.0.3"

if sys.platform == "win32":
    package_data = {"glfw": ["glfw.dll"]}
    
    # pre-built
    shutil.copyfile("glfw-{}/lib/win32/glfw.dll".format(version), "glfw/glfw.dll")
    
elif sys.platform == "darwin":
    package_data = {"glfw": ["libglfw.dylib"]}
    
    if not os.path.exists("glfw/libglfw.dylib") and is_build:
        # let's cross our fingers and hope the build goes smooth (without user intervention)
        os.chdir("glfw-{}".format(version))
        
        if os.system("make cocoa"):
            print("Error while building libglfw.dylib")
            sys.exit(1)
            
        os.chdir("..")
            
    shutil.copyfile("glfw-{}/lib/cocoa/libglfw.dylib".format(version), "glfw/libglfw.dylib")
        
else:
    package_data = {"glfw": ["libglfw.so"]}
    
    if not os.path.exists("glfw/libglfw.so") and is_build:
        os.chdir("glfw-{}".format(version))
        
        if os.system("make x11"):
            print("Error while building libglfw.so")
            sys.exit(1)
            
        os.chdir("..")
        
    shutil.copyfile("glfw-{}/lib/x11/libglfw.so".format(version), "glfw/libglfw.so")


setup_info = {
    "name": "pyglfw",
    "version": "0.1.0",
    "author": "Orson Peters",
    "author_email": "orsonpeters@gmail.com",
    "url": "http://github.com/nightcracker/pyglfw",
    "description": "GLFW bindings for Python",
    "license": "NC Labs license - BSD-style attribution-only license",
    "classifiers": [
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    "packages": ["glfw", "glfw.ext"],
    "package_data": package_data,
}
    
setup(**setup_info)