import zipfile
import csv
import os
import datetime
import math

def check_sanity(input_line):
	if len(input_line) < 5:
		print 'Failed Sanity check: ',line 
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
						scrip_return = math.log(float(line[5]) / float(line[7]))
					except (ValueError, ZeroDivisionError):
						print 'DEBUG, error', line
						continue
					master_db[scrip][current_date] = scrip_return
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
			days_ret = entries[k]
			if days_ret < -0.25 and symbol in valid_symbols: 
				debug_file.write('%s,%s,%.4f,%d\n'%(symbol,date_str,days_ret,0)) 
			outfile.write('%s,%s,%.4f\n'%(symbol,date_str,days_ret))
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
	cnx500_masterlist = read_cnx500_mappings('../symbols/cnx500_mappings.csv')
	dbgfile = open('../symbolwise/debug.csv', 'w')
	dbgfile.write('symbol,date,return,corrected\n')
	for year in range(2003, 2013):
		from_date = datetime.datetime(year, 1, 1)
		to_date   = datetime.datetime(year, 12, 31)
		my_db = create_symbol_db(from_date, to_date)
		output_db(my_db, cnx500_masterlist, '../symbolwise/' + str(year) + '/', dbgfile)
	# special processing for year 2013
	year = 2013
	from_date = datetime.datetime(year, 1, 1)
	to_date   = datetime.datetime(year, 2, 28)
	my_db = create_symbol_db(from_date, to_date)
	output_db(my_db, cnx500_masterlist, '../symbolwise/' + str(year) + '/', dbgfile)
	dbgfile.close()
