import csv
from collections import defaultdict
import re

# fix the usual stuff such as change LTD or LTD. to LIMITED etc.
def fix_name(input_name):
	fixed_name = input_name.upper()
	fixed_name = re.sub(r'\.$','',fixed_name) # remove any trailing .
	fixed_name = re.sub(r'LTD$','',fixed_name)
	fixed_name = re.sub(r'LIMITED$','',fixed_name)
	fixed_name = re.sub(r'\s','',fixed_name)
	return fixed_name

def read_symbols(fname, name2symbols):
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			if line[0] == 'CNX 500':
				company_name = fix_name(line[3]) 
				name2symbols[company_name] = line[1]
	return name2symbols
	

def read_current_list(fname, name2symbols):
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			company_name = fix_name(line[0]) 
			name2symbols[company_name] = line[2]
	return name2symbols

def fix_symbols(fname, name2symbols):
	i = 0
	marked_entries = {}
	outfile = open('to_fix_cnx500.csv', 'w')
	outfile.write('Name,Symbol,Auto\n')
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			company_name = fix_name(line[2])
			if company_name in marked_entries: 
				continue # already considered
			else: 
				marked_entries[company_name] = 1
			
			if company_name in name2symbols: 
				outfile.write('%s,%s,1\n'%(line[2], name2symbols[company_name]))
			else:
				outfile.write('%s,%s,0\n'%(line[2], line[1]))
	outfile.close()

if __name__ == '__main__':
	n2s = {}
	n2s = read_symbols('../symbols/Ix010609.csv', n2s)
	n2s = read_symbols('../symbols/Ix010610.csv', n2s)
	n2s = read_symbols('../symbols/ffix010611.csv', n2s)
	n2s = read_symbols('../symbols/ffix010612.csv', n2s)
	n2s = read_symbols('../symbols/ffix010113.csv', n2s)
	n2s = read_current_list('../symbols/ind_cnx500list.csv', n2s)
	fix_symbols('../symbols/cnx500_changes.csv', n2s)
