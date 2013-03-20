# Coursera NLP class
# Akhilesh Nayak
# Assignment 1
# 3/18/2013

import sys
import re
import os
import shutil
import commands

from replace_infreq import get_filtered, get_write_file_path

tag_list = ['I-GENE','O']
trigram_estimates_dict = {}

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

def get_tag(word,emission_params,freq_words):
  if word not in freq_words:
    word = '_RARE_'
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

def create_tagged_file(emission_params,filename,freq_words):
  read_file = open(filename,'rU')
  write_file_path = get_write_file_path(filename,'.tagged')
  write_file = open(write_file_path, 'w')
  for line in read_file:
    if line == '\n': 
      write_file.write('\n')
      continue 
    word = line.strip()
    tag = get_tag(word,emission_params,freq_words)
    write_file.write(word + ' ' + tag + '\n')
  read_file.close()
  write_file.close()

def create_viterbi(emission_params,filename,freq_words):
  read_file = open(filename,'rU')
  write_file_path = get_write_file_path(filename,'.viterbi')
  write_file = open(write_file_path, 'w')
  sentence = []
  for line in read_file:
    if line == '\n': 
      sentence.append('STOP')
      viterbi_tags = viterbi(emission_params,freq_words,sentence)
      write_viterbi_tags(sentence,viterbi_tags,write_file)
      sentence = []
    else: 
      word = line.strip()
      sentence.append(word)
  read_file.close()
  write_file.close()

def write_viterbi_tags(sentence,viterbi_tags,write_file):
  del sentence[-1]
  size = len(sentence)
  index = 0
  while index < size:
    write_file.write(sentence[index] + ' ' + viterbi_tags[index] + '\n')
    index += 1
  write_file.write('\n')

def generate_trigram_estimates(filename):
  bigram_counts_dict = {}
  trigram_counts_dict = {}
  read_file = open(filename,'rU')
  for line in read_file:
    if 'WORDTAG' in line or '1-GRAM' in line:
      continue
    elif '2-GRAM' in line:
      (count,tag,x,y) = line.split(' ')
      y = y.strip()
      bigram_counts_dict[(x,y)] = float(count)
    elif '3-GRAM' in line:
      (count,tag,x,y,z) = line.split(' ')
      z = z.strip()
      trigram_counts_dict[(x,y,z)] = float(count)
  read_file.close()
  for ((x,y,z),value) in trigram_counts_dict.items():
    trigram_estimates_dict[(x,y,z)] = value/bigram_counts_dict[(x,y)]
  #print trigram_estimates_dict
    
def trigram_estimate(x,y,z):
  return trigram_estimates_dict[(x,y,z)]
  
def get_emission_param(word,tag,emission_params,freq_words):
  if word not in freq_words:
    word = '_RARE_'
  if (word,tag) in emission_params:
   return emission_params[(word,tag)]
  else: return 0.0

def viterbi(emission_params,freq_words,sentence):
  n = len(sentence)
  #print 'n=', n
  s = {} 
  s[-1] = ['*']
  s[0] = ['*']
  for k in range(1,n+1):
    s[k] = tag_list
  #print 's=', s
  pi = {}
  pi[(0,'*','*')] = 1
  bp = {}
  for k in range(1,n+1):
    #print 'k=', k
    for u in s[k-1]:
      #print 'u=', u
      for v in s[k]:
        #print 'v=', v
        max = -1
        for w in s[k-2]:
          #print 'w=', w
          val = (pi[(k-1,w,u)] * trigram_estimate(w,u,v) * 
                  get_emission_param(sentence[k-1],v,emission_params,freq_words))
          if val > max:
            max = val
            pi[(k,u,v)] = max
            bp[(k,u,v)] = w
  max = -1
  y = ['']*(n+1)
  for u in s[n-1]:
    for v in s[n]:
      val = pi[(n,u,v)] * trigram_estimate(u,v,'STOP')
      if val > max:
        max = val
        y[n-1] = u
        y[n] = v
  for k in range(n-2,0,-1):
    y[k] = bp[(k+2,y[k+1],y[k+2])]
  del y[0]
  return y

def freq_filter(word,freq):
  if freq >= 5:
    return True
  else: return False
  
def approx_equal(a,b,eps=0.0001):
  return abs(a - b) <= eps

def usage():
  print "usage: --counts countsfile --train trainingfile [--input inputfile]";

def main():

  args = sys.argv[1:]
  if not args:
    usage()
    sys.exit(1)

  # counts file after replacing the _RARE_ words (gene.counts.replaced)
  counts_file = ''
  if args[0] == '--counts':
    counts_file = args[1]
    del args[0:2]
    
  # original training file (gene.train)
  training_file = ''
  if args[0] == '--train':
    training_file = args[1]
    del args[0:2]
    
  # file to be tagged (gene.dev)
  input_file = ''
  if len(args) != 0 and args[0] == '--input':
    input_file = args[1]
    del args[0:2] 

  if counts_file != '' and training_file != '':
    # counts from replaced training file
    emission_params = get_emission_params(counts_file)
    
    freq_words = get_filtered(training_file,freq_filter)
    
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
      create_tagged_file(emission_params,input_file,freq_words)
      
      generate_trigram_estimates(counts_file)
      create_viterbi(emission_params,input_file,freq_words)
    
  else:
    usage()
    
if __name__ == "__main__":
  main()
