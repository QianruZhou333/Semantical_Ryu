# runs with ofctl_rest.py

from rdflib import Graph, plugin, Namespace, Literal
import json, rdflib_jsonld
from rdflib.plugin import register, Serializer
from rdflib.namespace import RDF
import requests

n = Namespace('http://home.eps.hw.ac.uk/~qz1/')
file_abs = '../my_buffer/my_buff_switchStatus.rdf'
g = Graph()

def getAllSwitches():
	allSwitches = requests.get('http://localhost:8080/v1.0/topology/switches').json()
	
	switchCount = 1 
	portCount = 1

	for item in allSwitches:
		s = 's' + str(item['dpid']).lstrip("0")
		g.add( (n[s], RDF.type, n['Switch']) )
		g.add( (n[s], n.hasName, Literal(s) ) )
		g.add( (n[s], n.hasID, Literal(str(item['dpid']).lstrip("0"))) )
	
		for item_1 in item['ports']:
			for item_2 in item_1:
				p = s + '_port' + str(item_1['port_no']).lstrip("0")
				g.add( (n[s], n.hasPort, n[p]) ) 	
				g.add( (n[p], RDF.type, n['Port']) )
				g.add( (n[p], n.hasName, Literal(item_1['name'])) )
				g.add( (n[p], n.hasHWAddr, Literal(item_1['hw_addr'])) )
				g.add( (n[p], n.port_no, Literal(str(item_1['port_no']).lstrip("0"))) )
				g.add( (n[p], n.inSwitchID, Literal(str(item_1['dpid']).lstrip("0"))) )	
			portCount = portCount + 1
		switchCount = switchCount + 1
	
		getHosts(item['dpid'])
		getAllFlowStatus(item['dpid'])
	
	with open(file_abs, 'a') as f:
		f.write(g.serialize(format = 'turtle'))


def getAllFlowStatus(switchID):
	print str(switchID).lstrip('0')
	allFlows = requests.get('http://localhost:8080/stats/flow/' + str(switchID).lstrip('0') )
	if not allFlows: 
		print 'there is not any flows currently.'
	else:
		allFlows = allFlows.json()	
		flow_count = 0

		for flow in allFlows[str(switchID).lstrip('0')]:
			g.add( (n['s' + str(switchID).lstrip('0')], n.hasFlow, n['s'+ str(switchID).lstrip('0') +'_flow' + str(flow_count)]) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], RDF.type, n['Flow']) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.priority, Literal(flow['priority'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.hard_timeout, Literal(flow['hard_timeout'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.byte_count, Literal(flow['byte_count'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.duration_sec, Literal(flow['duration_sec'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.length, Literal(flow['length'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.flags, Literal(flow['flags'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.table_id, Literal(flow['table_id'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.cookie, Literal(flow['cookie'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.packet_count, Literal(flow['packet_count'])) )
			g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.idle_timeout, Literal(flow['idle_timeout'])) )
			
			if flow['match']:
				g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.hasInPort, n['s' + str(switchID).lstrip('0') + '_port' + str(flow['match']['in_port'])]) )
				g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.hasDstAddr, Literal( str(flow['match']['dl_dst'])) ) )

			if flow['actions']:
				action_count = 1
				for action in flow['actions']:
					g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count)], n.hasAction, n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count) + '_action' + str(action_count)]) )
					g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count) + '_action' + str(action_count)], RDF.type, n['Action']) )
					g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count) + '_action' + str(action_count)], n.hasType, Literal(action[0:5]) ) )
					g.add( (n['s' + str(switchID).lstrip('0') + '_flow' + str(flow_count) + '_action' + str(action_count)], n.toPort, n['s' + str(switchID).lstrip('0') + '_port' + action[7:] ] ) )

					action_count += 1
										
			flow_count = flow_count + 1


def getHosts(switchID):
	hosts = requests.get('http://localhost:8080/v1.0/topology/hosts/' + str(switchID))
	if not hosts:
		print 'there is currently no hosts.'
	else:
		hosts = hosts.json()
		hostCount = 0

		for item in hosts:
			g.add( (n['s' + str(switchID).lstrip("0")], n.hasHost, n['s' + str(switchID).lstrip("0") + '_host' + str(hostCount)] ))
			g.add( (n['s' + str(switchID).lstrip("0") + '_host' + str(hostCount)], n.connectToPort, n['s' + str(switchID).lstrip("0") + '_port' + str(item['port']['port_no']).lstrip("0") ] ) )
			g.add( (n['s' + str(switchID).lstrip("0") + '_host' + str(hostCount)], n.hasIPv4, Literal(item['ipv4'][0]) ) )
			g.add( (n['s' + str(switchID).lstrip("0") + '_host' + str(hostCount)], n.hasMAC, Literal(item['mac'])) )
			if item['ipv6']:
				g.add( (n['s' + str(switchID).lstrip("0") + '_host' + str(hostCount)], n.hasIPv6, Literal(item['ipv6'])) )
			hostCount = hostCount + 1			

def clearFile(fname):
	with open(fname, 'w') as f:
		f.write('')

clearFile(file_abs)
getAllSwitches()
