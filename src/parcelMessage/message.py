__author__ = 'juliewe'

import sys,ConfigParser,ast

class Token:

    def __init__(self,labels,values):
        self.attributes={label:value for label,value in zip(labels,values)}

    def display(self):
        print self.attributes

class ParsedMessage:

    def __init__(self,labels,lines,id=0):
        self.id=id
        self.labels=labels
        self.linelist=lines
        self.tokens=[]

        self.processlines()


    def processlines(self):
        #print self.id,self.labels
        for line in self.linelist:
            #print line.rstrip()
            fields=line.rstrip().split('\t')
            self.tokens.append(Token(self.labels,fields))

    def display(self):
        #print self.id
        for token in self.tokens:
            token.display()


class Message:

    def __init__(self,id):

        self.id=id
        self.parsed=False
        return

    def setParse(self,labels,linelist):
        self.parsedMessage=ParsedMessage(labels,linelist,id=self.id)
        self.parsed=True


    def display(self):
        print self.id
        if self.parsed:
            self.parsedMessage.display()


class MessageCollection:

    def __init__(self):
        self.messages=[]

    def load_parses(self,labels,parsefile):

        self.labels=labels
        labellength=len(self.labels)
        linebuffer=[]
        id=0
        with open(parsefile) as instream:
            for line in instream:
                if len(line.rstrip().split('\t'))==labellength:
                    linebuffer.append(line)

                else:
                    thisMessage=Message(id)
                    thisMessage.setParse(self.labels,linebuffer)
                    self.messages.append(thisMessage)
                    linebuffer=[]
                    id+=1
    def display(self):
        for message in self.messages:
            message.display()


def run_tests(configfile):

    config=ConfigParser.RawConfigParser()
    config.read(configfile)
    run_testA(config)

def run_testA(config):

    myMessages=MessageCollection()
    myMessages.load_parses(ast.literal_eval(config.get('default','labels')),config.get('default','parsefile'))
    myMessages.display()

if __name__=='__main__':

    run_tests(sys.argv[1])
