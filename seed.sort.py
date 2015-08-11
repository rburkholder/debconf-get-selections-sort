#
# author: Raymond Burkholder
#         rburkholder@quovadis.bm
# created: 2015/08/10
#
# license: public domain, keep author/email intact
#
# sorts and collates debconf output:
#  debconf-get-selections --installer > seed.txt
#  debconf-get-selections >> seed.txt
#  cat seed.txt | python seed.sort.py

import sys
import re
import os

# some output modifiers, which could be done from command line at some point
di_only = True  # True: exclude other entries d-i entry available, False to print all entries
answers_only = False # True: only print entries with answers

def buildfields( s ):
  fields = ()
  match = re.match( '^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', s )
  if ( None != match ):
    fields = ( match.group(1), match.group(2), match.group(3), match.group(4) )
  else:
    match = re.match( '^(\S+)\s+(\S+)\s+(\S+)', s )
    if ( None == match ):
      print 'broken 1'
      os._exit(0)
    else:
      fields = ( match.group(1), match.group(2), match.group(3), '' )
  if ( 4 != len(fields) ):
    print 'broken 2'
    os._exit(0)
  return fields

def buildkey( fields ):
  key = fields[0] + ' ' + fields[1] + ' ' + fields[2]
  return key

# http://stackoverflow.com/a/17927520/2730971
f = sys.stdin
if len(sys.argv) > 1:
  f = open(sys.argv[1])

# state:
# 0 nothing found yet
# 1 found #, on transition in, save/clear, append
# 2 [1-zA-Z]:  save/clear, then append
# 3 empty or white space: append
# 4 anything else:  error, or ignore

state = 0 # state transitions
buf = ""  # accumulation of statements
dict = {} # check for duplicate keys at some point, may therefore need a func
key = ""
fields = ()

# parse the file and build up dictionary with entries and associated comments
for line in f:
  if ( 0 < len(line) ):
    text = line[:-1]
    if ( 0 < len(text) ):
      if ( '#' == text[0] ):
        if ( 1 != state ): # save what came before
          if ( 0 < len(key) ):
            if ( not ( key in dict ) ): # ignore duplicaetes further in file
              #print 'added dict 1'
              dict[key] = ( fields, buf )
          key = ""
          buf = ""
          fields = ()
        buf += line
        state = 1 # state: comment
      else:
        if ( ( 'a' <= text[0] and 'z' >= text[0] ) or ( 'A' <= text[0] and 'Z' >= text[0] ) ):
          if ( 2 == state ):
            if ( not ( key in dict ) ): # ingnore  duiplicates further in file
              #print 'added dict 2'
              dict[key] = ( fields, buf )
            key = ""
            buf = ""
            fields = ()
          fields = buildfields( text )
          key = buildkey( fields )
          buf += line
          state = 2  # state: regular character
        else:
          if (  ' ' == line[0] or '\t' == line[0] ):
            buf += line
            state = 3 # state: empty line or continuation
          else:
            state  = 4 # state: nothing useful
    #print( "state %s" % (state) )
    #print line[0]
if ( 0 < len(key) ): # finish any stragglers
  if ( not ( key in dict ) ): # ignore duplicaetes further in file
    #print 'added dict 3'
    dict[key] = ( fields, buf )

# parse out second element of line so can sort the dictionary
#  and build a new dictionary with multiple answers of same key
newdict = {}
#print len(keys)
for akey in list(dict.keys()):
  #print dict[akey]
  #print match.group(2)
  # maybe choice with answers here but some answers are legitimate blanks
  newkey = dict[akey][0][1] # pull out list, pull out fields, second field in list
  if ( newkey in newdict ):
    #alist = newdict[newkey]
    #alist += [ dict[akey] ]
    newdict[newkey] += [ dict[akey] ]
  else:
    newdict[newkey] =  [ dict[akey] ]

# print out the sorted list of questions, combining debconf and d-i
keys = list( newdict.keys() )
keys.sort()
for akey in keys:
  #print akey
  alist = newdict[akey]
  #print( "%d, %s" % ( len(alist), akey ) )
  if ( di_only ):
    difound = False
    for item in alist:
      #match = re.match( '^(\S+)', item[ 1 ][0] )
      #if ( None != match ):
      if ( 'd-i' == item[0][0] ):
        difound = True
        print item[1]
    if ( not difound ):
      for item in alist:
        print item[1]
  else:
    for item in alist:
      print item[1]

# questions to look into:
#  debconf/priority
