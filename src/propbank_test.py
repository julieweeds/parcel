__author__ = 'juliewe'

from nltk.corpus import propbank
from xml.etree import ElementTree

n=103

if __name__=='__main__':
    pb_instances=propbank.instances()
    #print(pb_instances)
    instance=pb_instances[n]
    #print instance.roleset,instance.predicate,instance.arguments

    send_01=propbank.roleset('send.01')
    for role in send_01.findall("roles/role"):
        print role.attrib['n'],role.attrib['descr']

    #print (ElementTree.tostring(send_01.find('example')).decode('utf8').strip())
    examples=send_01.findall('example')
    print len(examples)
    for e in examples:
        print ElementTree.tostring(e).decode('utf8').strip()