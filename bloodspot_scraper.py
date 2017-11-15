import selenium.common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from os import path, remove
from scipy.io import savemat
import csv
from collections import defaultdict
from datetime import datetime
import re
import sys
import time
import json

genelist = [
            'ITGB5'
            , 'PTPRJ'
            , 'SLC30A1'
            , 'EMC10'
            , 'SLC6A6'
            , 'TNFRSF1B'
            , 'CD82'
            , 'ITGAX'
            , 'CR1'
            ,'DAGLB'
            ,'SEMA4A'
            ,'TLR2'
            ,'LTB4R'
            ,'P2RY13'
            ,'LILRB2'
            ,'EMB'
            ,'CD96'
            ,'LILRB3'
            ,'LILRA6'
            ,'LILRA2'
            ,'EMR2'# referred to as 'ADGRE2' in the paper
            ,'LILRB4'
            ,'CD70'
            ,'CCR1'
            ,'IL3RA'
            ,'CD44'
            ,'FOLR2'
            ,'CD38'
            ,'FUT3'
            ,'CD33'
            ,'CLEC12A'
            ]

dataset = 'MERGED_AML'

options = webdriver.ChromeOptions()
#options.add_argument('headless')
# options.binary_location ='chromedriver.exe'

def sanitize_name(namestr):
    """A valid variable name starts with a letter, followed by letters, digits, or underscores."""
    keywords = ['break'
                ,'case'
                ,'catch'
                ,'classdef'
                ,'continue'
                ,'else'
                ,'elseif'
                ,'end'
                ,'for'
                ,'function'
                ,'global'
                ,'if'
                ,'otherwise'
                ,'parfor'
                ,'persistent'
                ,'return'
                ,'spmd'
                ,'switch'
                ,'try'
                ,'while']
    sanitizer = re.compile(r'(\W)')
    namestr = sanitizer.sub('',namestr)
    if not namestr[0].isalpha():
        namestr = f'matlab_{namestr}'
    if namestr in keywords:
        raise NameError(f'{namestr} is not a valid matlab name')
    return namestr



def query_url(gene,dataset):
    """Form a proper URL for data retrieval"""
    return f'http://servers.binf.ku.dk/bloodspot/?gene={gene}&dataset={dataset}'

def process_csv(fname):
    name,ext = path.splitext(path.basename(path.abspath(fname)))
    with open(fname,'r') as _:
        r = csv.reader(_)
        headers = next(r)
        gene_name = headers.pop(0) #discard the first column, no data.
        values = next(r)
        values.pop(0) #discard the first column, no data.
        matlab_data = defaultdict(list)
        data = defaultdict(list)
        for k,v in zip(headers,values):
            matlab_data[sanitize_name(k)].append(float(v))
            data[k].append(float(v))
        matlab_data['dataset']:dataset
        data['dataset']:dataset
    struct = {name:matlab_data}
    savemat(f'{name}.mat', struct)
    with open(f'{name}.json','w') as _:
        json.dump(data,_)
    # remove(path.abspath(fname))




def main(*args):
    """Retrieve a list of gene data"""
    if not any(args):
        to_download=genelist
    else:
        to_download=args
    csvs = []

    for gene in to_download:
        driver = webdriver.Chrome(chrome_options=options)
        driver.implicitly_wait(15)
        driver.get(query_url(gene, dataset))
        # driver.refresh()
        try:
            dl_button = driver.find_element_by_id('export_text')
            dl_button.click()
            fname = path.join(path.expanduser('~'), 'Downloads',f'{gene}_log2.csv')
            dlstart = datetime.now()
            while not path.isabs(fname):
                WebDriverWait(driver=driver,timeout=15)
                if (datetime.start()-dlstart) > 60*5:
                    raise FileExistsError(f'could not download {fname}')
            #driver.close()
            csvs.append(fname)
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            print(f'failed to obtain data for {gene}, not present in database.')

    for f in csvs:
        process_csv(f)
        



if __name__ == "__main__":
    main([*sys.argv[1:]])
    #process_csv("IL3RA_log2.csv")