__author__ = 'juliewe'
#determine verb frames per verb e.g., in a given sentence
#also determine frequency over entire set of examples and most occurred

import sys,ConfigParser,os

class Sentence:
    #6+ column format
    #token, POS-tag, chunk, NE, sense label target verb, target-verb(s), SRL per target-verb

    def __init__(self,tmatrix):

        self.rowlist=tmatrix
        self.makecollist()


    def makecollist(self):
        #convert list of rows into list of columns
        no_cols=len(self.rowlist[0]) #should check they are all the same

        self.collist=[]
        for i in range(0,no_cols,1):
            self.collist.append([])
        #print len(self.collist),no_cols
        for row in self.rowlist:
            for(index,item) in enumerate(row):
                self.collist[index].append(item)

    def display(self):
        self.display_cols()

    def display_cols(self):

        for col in self.collist:
            print col

    def display_rows(self):

        for row in self.rowlist:
            print(row)

class FrameAnalyser:

    def __init__(self,configfile):
        self.parameters=ConfigParser.RawConfigParser()
        self.parameters.read(configfile)
        self.testing=int(self.parameters.get('default','testing'))

    def loadsentences(self):

        inputpath=os.path.join(self.parameters.get('default','parentdir'),self.parameters.get('default','datadir'),self.parameters.get('default','dataset'))

        with open(inputpath) as instream:
            processed=0
            fieldbuffer=[]
            for line in instream:
                fields=line.rstrip().split(' ')
                #print fields
                if len(fields)==1 and fields[0]=='':
                    thisSentence=Sentence(fieldbuffer)
                    thisSentence.display()
                    processed+=1
                    fieldbuffer=[]
                else:
                    fieldbuffer.append(fields)
                if self.testing>2 and processed>2:
                    break

    def run(self):
        self.loadsentences()


if __name__=='__main__':
    myAnalyser=FrameAnalyser(sys.argv[1])
    myAnalyser.run()


