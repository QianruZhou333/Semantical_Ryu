# Semantical_Ryu

topo_to ontology_mapper.py: A simple .py file to retrieve network element information (topology, flow entries, etc.) to RDF graphs with Ryu REST APIs. 

SPARQL_Engine.py: A demo of how to run SPARQL queries on the RDF graph generated.

my_connectAll.py: Three linked-data APIs:
  connectAll(): connect all the hosts with each other automatically
  addARPFlow(): add an ARP flood flow to the switch
  addFlow(dst, in_port, action_type, to_port): add an flow entry to the switch flow table.
