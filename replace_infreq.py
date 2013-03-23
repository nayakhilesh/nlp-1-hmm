# Coursera NLP class
# Akhilesh Nayak
# Assignment 1
# 3/18/2013

import sys
import re
import os
import shutil
import commands

def get_filtered(filename,filter):
  read_file = open(filename, 'rU')
  freq_dict = {}
  for line in read_file:
    if line.strip() == '': 
      continue
    (word,tag) = line.split(' ')
    if word in freq_dict:
      freq_dict[word] += 1
    else: freq_dict[word] = 1
  read_file.close()
  #print freq
  return set([word for (word,freq) in freq_dict.items() if filter(word,freq)])

def get_write_file_path(filename,suffix):
  path = os.path.abspath(filename)
  return path + suffix

def resolve_rare_class(word):
  if re.search(r'.*\d.*',word):
    return '_NUMERIC_'
  elif word.isupper():
    return '_ALLCAPS_'
  elif word[-1].isupper():
    return '_LASTCAP_'
  else: return '_RARE_'

def write_replaced_file(infrequent_words,filename):
  write_file_path = get_write_file_path(filename,'.replaced.classes')
  #print write_file_path
  write_file = open(write_file_path, 'w')
  read_file = open(filename, 'rU')
  for line in read_file:
    if line.strip() == '': 
      write_file.write('\n')
      continue
    (word,tag) = line.split(' ')
    if word in infrequent_words:
      write_file.write(resolve_rare_class(word) + ' ' + tag)
    else:
      write_file.write(line)
  read_file.close()
  write_file.close()
  
def infreq_filter(word,freq):
  if freq < 5:
    return True
  else: return False

def replace_infrequent(filename):
  infrequent_words = get_filtered(filename,infreq_filter)
  write_replaced_file(infrequent_words,filename)    

def usage():
  print "usage: --file filename";

def main():

  args = sys.argv[1:]
  if not args:
    usage()
    sys.exit(1)

  filename = ''
  if args[0] == '--file':
    filename = args[1]
    del args[0:2]

  if filename != '':
     replace_infrequent(filename)
  else:
    usage()

if __name__ == "__main__":
  main()