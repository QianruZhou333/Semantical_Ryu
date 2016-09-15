# runs with ofctl_rest.py
# @author: Qianru Zhou
# @email: chowqianru@gmail.com
# all rights reserved

from rdflib import Graph, plugin, Namespace, Literal
import json, rdflib_jsonld
from rdflib.plugin import register, Serializer
from rdflib.namespace import RDF
import os
import requests

n = Namespace('http://home.eps.hw.ac.uk/~qz1/')
file_abs = '../my_buffer/my_buff_switchStatus.rdf'
g = Graph()

def getAllSwitches():
        allSwitches = requests.get('http://localhost:8080/v1.0/topology/switches').json()

        switchCount = 1
        portCount = 1

        for item in allSwitches:
                s = 's' + str(switchCount)
                g.add( (n[s], RDF.type, n['Switch']) )
                g.add( (n[s], n.name, Literal(s) ) )
                g.add( (n[s], n.dpid, Literal(item['dpid'])) )

                for item_1 in item['ports']:
                        for item_2 in item_1:
                                p = s + '_port' + str(item_1['port_no'])
                                g.add( (n[s], n.hasPort, n[p]) )
                                g.add( (n[p], RDF.type, n['Port']) )
                                g.add( (n[p], n.name, Literal(item_1['name'])) )
                                g.add( (n[p], n.hw_addr, Literal(item_1['hw_addr'])) )
                                g.add( (n[p], n.port_no, Literal(item_1['port_no'])) )
                                g.add( (n[p], n.dpid, Literal(item_1['dpid'])) )
                        portCount = portCount + 1
                switchCount = switchCount + 1

                getHosts(item['dpid'])

        with open(file_abs, 'a') as f:
                f.write(g.serialize(format = 'turtle'))


def getAllFlowStatus(switchID):
        allFlows = os.popen('curl -X GET http://localhost:8080/stats/flow/' + str(switchID)).read()
        allFlowsJson = json.loads(allFlows)

        for index in range( len(j[str(switchID)]) ):
                g.add( (n['s' + str(switchID)], n.hasFlow, n['s'+ str(switchID) +'_flow' + str(index)]) )
                g.add( (n['s' + str(switchID)], n.hasFlow, n['s'+ str(switchID) +'_flow' + str(index)]) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], RDF.type, n[Flow]) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], n.priority, Literal(j[switchID][index]['priority'])) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], n.hard_timeout, Literal(j[switchID][index]['hard_timeout'])) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], n.byte_count, Literal(j[switchID][index]['byte_count'])) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], n.duration_sec, Literal(j[switchID][index]['duration_sec'])) )
                g.add( (n['s' + str(switchID) + '_flow' + str(index)], n.actions, Literal(j[switchID][index]['actions'])) )
              
def getHosts(switchID):
        hosts = requests.get('http://localhost:8080/v1.0/topology/hosts/' + str(switchID))
        if not hosts:
                print 'there is currently no hosts.'
        else:
                hosts = hosts.json()
                hostCount = 0

                for item in hosts:
                        g.add( (n['s' + str(switchID)], n.hasHost, n['s' + str(switchID) + '_host' + str(hostCount)] ))
                        g.add( (n['s' + str(switchID) + '_host' + str(hostCount)], n.connectToPort, n['s' + str(switchID) + '_port' + item['port']['port_no'] ] ) )
                        g.add( (n['s' + str(switchID) + '_host' + str(hostCount)], n.hasIPv4, Literal(item['ipv4']) ) )
                        g.add( (n['s' + str(switchID) + '_host' + str(hostCount)], n.hasMAC, Literal(item['mac'])) )
                        if item['ipv6']:
                                g.add( (n['s' + str(switchID) + '_host' + str(hostCount)], n.hasIPv6, Literal(item['ipv6'])) )
                        hostCount = hostCount + 1
def writeToRDF(content, context, fname):
        g = Graph()
        print content, context
        g.parse(data=('[' + content + ']'), format='json-ld', context=context)
        print(g.serialize(format='n3'))

        with open('my_buffer/' + fname, 'a') as f:
                f.write(str(g.serialize(format='n3')))
        g.close()

getAllSwitches()
