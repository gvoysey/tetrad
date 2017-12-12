"""Scrapes bloodspot.edu for expression data in various tissue types for a list of genes."""
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from os import path

import selenium.common
from scipy.io import savemat
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

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
            , 'DAGLB'
            , 'SEMA4A'
            , 'TLR2'
            , 'LTB4R'
            , 'P2RY13'
            , 'LILRB2'
            , 'EMB'
            , 'CD96'
            , 'LILRB3'
            , 'LILRA6'
            , 'LILRA2'
            , 'EMR2'# referred to as 'ADGRE2' in Perna (2017)
            , 'LILRB4'
            , 'CD70'
            , 'CCR1'
            , 'IL3RA'
            , 'CD44'
            , 'FOLR2'
            , 'CD38'
            , 'FUT3'
            , 'CD33'
            , 'CLEC12A'
            ]

dataset = 'MERGED_AML'

options = webdriver.ChromeOptions()
#options.add_argument('headless')
# options.binary_location ='chromedriver.exe'

def known_bad(x):
    """provide string substitutions for common invalid tokens, or remove them if not found."""
    return {' ': '_',
            '(': '_lp_',
            ')': '_rp_',
            '-': '_minus_',
            '/': '_div_',
            ';': '_sc_'
            }.get(x, '')


def sanitize_name(namestr):
    """A valid matlab variable name starts with a letter, followed by letters,
    digits, or underscores, and cannot be one of several reserved words."""
    keywords = {'break', 'case', 'catch', 'classdef', 'continue', 'else', 'elseif', 'end', 'for', 'function',
                'global', 'if', 'otherwise', 'parfor', 'persistent', 'return', 'spmd', 'switch', 'try', 'while'}
    if namestr in keywords:
        raise NameError(f'{namestr} is not a valid matlab name')    
    
    # match whatever isn't alphanumeric or underscore
    for illegal in re.compile(r'([^A-Za-z0-9_])').findall(namestr):
        namestr = namestr.replace(illegal, known_bad(illegal))
    if not namestr[0].isalpha():
        namestr = f'm_{namestr}'
    return namestr



def query_url(gene,dataset):
    """Form a proper URL for data retrieval"""
    return f'http://servers.binf.ku.dk/bloodspot/?gene={gene}&dataset={dataset}'

def process_csv(fname):
    """Convert a data file downloaded from bloodspot into a valid collection of data points."""
    name,ext = path.splitext(path.basename(path.abspath(fname)))
    with open(fname,'r') as _:
        r = csv.reader(_)
        # The first row of the file is a row of repeated headers.
        headers = next(r)
        headers.pop(0) #discard the first column, no data.
        # The second row of the file is a row of repeated values, and this is the last row.
        values = next(r)
        values.pop(0) #discard the first column, no data.

        # matlab data gets the names changed, json data doesn't
        matlab_data = defaultdict(list)
        json_data = defaultdict(list)
        for k,v in zip(headers,values):
            matlab_data[sanitize_name(k)].append(float(v))
            json_data[k].append(float(v))
        matlab_data['dataset']=dataset
        json_data['dataset']=dataset

    struct = {name:matlab_data}
    savemat(f'{name}.mat', struct)

    with open(f'{name}.json','w') as _:
        json.dump(json_data,_)


def main(*args):
    """Retrieve a list of gene data"""
    if not any(args):
        to_download=genelist
    else:
        to_download=args
    csvs = []

    #  Scrape the page for each gene with a seperate chromedriver instance for stability.
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
        

def get_descriptions(driver):
    """Return the description of the variables"""
    driver.find_element_by_id('abbreviations').click()
    desc = driver.find_element_by_id('dropdownContentAbbs')
    desc = desc.split('Abbreviation')[1]
    descs = desc.split('\n')
    descriptions = {}
    for line in descs:
        abbrev, *full = line.split(' ')
        descriptions[abbrev] = ' '.join(full)
    return descriptions


if __name__ == "__main__":
    main([*sys.argv[1:]])
    #process_csv("IL3RA_log2.csv")