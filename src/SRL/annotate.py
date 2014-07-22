__author__ = 'juliewe'

from nltk.corpus import propbank as pb
import ConfigParser,sys,ast
from xml.etree import ElementTree
import re,os

whitespacePATT=re.compile('(.*)\n')
rpunctPATT=re.compile('(.*)([,\.;]+$)')
lpunctPATT=re.compile('^([,\.;]+)(.*)')
tracePATT=re.compile('\*trace\*(.*)')
chainPATT=re.compile('-&gt')

def removewhitespace(tokenlist):

    newlist=[]
    for t in tokenlist:
        matchobj=whitespacePATT.match(t)  #identify and remove whitespace
        if matchobj:
            t=matchobj.group(1)

        if len(t)>0:
            newlist.append(t)
    return newlist

def removetrace(tokenlist):
    newlist=[]
    for t in tokenlist:
        matchobj=tracePATT.match(t)  #identify and remove *trace* tokens which aren't in actual text
        if matchobj:
            t=matchobj.group(1)
        if len(t)>0:
            newlist.append(t)
    return newlist


def retokenise(tokenlist):
    newlist=[]
    for t in tokenlist:
        lp=''
        rp=''
        matchobj=rpunctPATT.match(t)
        if matchobj:
            (t,rp)=(matchobj.group(1),matchobj.group(2))
        matchobj=lpunctPATT.match(t)
        if matchobj:
            (lp,t)=(matchobj.group(1),matchobj.group(2))
        if len(lp)>0:
            newlist+=list(lp)
        if len(t)>0:
            newlist.append(t)
        if len(rp)>0:
            newlist+=list(rp)
    return newlist



class Argument:

    def __init__(self,namelist,textlist):
        self.namelist=namelist #list of tuples
        self.textlist=textlist
        self.inpointer=0
        self.completed=False
        self.followtraces()

    def name(self):

        namestring=self.namelist[0][0]+':'+self.namelist[0][1]
        for name in self.namelist[1:]:
            namestring+=', '+name[0]+':'+name[1]
        return namestring

    def followtraces(self):
        if self.textlist[0]=='*trace*':
            #self.textlist=self.textlist[2:]
            lastindex=0
            for (index,item) in enumerate(self.textlist):
                if item=='->':
                    lastindex=index
            self.textlist=self.textlist[lastindex+1:]
            self.traced="T"
        else:
            self.traced="NT"

    def display(self):
        print self.name()
        #print self.namelist
        print self.textlist

    def greedymatch(self,index,tokens,tags):

        match=False

        match=True
        newindex=index
        while self.inpointer<len(self.textlist) and match==True:
            if tokens[newindex]==self.textlist[self.inpointer]:
                self.inpointer+=1
                newindex+=1
            else:
                match=False

        if match:
            while index<newindex:
                tags[index]=(self.name(),self.traced)
                index+=1
        self.completed=match
        self.inpointer = 0 #restart next time and allow multiple matches


        return(index,tags,match)

class Example:

    def __init__(self,e):
        #input e is an ElementTree
        self.etree = e
        self.annotated=False

    def annotate(self):

        self.display()
        self.text=self.etree.find('text').text.rstrip()
        alltokens=self.text.split(' ')
        self.tokens=retokenise(removetrace(removewhitespace(alltokens)))

        #print self.tokens

        self.rel=self.etree.find('rel').text.rstrip()
        #print self.rel
        args=self.etree.findall('arg')
        self.args={}
        for arg in args:
            names=arg.attrib.keys()
            namelist=[]
            for name in names:
                value=arg.attrib[name]
                namelist.append((name,value))
            argtext=arg.text.rstrip().split(' ')
            argtext=retokenise(removewhitespace(argtext))
            namedArgument=Argument(namelist,argtext)
            #namedArgument.display()
            self.args[namedArgument.name()]=namedArgument
        rel = Argument([('rel',self.rel)],[self.rel])
        self.args[rel.name()]=rel

        for arg in self.args.values():
            arg.display()

        self.process()
        self.annotated=True



    def process(self):
        index=0
        self.tags=[]
        while len(self.tags)<len(self.tokens):
            self.tags.append(('O','NT'))

        while index<len(self.tokens):
            #print self.tokens[index]
            matched=False
            for arg in self.args.values():
                if not matched:
                    #greedily try to match each argument to stretch of tokens
                    (index,self.tags,matched)=arg.greedymatch(index,self.tokens,self.tags)

            if not matched:
                index +=1 #leaves tag as 'O' if not matched
        #for (token,tag)in zip(self.tokens,self.tags):
        #    print token+':'+tag

    def write_to_file(self,outstream):
        if not self.annotated:
            self.annotate()

        print self.tokens
        print self.tags
        for(index,token) in enumerate(self.tokens):
            outstream.write(str(index+1)+'\t'+self.tokens[index]+'\t'+self.tags[index][0]+'\t'+self.tags[index][1]+'\n')
        outstream.write('\n')


    def display(self):
        print ElementTree.tostring(self.etree).decode('utf8').strip()

class Annotator:

    def __init__(self,configfile):
        parameters=ConfigParser.RawConfigParser()
        parameters.read(configfile)
        self.testing=int(parameters.get('default','testing'))
        #print self.testing
        self.outfile=os.path.join(parameters.get('default','parentdir'),parameters.get('default','outdatafile'))

    def findexamples(self):
        self.allexamples=[]
        processed=0
        for instance in pb.instances():
            if self.testing>5:
                print instance.roleset
                print instance.arguments
            try:
                roleset=pb.roleset(instance.roleset)
                examples=roleset.findall('example')
                for e in examples:
                    #print ElementTree.tostring(e).decode('utf8').strip()
                    self.allexamples.append(e)
            except:
                pass
            processed+=1
            if self.testing > 2 and processed>10:
                break
        print "Number of examples: ",len(self.allexamples)

    def annotate(self):

        with open(self.outfile,'w') as outstream:
            processed=0
            for e in self.allexamples:
                thisExample=Example(e)
                thisExample.annotate()
                thisExample.write_to_file(outstream)

                processed+=1
                if self.testing>4 and processed>4:
                    break



    def run(self):
        self.findexamples()
        self.annotate()
if __name__=='__main__':

    myAnnotator=Annotator(sys.argv[1])
    myAnnotator.run()
