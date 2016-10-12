import urllib2
import rdflib
from rdflib import plugin
from rdflib import Namespace
import requests, os

# Form the SPARQL query
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

def connectAll(q):
	# For each results print the value
	q1 = q
	action_type = 'output'
	for row in q.bindings:
		in_port = row['port']
		for row1 in q1.bindings:
			out_port = row1['port']
			print in_port, out_port
			if (in_port != out_port):
				dst = row1['macAddr']
				addFlow(dst, in_port, action_type, out_port)
			
def addARPFlow():
	payload = '{"table":0,"priority":10,"idle_timeout":0,"arp","actions":"flood"}'
	r = os.system('ovs-ofctl -O OpenFlow13 add-flow s1 "table=0,priority=10,idle_timeout=0,arp,actions=flood" ')
	print r

def addFlow(dst, in_port, action_type, to_port):
	payload = '{"dpid":1, "table_id":0, "priority":1, "match":{"dl_dst":"'+ str(dst) + '","in_port":'+ str(in_port) + '},"actions":[{"type":"'+ str(action_type).upper() + '","port":'+ str(to_port) + '}]}'
	print payload
	r = requests.post('http://localhost:8080/stats/flowentry/add', payload)

#addARPFlow()
q = runQuery(qstring)
connectAll(q)