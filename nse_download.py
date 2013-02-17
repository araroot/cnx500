import os
import urllib2
import datetime, time


# Add the headers that NSE servers like
def spoof_url(url):
	url.add_header('Accept', '*/*')
	url.add_header('User-Agent', 'Mozilla/5.0')
	url.add_header('Referer', 'http://www.nseindia.com/products/content/equities/equities/eq_security.htm')
	return url
	 
def download_bhav(start_date, end_date, write_dir, btype='fo'):
	if btype == 'fo': bdir = 'DERIVATIVES'
	else: 			  bdir = 'EQUITIES'
	
	current_date = start_date - datetime.timedelta(days=1)
	while current_date < end_date:
		current_date += datetime.timedelta(days=1)
		if current_date.isoweekday() > 5: continue # No market on Saturday, Sunday
		date_str = current_date.strftime('%d-%m-%Y')
		outfile = write_dir + date_str + '.csv.zip'
		if os.path.isfile(outfile): 
			print 'File exists for %s, skipping ...' %date_str 
			continue
	    
		try:
			url   = 'http://www.nseindia.com/ArchieveSearch?h_filetype='
			url  += '%sbhav&date=%s&section=%s'%(btype, date_str, btype.upper())
			dummy = spoof_url(urllib2.Request(url))
			junk = urllib2.urlopen(dummy).read()
		except urllib2.URLError:
			print 'Phase 1: Failed to get data for %s'%(date_str)
			continue
		try:
			x = datetime.datetime.strptime(date_str, '%d-%m-%Y')
			y = x.year
			m = x.strftime('%b').upper()
			d = x.strftime('%d') 
			#example_url = 'http://www.nseindia.com/content/historical/DERIVATIVES/2008/SEP/cm08SEP2008bhav.csv.zip'
			url = 'http://www.nseindia.com/content/historical/'
			url += '%s/%s/%s/%s%s%s%sbhav.csv.zip'%(bdir,y,m,btype,d,m,y)
			download_link = spoof_url(urllib2.Request(url))
			tru_file = urllib2.urlopen(download_link)
			output = open(outfile, 'wb')
			output.write(tru_file.read())
			output.close()
			print '... progress ... downloaded data for %s'%date_str
		except urllib2.URLError:
			print 'Phase 2: Failed to get data for %s'%(date_str)
			continue

def download_fovolt(start_date, end_date, write_dir):
	base_url   = 'http://www.nseindia.com/ArchieveSearch?h_filetype=fovolt&date=%s&section=FO'

	current_date = start_date - datetime.timedelta(days=1)
	while current_date < end_date:
	  current_date += datetime.timedelta(days=1)
	  if current_date.isoweekday() > 5: continue # No market on Saturday, Sunday
	  date_str = current_date.strftime('%d-%m-%Y')
	  outfile = write_dir + 'fovolt' + date_str + '.csv'
	  if os.path.isfile(outfile): 
	    print 'File exists for %s, skipping ...' %date_str 
	    continue
	    
	  try:
	    url   = base_url % (date_str)    
	    dummy = spoof_url(urllib2.Request(url))
	    junk = urllib2.urlopen(dummy).read()
	  except urllib2.URLError:
	      print 'Phase 1: Failed to get data for %s'%(date_str)
	      continue
	  try:
	    x = datetime.datetime.strptime(date_str, '%d-%m-%Y')
	    y = x.year
	    m = x.strftime('%m')
	    d = x.strftime('%d') 
	    #example_url = 'www.nseindia.com/archives/nsccl/volt/FOVOLT_07022012.csv'
	    url = 'http://www.nseindia.com/archives/nsccl/volt/FOVOLT_%s%s%s.csv'%(d,m,y)
	    download_link = spoof_url(urllib2.Request(url))
	    tru_file = urllib2.urlopen(download_link)
	    output = open(outfile, 'wb')
	    output.write(tru_file.read())
	    output.close()
	    print '... progress ... downloaded data for %s'%date_str
	  except urllib2.URLError:
	      print 'Phase 2: Failed to get data for %s'%(date_str)
	      continue
  
if __name__ == '__main__':
	from_date = datetime.datetime(2013, 2, 1)
	to_date   = datetime.datetime(2013, 2, 28)
	download_bhav(from_date, to_date, '../fotest/', 'fo')
	download_bhav(from_date, to_date, '../eqbhav/', 'cm')
	#download_fovolt(from_date, to_date, '../fovolt/')
