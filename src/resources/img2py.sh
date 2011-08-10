#!/bin/sh

echo "#!/usr/bin/python"
FFILE="$@"
echo
echo "# -- converted by img2py.sh"
VARNAME=`basename "$FFILE" | sed -e 's/\..*$//g;' -e 's/-/_/g;' -e 's/\s/_/g;'`
echo "$VARNAME=\\"
echo -n "'''"
convert "$FFILE" gif:- | base64 -e
echo "'''"
