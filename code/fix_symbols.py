import csv
from collections import defaultdict
import re
import datetime

# fix the usual stuff such as change LTD or LTD. to LIMITED etc.
def fix_name(input_name):
	fixed_name = input_name.upper()
	fixed_name = re.sub(r'\.','',fixed_name) # remove any .
	fixed_name = re.sub(r'\s','',fixed_name) # any spaces
	fixed_name = re.sub(r'\&','AND',fixed_name)
	fixed_name = re.sub(r'LTD$','',fixed_name)
	fixed_name = re.sub(r'LIMITED$','',fixed_name)
	if len(fixed_name) > 20: fixed_name = fixed_name[:20] # take first 20 chars
	return fixed_name

def get_symbol_changes(fname):
	sym_changes = {}
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			effective_date = datetime.datetime.strptime(line[3], '%d-%b-%Y')
			sym_changes[line[2]]  = (line[1], effective_date)
	return sym_changes

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


def get_cnx500list(fname, month_stamp):
	cnx500 = []
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			if month_stamp in line[0]:
				cnx500.append(line[1])
	return cnx500

def get_cnx500_mappings(fname):
	cnx500map = {}
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			company_name = fix_name(line[0])
			cnx500map[company_name] = line[1]
	return cnx500map


def get_cnx500_changes(fname, name2symbols, sym_changes):
	cnx500changes = []
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i == 1: continue # skip the header
			if '-' in line[1]: change_date = datetime.datetime.strptime(line[1], '%d-%m-%Y')
			if '/' in line[1]: change_date = datetime.datetime.strptime(line[1], '%d/%m/%Y')
			if change_date > datetime.datetime(2009, 5, 1): continue # we have gr8 data till May 2009
			try:
				change_symbol = name2symbols[fix_name(line[2])]
			except KeyError:
				print 'DEBUG: symbol not in map', line[2]
				continue
			if 'Exclusion' in line[3]: change_type = 'E'
			if 'Inclusion' in line[3]: change_type = 'I'
			adjusted_symbol = adjust_for_symbolchange(change_date, change_symbol, sym_changes)
			cnx500changes.append((change_date, adjusted_symbol, change_type))
	
	cnx500r = [c for c in reversed(cnx500changes)]
	return cnx500r # so that latest changes are first

def adjust_for_symbolchange(cutoff, symbol, sym_changes):
	if symbol in sym_changes and cutoff < sym_changes[symbol][1]:
		adjusted_symbol = sym_changes[symbol][0]
		print 'DEBUG: returning %s instead of %s'%(adjusted_symbol,symbol)
		return adjusted_symbol
	else:
		return symbol
	
def print_cnx500_list(current_list, changes, cutoff, outfile, sym_changes):
	''' Apply changes going from back to front
	Output the list as it existed at that point in time
	'''
	date_at_cutoff = datetime.datetime.strftime(cutoff, '%m%y')
	print 'DEBUG: preparing list for ',date_at_cutoff
	list_at_cutoff = [c for c in current_list] # list copy needs to be done!
	for entry in changes:
		if entry[0] < cutoff: break
		if entry[2] == 'E' : list_at_cutoff.append(entry[1])
		if entry[2] == 'I' :
			try: 
				list_at_cutoff.remove(entry[1])
			except ValueError:
				print 'DEBUG: could not remove entry', entry
				continue
	for e in list_at_cutoff:
		e_adj = adjust_for_symbolchange(cutoff, e, sym_changes)
		outfile.write('%s,%s\n'%(date_at_cutoff, e_adj))
	
def create_cnx500_history():
	cnx500_may09     = get_cnx500list('../symbols/cnx500_history.csv', '0509')
	eq_mappings      = get_cnx500_mappings('../symbols/cnx500_mappings.csv')
	symbol_changes  = get_symbol_changes('../symbols/symbolchange.csv')
	cnx500_changes  = get_cnx500_changes('../symbols/cnx500_changes.csv', eq_mappings, symbol_changes)
	#print cnx500_changes
	output_file = open('../symbols/cnx500history_old.csv', 'w')
	output_file.write('Date,Symbol\n')
	for year in reversed(range(2001, 2010)):
		for month in reversed(range(1,13)):
			cutoff_date = datetime.datetime(year, month, 1)
			print_cnx500_list(cnx500_may09, cnx500_changes, cutoff_date, output_file, symbol_changes)
	output_file.close() 
	
if __name__ == '__main__':
	create_cnx500_history()
