# Coursera NLP class
# Akhilesh Nayak
# Assignment 1
# 3/18/2013

import sys
import re
import os
import shutil
import commands


def get_emission_params(filename):
  read_file = open(filename, 'rU')
  gene_tag_count = 0
  zero_tag_count = 0
  gene_tag_dict = {}
  zero_tag_dict = {}
  for line in read_file:
    if re.search(r'\d-GRAM',line):
      #print 'skipping -GRAM'
      continue
    try:
      (count,type,tag,word) = line.split(' ')
    except ValueError:
      print 'ValueError'
      continue
    #print count, type, tag, word
    word = word.strip()
    count = float(count)
    if tag == 'I-GENE':
      gene_tag_count += count
      gene_tag_dict[word] = count
    elif tag == 'O':
      zero_tag_count += count
      zero_tag_dict[word] = count
    else: 
      raise Exception('unknown tag found')
  read_file.close()
  emission_params = {}
  for (key,value) in gene_tag_dict.items():
    emission_params[(key,'I-GENE')] = value/float(gene_tag_count)
  for (key,value) in zero_tag_dict.items():
    emission_params[(key,'O')] = value/float(zero_tag_count)
  #print emission_params
  return emission_params

def get_write_file_path(filename):
  path = os.path.abspath(filename)
  return path + '.tagged'

def get_tag(word,emission_params):
  if ((word, 'I-GENE') not in emission_params) and ((word, 'O') not in emission_params):
    word = '_RARE_'
  tag_list = ['I-GENE','O']
  max_val = 0
  max_tag = ''
  for tag in tag_list:
    key_tuple = (word, tag)
    if key_tuple in emission_params:
      val = emission_params[key_tuple]
      if val > max_val:
        max_tag = tag
        max_val = val
  return max_tag

def create_tagged_file(emission_params,filename):
  read_file = open(filename,'rU')
  write_file_path = get_write_file_path(filename)
  write_file = open(write_file_path, 'w')
  for line in read_file:
    if line == '\n': 
      write_file.write('\n')
      continue 
    word = line.strip()
    tag = get_tag(word,emission_params)
    write_file.write(word + ' ' + tag + '\n')
  return

def approx_equal(a,b,eps=0.0001):
  return abs(a - b) <= eps

def usage():
  print "usage: --counts countsfile [--input inputfile]";

def main():

  args = sys.argv[1:]
  if not args:
    usage()
    sys.exit(1)

  counts_file = ''
  if args[0] == '--counts':
    counts_file = args[1]
    del args[0:2]
    
  input_file = ''
  if len(args) != 0 and args[0] == '--input':
    input_file = args[1]
    del args[0:2] 

  if counts_file != '':
    # from replaced training file
    emission_params = get_emission_params(counts_file)
    
    # simple check
    gene_sum = 0
    zero_sum = 0
    for ((word,tag),value) in emission_params.items():
      #print ((word,tag),value)
      if tag == 'I-GENE':
        gene_sum += value
        #print 'gene_sum', gene_sum
      elif tag == 'O':
        zero_sum += value
        #print 'zero_sum', zero_sum
    if (not approx_equal(gene_sum,1.0)) or (not approx_equal(zero_sum,1.0)):
      print gene_sum, zero_sum
      raise Exception('error in computing emission parameters')
    
    if input_file != '':
      create_tagged_file(emission_params,input_file)
          
  else:
    usage()
    
if __name__ == "__main__":
  main()
