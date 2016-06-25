#!/usr/bin/env python

"""
Count the frequency of word tuples.

Usage:	freq.py                    [--clean] [--merge] [INFILE]
	freq.py freq   --length L  [--clean] [--merge] [INFILE]
	freq.py top N  --length L  [--clean] [--merge] [INFILE]
	freq.py --test
	freq.py --help

Where:
	--length L may be a single number or a range, such as 2:5
	--clean  puts the strings into a cononical form by lowercasing.

Output:
	length	freq	tuple
	1	7	badger
	1	5	fen
	2	2	very long
"""


import re
import sys
import itertools
from docopt import docopt

def test_count_ngrams():
	print "Test: Counting ngrams:"
	# Input:
	phrase= "a cat sat on a mat "
	desc  = "'"+phrase+"' repeated 9 times"
	words = (phrase*9).split(" ")
	words = [word for word in words if len(word)>0]
	# Call:
	freq1 = count_ngrams(words, 1)
	# Check:
	assert len(freq1) == 5, "Expect 5 distinct words in "+desc
	assert freq1[("cat",)] == 9, "Expect to see 'cat' nine times in "+desc
	assert freq1[("a",)] == 18, "Expect to see 'a' eighteen times in "+desc
	freq2 = count_ngrams(words, 2)
	assert len(freq2) == 6, "Expect six distinct 2-tuples in "+desc
	for ngram in freq2:
		expect = 9
		if ngram == ('mat','a'):
			expect = 8
		actual = freq2[ngram]
		assert actual == expect, "Expected "+str(expect)+"instances of "+str(ngram)+" in "+desc

def count_ngrams(source, n):
	"""
	Given a source of things, return a dictionary of tuple frequencies.
	"""
	source = iter(source)
	ngram = tuple([None]*n)
	try:
		for i in xrange(n-1):
			ngram = ngram[1:] + (next(source),)
	except:
		pass
	ans = {}
	for word in source:
		ngram = ngram[1:] + (word,)
		ans[ngram] = ans.get(ngram, 0) + 1
	return ans

def test_count_ngram_range():
	print "Test: count_ngram_range"
	# Input:
	words = ("a plague on both your houses "*5).split(" ")
	words = [word for word in words if len(word)>0]
	# Run:
	ans = count_ngram_range(words, 2, 5)
	# Test:
	assert len(ans) == 3, "Expected three results"
	for length in ans:
		assert len(words)+1-length == sum([ ans[length][ngram] for ngram in ans[length] ]), "The number of tuples doesn't add up."

def count_ngram_range(source, min, max):
	"""
	Given a source of things, return a dictionary of tuple frequencies for each frequency in the given range.
	Arguments:
	source - yields words
	min    - inclusive min length
	max    - exclusive max length
	"""
	return { i:count_ngrams(source, i) for i,source in itertools.izip(xrange(min, max), itertools.tee(source, max - min)) }

def test_top_n():
	print "Test: top n"
	# Input:
	d = {"nine": 9, "one": 1, "seven":7}
	ans = top_n(d,2)
	assert tuple(ans) == (("nine",9),("seven",7)), "Got:"+str(ans)

def top_n(freq, n):
	"""
	Given a dictionary with numeric values, return the top N key/value pairs as a list of tuples.
	"""
	entries = [ (k, v) for k, v in freq.iteritems() ]
	entries.sort(lambda a, b: b[1]-a[1])
	return entries[:n]

def top_ngrams(source, length, topN):
	"""
	Given a source of things, give the most frequently occurring tuples of a given length.
	"""
	freq = count_ngrams(source, length)
	return top_n(freq, topN)

def top_ngrams_range(source, min, max, topN):
	"""
	Given a source of things, give the most frequently occurring tuples for each in a range of lengths.
	"""
	return { i:top_ngrams(source, i, topN) for i,source in itertools.izip(xrange(min, max), itertools.tee(source, max - min)) }

def test_parse_file():
	print "Test: Parse a file into words"
	# Input:
	try:
		file = open(__file__, "r")
	except IOError as e:
		bail("I/O error({0}): {1}".format(e.errno, e.strerror))
		
	# Run:
	ans = parse_file(file)
	# Check:
	nwords = 0
	for word in ans:
		assert isinstance(word, basestring), "The file parser is not returning strings"
		assert len(word.split(' ')) == 1, "These aren't words but phrases: "+word
		assert len(word) > 0, "The words include empty strings"
		nwords += 1
	assert nwords>10, "There are definitely more than ten words in this file!"

def parse_file(file):
	"""
	Generate a sequence of words in a file.
	"""
	for line in file:
		for match in re.findall(r'\W*(\w+)', line):
			yield match

def get_words(args):
	"""
	Get  stream of words, cleaned as dictated by the command line arguments.
	"""
	words = parse_file(args['infile'])
	if args['clean']:
		words = lowercase(words)
	if args['merge']:
		words = merge_similar_words(words)
	return words

def lowercase(words):
	"""
	This gives words in a canonical form:
	"""
	for word in words:
		yield word.lower()

def printout(length, frequency, ngram):
	print "{0}\t{1}\t{2}".format(length, frequency, ngram)
def printout_header():
	printout("length", "freq", "ngram")

def main_test(args):
	print "Running all tests"
	test_count_ngrams()
	test_count_ngram_range()
	test_parse_file()
	test_top_n()
	test_similar_word()
	print "All tests complete"

def main_count_ngram_range(args):
	words = get_words(args)
	ans = count_ngram_range(words, args['nmin'], args['nmax'])
	printout_header()
	for length, freqs in ans.iteritems():
		for tuple, freq in freqs.iteritems():
			printout(length, freq, ' '.join(tuple))

def main_top_ngrams_range(args):
	words = get_words(args)
	ans = top_ngrams_range(words, args['nmin'], args['nmax'], args['top'])
	printout_header()
	for length, freqs in ans.iteritems():
		for tuple, freq in freqs:
	 		printout(length, freq, " ".join(tuple))

def bail(message):
	"""
	Print an error message and die.
	"""
	print >> sys.stderr, message
	exit(1)

def test_similar_word():
	print "Test: similar word"
	assert 0.5 < similarity('the', 'tree') < 0.6
	assert 0.2 < similarity('the', 'monkeypuzzletree') < 0.3
	assert 0.2 < similarity('monkeypuzzletree','treaty') < 0.3

def similarity(word1, word2):
	"""
	Computes similarity by:
		 2 * (longest common subsequence)
		----------------------------------
		   len(word1)   + len(word2)
	"""
	grid = [ [ 0 for i in xrange(-1, len(word2)) ] for i in xrange(-1, len(word1)) ]
	for i in xrange(1, len(word1)+1):
		for j in xrange(1, len(word2)+1):
			if (word1[i-1] == word2[j-1]):
				grid[i][j] = 1+grid[i-1][j-1]
			else:	grid[i][j] = max( grid[i][j-1], grid[i-1][j] )
	longest = grid[-1][-1]
	return longest * 2.0 / (len(word1) + len(word2))

def sign(n):
	"""
	Return:
		 1 if n is positive
		 0 if n is zero
		-1 if n is negative
	"""
	if n < 0: return -1
	if n > 0: return 1
	return 0

def merge_similar_words(source):
	"""
	Given a stream of words, generate another stream that is identical except that
	words have been replaced by previous words, if similar enough.
	"""
	dict = {}  # Output words
	root = {}  # Mapping from input words to output words

	for word in source:
		if word not in root:
			similar_words = [(known, similarity(word, known)) for known in dict if similarity(word, known) > 0.5]
			similar_words.sort(lambda a, b: sign(b[1] - a[1]))
			if len(similar_words) == 0:
				dict[word] = word
				root[word] = word
			else:
				root[word] = similar_words[0][0]
		yield root[word]

def get_cli_arguments():
	"""
	From the command line, get:
	infile	- a file handle
	nmin	- the minimum tuple length (int)
	nmax	- the maximum tuple length (int)
	top	- the number of top entries (int or None)
	action  - the function to apply (func)

	and return these as a dictionary.
	"""
	arguments = docopt(__doc__)

	infile = None
	if arguments['INFILE'] == None:
		infile = sys.stdin
	else:
		try:
			infile = open(arguments['INFILE'], "r")
		except IOError as e:
			bail("I/O error({0}): {1} {2}".format(e.errno, e.strerror, arguments['INFILE']))


	nmin = 2
	nmax = 5
	if arguments['L'] != None:
		if None == re.match(r'[0-9]+(:[0-9]+)?', arguments['L']):
			bail("Malformed length should be min:max e.g. 1:3 not "+arguments['L'])
		nmin, nmax = ([int(x) for x in arguments['L'].split(":")]*2)[:2]    #  5 -> (5,5)  or 3:7 -> (3,7)
		nmax += 1 # Assume that humans prefer inclusive ranges [] and pythonistas prefer right-exclusive ranges [).

	top = None
	if arguments['N'] != None:
		if None == re.match(r'[0-9]+', arguments['N']):
			bail("Malformed number: "+arguments['N'])
		top = int(arguments['N'])

	action = None
	if   arguments['--test']:
		action = main_test
	elif arguments['freq']:
		action = main_count_ngram_range
	elif arguments['top']:
		action = main_top_ngrams_range
	else:
		top = 10
		nmin, nmax = 2, 5
		action = main_top_ngrams_range

	return { 'infile':infile, 'nmin':nmin, 'nmax':nmax, 'top':top, 'action':action, 'clean':arguments['--clean'], 'merge':arguments['--merge']}
	
if __name__ == '__main__':
	arguments = get_cli_arguments()
	arguments['action'](arguments)
