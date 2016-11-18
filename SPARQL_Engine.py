# @author: Qianru Zhou
# @email: chowqianru@gmail.com
# all rights reserved

import urllib2
import rdflib
from rdflib import plugin
from rdflib import Namespace
import requests, os

# Form the SPARQL query string based on customer's requirement
qstring = """
	select ?host ?port ?macAddr
	where { ?h :connectToPort ?port;
		   :hasMAC ?macAddr.
		bind(strafter(str(?h), 'http://home.eps.hw.ac.uk/~qz1/') as ?host)
	}
	"""

def runQuery(qstring):
	# Code from Fetching Data and Parsing Data examples
	with open('../my_buffer/my_buff_switchStatus.rdf', 'rb') as f: 
		response = str(f.read())

	graph = rdflib.Graph()
	graph.parse(data=response, format='turtle')

	netRes = Namespace("http://home.eps.hw.ac.uk/~qz1/")
	q = graph.query(qstring, initNs = {'':netRes})

	for row in q.bindings:
		print row

	return q

q = runQuery(qstring)
