import zipfile
import csv
import os
import datetime
import math

def check_sanity(input_line):
	if len(input_line) < 5:
		print 'Failed Sanity check: ',input_line 
		return False  
	
	if not(input_line[1] == 'EQ' or input_line[1] == 'BE'):
		return False
	
	return True
					
def create_symbol_db(start_date, end_date):
	master_db = {}
	current_date = start_date - datetime.timedelta(days=1)
	while current_date < end_date:
		current_date += datetime.timedelta(days=1)
		if current_date.isoweekday() > 5: continue # No market on Saturday, Sunday
		date_str = current_date.strftime('%d-%m-%Y')
		try:
			fh = open('../eqbhav/' + date_str + '.csv.zip', 'rb')
			z = zipfile.ZipFile(fh)
		except IOError:
			continue
		for fname in z.namelist():
			z.extract(fname)
			with open(fname, 'r') as csvfile:
				reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
				for line in reader:
					if check_sanity(line) == False: continue
					scrip = line[0]
					if scrip not in master_db: master_db[scrip] = {}
					try:
						scrip_return_cc = math.log(float(line[5]) / float(line[7])) # close2close
						scrip_return_oc = math.log(float(line[5]) / float(line[2])) # open2close
					except (ValueError, ZeroDivisionError):
						print 'DEBUG, error', line
						continue
					master_db[scrip][current_date] = (scrip_return_cc, scrip_return_oc)
			os.remove(fname)
		fh.close()
        
	return master_db
	
def output_db(master_db, valid_symbols, outdir, debug_file):
	for symbol in master_db:
		outfile = open(outdir + symbol + '.csv', 'w')
		outfile.write('symbol,date,return\n')
		entries = master_db[symbol]
		mykeys = sorted(entries)
		for k in mykeys: 
			date_str = datetime.datetime.strftime(k,'%d-%b-%Y')
			days_ret_cc, days_ret_oc = entries[k]
			if days_ret_cc < -0.25: # and condition is BUG!
				if days_ret_oc > -0.15:  						# likely corporate action
					debug_file.write('%s,%s,%.6f,%d\n'%(symbol,date_str,days_ret_cc,0)) 
					days_ret_cc = days_ret_oc
				# no else required, else means days_ret_oc is also very low and that's OK	
			outfile.write('%s,%s,%.6f\n'%(symbol,date_str,days_ret_cc))
		outfile.close()


def read_cnx500_mappings(fname):
	cnx500_list = {}
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			symbol = line[1]
			cnx500_list[symbol] = 1
	return cnx500_list
	

if __name__ == '__main__':
	cnx500_masterlist = read_cnx500_mappings('../symbols/cnx500_history_all.csv')
	dbgfile = open('../symbolwise/debug.csv', 'w')
	dbgfile.write('symbol,date,return,corrected\n')
	from_date = datetime.datetime(2004, 1, 1)
	to_date   = datetime.datetime(2013, 2, 28)
	my_db = create_symbol_db(from_date, to_date)
	output_db(my_db, cnx500_masterlist, '../symbolwise/', dbgfile)
	dbgfile.close()
