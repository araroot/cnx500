import os
import glob
import csv
import datetime
import zipfile 
import math
import numpy as np

def get_price(symbol, given_date):
    date_str = given_date.strftime('%d-%m-%Y')
    try:
        fh = open('../eqbhav/' + date_str + '.csv.zip', 'rb')
        z = zipfile.ZipFile(fh)
        for fname in z.namelist():
            z.extract(fname)
            with open(fname, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
                for line in reader:
                    if line[0] == symbol:
                        os.remove(fname)
                        return float(line[5])
    except:
        return None
    return None

def create_price_history(symbol, last_price, r_history, r_dates):
    if not last_price:
        print 'DEBUG: serious error for symbol', symbol
        return []
    p_history = []
    for r in reversed(r_history):
        p_history.append(last_price)
        last_price = last_price / math.exp(r)
    price_history = [p for p in reversed(p_history)]
    return price_history

def get_past_returns(r_history, start_point, n):
    try:
        if n > 0: past_ret = '%.2f'%sum(r_history[start_point+1:start_point+n]) 
        else:     past_ret = '%.2f'%sum(r_history[start_point+n:start_point+1])
    except:
        past_ret = 'NA'
    
    return past_ret
        
    
def walk_price_history(symbol, p_history, r_history, r_dates, fout):
    days_in_year = 250  # trading days in a year to first approx.
    hlen = len(p_history)
    if hlen <= days_in_year: return # insufficient price_history
    
    for k in range(days_in_year, hlen-1):
        if r_dates[k].month == r_dates[k+1].month : continue # we're interested only at end of month
        current_date  = datetime.datetime.strftime(r_dates[k], '%Y-%m-%d')
        current_price = p_history[k]
        price_window  = p_history[(k-250):(k+1)]
        date_window   = r_dates[(k-250):(k+1)]
        
        hi52, lo52 = max(price_window), min(price_window)
        hi52_date  = datetime.datetime.strftime(date_window[price_window.index(hi52)], '%Y-%m-%d')
        lo52_date  = datetime.datetime.strftime(date_window[price_window.index(lo52)], '%Y-%m-%d')
        fr         = 1.0 * (current_price - lo52) / (hi52 - lo52)
        vol        = np.std(price_window)
        
        ret_f1      = get_past_returns(r_history, k, 22) # fwd 1 month
        ret_b1      = get_past_returns(r_history, k,  -22) # prev 1 months
        ret_b6      = get_past_returns(r_history, k,  -126) # prev 6 months
        ret_b9      = get_past_returns(r_history, k,  -189) # prev 9 months
        ret_b12     = get_past_returns(r_history, k, -252) # prev 12 months
        
        my_key      = symbol + datetime.datetime.strftime(r_dates[k], '%m%y')
        fout.write('%s,%s,%s,%.2f,%.2f,%s,%.2f,%s,%.2f,%.2f,%s,%s,%s,%s,%s\n'
                   %(my_key,current_date,symbol,current_price,hi52,hi52_date,lo52,
                     lo52_date,fr,vol,ret_f1,ret_b1, ret_b6, ret_b9,ret_b12))
        
def create_data(fname, fout):
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
        i = 0
        r_history, r_dates = [], []
        for line in reader:
            i+= 1
            if i==1: continue # skip header
            r_history.append(float(line[2]))
            r_dates.append(datetime.datetime.strptime(line[1], '%d-%b-%Y'))
        
    last_date = r_dates[-1]
    symbol    = fname.split('/')[2].replace('.csv','')
    last_price = get_price(symbol, last_date)
    p_history = create_price_history(symbol, last_price, r_history, r_dates)
    walk_price_history(symbol, p_history, r_history, r_dates, fout)


def write_file_header(ofile):
    ofile.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'
                   %('key','date','symbol','close_price','hi52price','hi52date','lo52price',
                     'lo52date','fraction','vol','ret_f1','ret_b1', 'ret_b6', 'ret_b9','ret_b12'))
    
def create_master_datafile():
    filenames = glob.glob('../symbolwise/*.csv')
    outfile   = open('52wk.csv', 'w')
    write_file_header(outfile)
    
    for filename in filenames:
        create_data(filename, outfile)
    outfile.close()

def create_cnx500_datafile():
    dict52 = {}
    outfile   = open('rdata.csv', 'w')
    write_file_header(outfile)
        
    with open('../symbols/52wk.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
        for line in reader:
            dict52[line[0]] = ','.join(line)
    
    with open('../symbols/cnx500_history_all.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',', quotechar='"')
        for line in reader:
            my_key = line[1] + line[0]
            if my_key in dict52:
                outfile.write('%s\n'%dict52[my_key])
    
    outfile.close()
            
    
if __name__ == '__main__' :
    # create_master_datafile()
    create_cnx500_datafile()
    
