#!/bin/python
# -*- coding: utf-8 -*-

'''
' Tests the behaviour of loading different unicode encoded files
' in python, together with different specified encodings.
'''


# Notice that in the second line of this file I choose the default
# encoding of literals to be UTF-8

import codecs

### UTF-8 input ###

# 1 Without specifying a decoder
# (the default encoder of codecs is probably set to the 
# encoding chosen for the file, which in this case is UTF-8)
# Note: in a unix interactive python terminal, this will probably
# also be UTF-8
f = codecs.open('test-utf8.txt')
a = f.read()
a
print a		# should be correct
			# HOWEVER! note that a is just a str, not a unicode string!!

# 2 With explicit specification of codec
f = codecs.open('test-utf8.txt', encoding="utf-8")
a = f.read()
a
print a		# will certainly be correct
			# a is now a unicode string!!

# 3 When specifying the wrong decoder (latin1)
f = codecs.open('test-utf8.txt', encoding="latin1")
a = f.read()
a
print a		# will have garbled symbols
			# because latin1 uses all 256 possible combinations
			# of char, an error will never be detected

### latin-1 input ###

# 4 without specifying a decoder (will use utf-8 as default)
f = codecs.open('test-latin1.txt')
a = f.read()
a
print a		# special characters are replaced by ? symbols
			# a is a regular str
			
# 5 With explicit specification of codec
f = codecs.open('test-latin1.txt', encoding="latin1")
a = f.read()
a
print a		# is correct!
			# a will be unicode string
			
# 6 With explicit specification of the WRONG codec
f = codecs.open('test-latin1.txt', encoding="utf-8")
a = f.read()
			# WILL THROW ERROR!
			# UnicodeDecodeError: 'utf8' codec can't decode bytes in position 1-6: unsupported Unicode code range
# This is because utf-8 doesn't use all byte combinations, unlike latin-1

# 7 When we use error ignoring:
f = codecs.open('test-latin1.txt', encoding="utf-8", errors="ignore")
a = f.read()
a
print a		# the special characters will be gone
			# a is a unicode string object!
			
# 8 Another strategy is to replace erroneuous characters with a ? symbol
f = codecs.open('test-latin1.txt', encoding="utf-8", errors="replace")
a = f.read()
a
print a		# the special characters will be replaced by ? symbols
			# Note that is the same behaviour when loading latin1 files without specifying codec
			# or error handling. (example 4)
			# This would suggest that errors=replace is the default.
			
			
'TODO: auto detection tests'
