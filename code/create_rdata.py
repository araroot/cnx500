import csv
import datetime
from collections import defaultdict

def get_cnx500list(fname, month_stamp):
	cnx500 = []
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			if month_stamp in line[0]:
				cnx500.append(line[1])
	return cnx500

def diff_month(d1, d2):
    return (d1.year - d2.year)*12 + d1.month - d2.month

def get_symbol_data(symbol, on_date):
	fname = '../symbolwise/' + symbol + '.csv'
	ret_history = defaultdict(list) 
	ret_summary = []
	i = 0
	with open(fname, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
		for line in reader:
			i += 1
			if i==1: continue
			try:
				dt    = datetime.datetime.strptime(line[1],'%d-%b-%Y')
				ret   = float(line[2])
				n     = diff_month(on_date, dt)
				if n > 13 or n < 0: continue # not interested in such price histories
				ret_history[n].append(ret)
			except ValueError:
				continue
	for j in range(0,14):
		if len(ret_history[j]) > 15:	# the month needs to have atleast 15 trading days
			ret_summary.append('%.4f'%sum(ret_history[j]))
		else:
			ret_summary.append('NA')
	
	return ret_summary
	
def create_rdata(on_date, ofile):
	stamp = '%02d%02d'%(on_date.month, on_date.year-2000)
	out_stamp = '%d%02d'%(on_date.year,on_date.month)
	print 'debug processing ', out_stamp
	current_list = get_cnx500list('../symbols/cnx500_history_all.csv', stamp)
	for symbol in current_list:
		symbol_data = get_symbol_data(symbol, on_date)
		output_data = ','.join(symbol_data)
		ofile.write('%s,%s,%s\n'%(out_stamp,symbol,output_data))
		
if __name__ == '__main__':
	outfile = open('data4r.csv','w')
	header_str = ''
	for i in range(0,14): header_str = header_str + ',r'+str(i)
	outfile.write('stamp,symbol%s\n'%header_str)
	
	for year in range(2008, 2013):
		for month in range(1,13):
			cutoff_date = datetime.datetime(year, month, 1)
			create_rdata(cutoff_date, outfile)
	outfile.close()
