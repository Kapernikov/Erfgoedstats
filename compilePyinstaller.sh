#!/bin/bash
##
# This script builds a linux one-file executable package (might
# also work for MacOS).
# You need to download and extract pyinstaller in the pyinstaller
# folder.
# Known to work with python 2.6
# Will compress the distributable with UPX if it is installed.
##

pushd pyinstaller

if [[ -e erfgoedstats/dist ]]; then
	rm -R -f erfgoedstats/dist
fi
mkdir erfgoedstats/dist

python Configure.py

python Makespec.py --onefile --windowed --upx --name=erfgoedstats ../src/NewGUI.py

python Build.py erfgoedstats/erfgoedstats.spec

if [[ ! -e ../dist ]]; then
	mkdir ../dist
fi

cp erfgoedstats/dist/erfgoedstats ../dist

popd
