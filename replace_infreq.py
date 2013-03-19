# Coursera NLP class
# Akhilesh Nayak
# Assignment 1
# 3/18/2013

import sys
import re
import os
import shutil
import commands

# TODO : use comprehension for filtering?
def get_infrequent(filename):
  read_file = open(filename, 'rU')
  freq = {}
  infrequent_words = set()
  for line in read_file:
    if line == '\n': continue
    (word,tag) = line.split(' ')
    if word in freq:
      freq[word] += 1
    else: freq[word] = 1
  read_file.close()
  #print freq
  for key,value in freq.items():
    if value < 5:
      infrequent_words.add(key)
  return infrequent_words

def get_write_file_path(filename):
  path = os.path.abspath(filename)
  return path + '.replaced'
  
def write_replaced_file(infrequent_words,filename):
  write_file_path = get_write_file_path(filename)
  #print write_file_path
  write_file = open(write_file_path, 'w')
  read_file = open(filename, 'rU')
  for line in read_file:
    if line == '\n': 
      write_file.write('\n')
      continue
    (word,tag) = line.split(' ')
    if word in infrequent_words:
      write_file.write('_RARE_ ' + tag)
    else:
      write_file.write(line)
  read_file.close()
  write_file.close()
  
def replace_infrequent(filename):
  infrequent_words = get_infrequent(filename)
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