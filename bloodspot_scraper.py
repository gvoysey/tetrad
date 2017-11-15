from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from os import path
from scipy.io import savemat
import csv
from collections import defaultdict
import re
import sys
import time

genelist = [
            'IL3RA'
            ,
            ]
dataset = 'MERGED_AML'

options = webdriver.ChromeOptions()
# options.add_argument('headless')
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
        gene_name = headers.pop(0)
        values = next(r)
        values.pop(0)
        data = defaultdict(list)
        for k,v in zip(headers,values):
            data[sanitize_name(k)].append(float(v))
    struct = {name:data}
    savemat(f'{name}.mat', struct)




def main(*args):
    """Retrieve a list of gene data"""
    if not any(args):
        to_download=genelist
    else:
        to_download=args
    csvs = []
    driver=webdriver.Chrome(chrome_options=options)
    for gene in to_download:        
        driver.implicitly_wait(5)
        driver.get(query_url(gene, dataset))
        driver.find_element_by_id('export_text').click()
        time.sleep(1)
        fname = path.join(path.expanduser('~'), 'Downloads',f'{gene}_log2.csv')
        if not path.isfile(fname):
            time.sleep(5)
            if not path.isfile(fname):      
                raise FileExistsError(f'{fname} not found!')
        csvs.append(fname)
    driver.close()
    for f in csvs:
        process_csv(f)
        



if __name__ == "__main__":
    main([*sys.argv[1:]])
    #process_csv("IL3RA_log2.csv")