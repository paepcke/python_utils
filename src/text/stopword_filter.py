#!/usr/bin/env python
'''
Created on Aug 28, 2015

@author: paepcke
'''
import argparse
import os
import re
import sys


class StopwordFiler(object):
    '''
    Takes a textual input file and a stopword file.  
    Outputs a two or more columned CSV file, depending on 
    whether output is to be prepared for use on the tagul.com
    Website. Normally, words and frequencies are output.
    For example, an input file containing:
	    foo bar, blue, green!
	    Gray yellow.
	    bar
	    gray
    and a stopword list of:
	    Gray
		blue
	will output:
	    word,weight
	    bar,2
	    foo,1
	    gray,1
	    green,1
	    yellow,1
    
    If tagul is to be the final use, the output instead
    looks like this:
    
		word,weight,color,angle,font,url
		bar	2	000001	0	Expressway Regular	
		foo	1	000001	0	Expressway Regular	
		green	1	000001	0	Expressway Regular	
		yellow	1	000001	0	Expressway Regular	    
    '''
    
    def __init__(self, 
                 stopword_file, 
                 infile=None, 
                 outfile=None, 
                 filter_numbers=True, 
                 for_tagul=True,
                 tagul_color=(0,0,1),
                 tagul_font='Expressway Regular'
                 ):
        
        self.infile = infile
        self.outfile = outfile
        self.filter_numbers = filter_numbers
        self.for_tagul = for_tagul
        self.tagul_color = tagul_color
        self.tagul_font = tagul_font
        
        self.stop_set = set()
        self.in_set_freq_dict = {}
        
        self.tokenize_pattern = re.compile(r"[\s,.?!:]")
        self.numbers_pattern  = re.compile(r"[0-9.+-]+")
        
        # Import stopwords, lower-casing them all:
        with open(stopword_file, 'r') as fd:
            for line in fd:
                for word in self.tokenize_pattern.split(line):
                    self.stop_set.add(word.strip().lower())
                    
        self.filter()
        self.output_result()
        
    def filter(self):
        
        with (sys.stdin if self.infile is None else open(self.infile, 'r')) as in_fd:
            for line in in_fd:
                for word in self.tokenize_pattern.split(line):
                    if self.filter_numbers:
                        if self.numbers_pattern.match(word) is not None:
                            continue
                    word_lower = word.lower() 
                    if word_lower not in self.stop_set:
                        #out_fd.write(word + '\n')
                        # Word seen before?
                        freq_count = self.in_set_freq_dict.get(word_lower, None)
                        # If  
                        self.in_set_freq_dict[word_lower] = 1 if freq_count is None else freq_count+1

    def output_result(self):
        if self.for_tagul:
            col_header = 'word,weight,color,angle,font,url'
            tagul_addendum = '\t' + '\t'.join([self.rgb_to_hex(self.tagul_color).lstrip('#'), '0', self.tagul_font, '']) 
        else:
            col_header = 'word,weight'
            tagul_addendum = ''

        with (sys.stdout if self.outfile is None else open(self.outfile, 'w')) as out_fd:
            out_fd.write(col_header + '\n')
            for word in sorted(self.in_set_freq_dict.keys()):
                out_fd.write(word + '\t' + str(self.in_set_freq_dict[word]))
                if self.for_tagul:
                    out_fd.write(tagul_addendum)
                out_fd.write('\n')

    def rgb_to_hex(self, rgb):
        '''
        Given a tuple of integer RGB values,
        ouput '#rrggbb'
        
        :param rgb: rgb value, such as (252,176,10)
        :type rgb: (int,int,int)
        '''
        return '#%02x%02x%02x' % rgb

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('stopword_file',
                        action='store',
                        help='File with list of stopwords (mandatory).')
    parser.add_argument('-i', '--infile',
                        action='store',
                        help='File from which to remove stopwords; default: stdin'
                        )
    parser.add_argument('-o', '--outfile',
                        action='store',
                        help='Output file; default: stdout'
                        )
    parser.add_argument('-n', '--nonumbers',
                        action='store_true',
                        help='Filter all numbers; default: True'
                        )
    parser.add_argument('-t', '--tagul',
                        action='store_true',
                        help='Output not just words and frequencies, but also color and other columns needed for tagul.com wordclouds; default: True'
                        )
    
    
    args = parser.parse_args();
    
    StopwordFiler(args.stopword_file,
                  infile=args.infile,
                  outfile=args.outfile,
                  filter_numbers=args.nonumbers,
                  for_tagul=args.tagul
                 )
