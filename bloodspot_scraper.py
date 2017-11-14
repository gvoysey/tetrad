import scrapy
import selenium 

genelist = [
			'IL3RA'
			,
			]
dataset = 'MERGED_AML'

def query_url(gene,dataset):
	"""Form a proper URL for data retrieval"""
	return f'http://servers.binf.ku.dk/bloodspot/?gene={gene}&dataset={dataset}'

