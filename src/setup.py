'''
Py2Exe setup file
Run this to compile the script into a windows executable

External libraries needed: py2exe
'''

from distutils.core import setup
import py2exe
import shutil
import os

DIST_DIR = "../dist"

if(not os.path.exists(DIST_DIR)):
    os.mkdir(DIST_DIR)

setup(options={'py2exe': {'dist_dir': DIST_DIR}}, windows=['NewGUI.py'], zipfile = None)

# Create folders used by the app
if(not os.path.exists(DIST_DIR+"/../data")):
    os.mkdir(DIST_DIR+"/../data")
if(not os.path.exists(DIST_DIR+"/../data/musea")):
    os.mkdir(DIST_DIR+"/../data/musea")

# Copy necessary files to deploy directory
if(os.path.exists(DIST_DIR+"/html")):
	shutil.rmtree(DIST_DIR+"/html")
if(os.path.exists(DIST_DIR+"/images")):
	shutil.rmtree(DIST_DIR+"/images")
shutil.copytree("html", DIST_DIR+"/html")
shutil.copytree("images", DIST_DIR+"/images")

# Rename main executable
shutil.move(DIST_DIR+"/NewGUI.exe", DIST_DIR+"/erfgoedstats.exe")
