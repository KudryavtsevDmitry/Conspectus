import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as ScrollTxt
from tkinter import END,E,W,filedialog
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize, RegexpTokenizer
import networkx as netx
import itertools
from collections import Counter
from math import tanh
from nltk.stem.snowball import SnowballStemmer
import fileinput

class MenuBarFrame(Tk.Frame):

    def __init__(self, master=None):
        Tk.Frame.__init__(self,master)
        self.grid(row=0,column=0,sticky=W+E)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1,weight=1)
        self.CreateWidgets()
        
    def CreateWidgets(self):
        menubar = Tk.Menu(self)
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open text",command=self.OpenFile)
        filemenu.add_command(label="Save text",command=self.SaveText)
        filemenu.add_command(label="Save summary",command=self.SaveSummary)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=MainWindow.destroy)
        menubar.add_cascade(label="File",menu=filemenu)
        self.master.config(menu=menubar)
        self.txtInptLbl = Tk.Label(self, text="Text for summarization:",anchor=W,width=10)
        self.txtInptLbl.grid(row=0,column=0,sticky=W+E)
        self.summaryLbl = Tk.Label(self, text="Summary:",anchor=W,width=10)
        self.summaryLbl.grid(row=0,column=1,sticky=W+E)

    def OpenFile(self):
        textBoxFrame.inputTxtBox.delete('1.0',END)
        openFile=filedialog.askopenfilename(parent=self,filetypes=[('text document (*.txt)','*.txt')])
        for l in fileinput.input(openFile):
            textBoxFrame.inputTxtBox.insert(END,l)

    def SaveText(self):
        saveText=filedialog.asksaveasfilename(parent=self,filetypes=[('text document (*.txt)','*.txt')],defaultextension='.txt')
        text=textBoxFrame.inputTxtBox.get('1.0',END)
        file=open(saveText,"w")
        file.write(text)
        file.close

    def SaveSummary(self):
        saveText=filedialog.asksaveasfilename(parent=self,filetypes=[('text document (*.txt)','*.txt')],defaultextension='.txt')
        text=textBoxFrame.outputTxtBox.get('1.0',END)
        file=open(saveText,"w")
        file.write(text)
        file.close

class TextBoxFrame(Tk.Frame):    

    def __init__(self, master=None):
        Tk.Frame.__init__(self,master)
        self.grid(row=1,column=0,sticky='w,e,s,n')
        self.CreateWidgets()
        self.ContextMenu()

    def CreateWidgets(self):
        self.inputTxtBox = ScrollTxt.ScrolledText(self,height=10,width=10,wrap=Tk.WORD)
        self.inputTxtBox.pack(side='left',fill=Tk.BOTH,expand=1)
        self.outputTxtBox = ScrollTxt.ScrolledText(self,height=10,width=10,wrap=Tk.WORD)
        self.outputTxtBox.pack(side='left',fill=Tk.BOTH,expand=1)

    def ContextMenu(self):
        self.contextMenu=Tk.Menu(self,tearoff=0)
        self.contextMenu.add_command(label="Cut",accelerator="CTRL+X",command=self.Cut)
        self.contextMenu.add_command(label="Copy",accelerator="CTRL+C",command=self.Copy)
        self.contextMenu.add_command(label="Paste",accelerator="CTRL+V",command=self.Paste)
        self.bind_class("Text","<Button-3>", self.Callback)

    def Callback(self,event):
        self.contextMenu.post(event.x_root, event.y_root)
        self.currentTextWidget=event.widget

    def Cut(self):
        self.currentTextWidget.event_generate("<<Cut>>")
        
    def Copy(self):
        self.currentTextWidget.event_generate("<<Copy>>")

    def Paste(self):
        self.currentTextWidget.event_generate("<<Paste>>")
        
class BottomButtonsFrame(Tk.Frame):

    def __init__(self, master=None):
        Tk.Frame.__init__(self,master,)
        self.grid(row=2,column=0,sticky=W+E)
        self.CompressRate=50
        self.LangSupport=[]
        self.stemLang='English'
        for lang in SnowballStemmer.languages:
            if (lang!='porter'):
                self.LangSupport.append(lang[0].upper()+lang[1:])
        self.CreateWidgets() 
        
    def CreateWidgets(self):        
        self.Summarize = Tk.Button(self, text="Summarize",width=10,command=ComputeSummary)
        self.Summarize.grid(row=0)
        self.LangLabel = Tk.Label(self, text="Language:")
        self.LangLabel.grid(row=0,column=1)
        self.CmbBx = ttk.Combobox(self,values=self.LangSupport,state='readonly')
        self.CmbBx.set(self.stemLang)
        self.CmbBx.grid(row=0,column=2)
        self.CmbBx.bind("<<ComboboxSelected>>",self.CmbBxValue)
        self.RatioLabel = Tk.Label(self, text="Compress percent:")
        self.RatioLabel.grid(row=1,column=1)
        self.CmbBxRt = ttk.Combobox(self,values=list(range(10,100,10)),state='readonly')
        self.CmbBxRt.set(self.CompressRate)
        self.CmbBxRt.bind("<<ComboboxSelected>>",self.CmbBxRtValue)
        self.CmbBxRt.grid(row=1,column=2)
        self.LangLabel.grid(row=0,column=1)         
        self.Exit = Tk.Button(self, text="Exit",width=10,command=MainWindow.destroy)
        self.Exit.grid(row=1)

    def CmbBxRtValue(self,event):
        self.CompressRate=(self.CmbBxRt.get())                  
    
    def CmbBxValue(self, event):
        self.stemLang=(self.CmbBx.get())         

def ComputeSummary():   
     textBoxFrame.outputTxtBox.delete('1.0', END)
     setOfSent=sent_tokenize(textBoxFrame.inputTxtBox.get("1.0",END)) 
     textGraph=netx.Graph()        
     orderList=[]

     for i in range(0,len(setOfSent)):
         orderList.append((i+1,{'sentence':setOfSent[i],'spdUpW':0,'AlphThresold':0}))
     textGraph.add_nodes_from(orderList)
     sentPairs=list(itertools.combinations(orderList,2)) 

     for ((sntNum1,snt1),(sntNum2,snt2)) in sentPairs:
         phrasalOvrlpScore=PhrasalOverlap(snt1['sentence'],snt2['sentence'])
         if phrasalOvrlpScore>0:
             textGraph.add_edge(sntNum1,sntNum2,weight=phrasalOvrlpScore)
     remainTextGraph=textGraph.copy()
     RmnTextList=remainTextGraph.nodes()

     for (n1,n2,snt) in textGraph.edges(data=True):         
         textGraph.node[n1]['AlphThresold']+=0.75*snt['weight']   
     summaryList=[]
     summaryLength=0
     summaryList=[]     

     while summaryLength<(((int(bottomButtonsFrame.CompressRate)/100)*len(textGraph))):
         sntMaxWght=0
         maxNode=0
         maxWghtRmnSnt=''
         for n,atr in remainTextGraph.nodes(data=True):
             atr['sntWgt']=0
         for snt,wht in remainTextGraph.nodes(data=True):
             for (n1,n2,wgh) in textGraph.edges(nbunch=snt,data=True):          
                     remainTextGraph.node[snt]['sntWgt']+=(wgh['weight']+textGraph.node[n2]['spdUpW'])                
         for sent,atr in remainTextGraph.nodes(data=True):       
             if atr['sntWgt']>sntMaxWght:
                 sntMaxWght=atr['sntWgt']
                 maxNode=sent
                 maxWghtRmnSnt=atr['sentence']         
         summaryList.append((maxNode,maxWghtRmnSnt))
         remainTextGraph.remove_node(maxNode)
         for n,atr in textGraph.nodes(data=True):
             weight=PhrasalOverlap(maxWghtRmnSnt,atr['sentence'])
             atr['spdUpW']+=weight
         simOfSumm=0        
         summaryLength+=1

     sortedSummary = sorted(summaryList, key=lambda tup: tup[0])
     finalSummary=''
     for n,s in sortedSummary:
         finalSummary+=(s+' ')
     textBoxFrame.outputTxtBox.insert(END,finalSummary)
     
     
def PhrasalOverlap(fstSent,sndSent):

     stemmer = SnowballStemmer(bottomButtonsFrame.stemLang[0].lower()+bottomButtonsFrame.stemLang[1:])
     tokenizer=RegexpTokenizer(r"\w+")
     cnt1=Counter()
     cnt2=Counter()
     s1=tokenizer.tokenize(fstSent)
     s2=tokenizer.tokenize(sndSent)     
     for n in range(0,len(s1)):
         s1[n]=stemmer.stem(s1[n])
     for n in range(0,len(s2)):
         s2[n]=stemmer.stem(s2[n])
     ovrlpScore=0
     for n in range(1,len(s1)):
         for i in range(len(s1)-(n-1)):
             cnt1[' '.join(s1[i:i+n])]+=1
         for j in range(len(s2)-(n-1)):
             cnt2[' '.join(s2[j:j+n])]+=1    
         interSec=(cnt1&cnt2)        
         if sum(interSec.values())==0:
             break
         ovrlpScore+=(sum(interSec.values()))*n**2       
         cnt1.clear()
         cnt2.clear()
     ovrlpScore=tanh(ovrlpScore/(len(s1)+len(s2)))
     return ovrlpScore

MainWindow = Tk.Tk()
MainWindow.title("Conspectus")
MainWindow.minsize(800,500)
MainWindow.columnconfigure(0,weight=1)
MainWindow.rowconfigure(0, weight=0)
MainWindow.rowconfigure(1, weight=1)
MainWindow.rowconfigure(2, weight=0)
menuBarFrame = MenuBarFrame(master=MainWindow)
textBoxFrame=TextBoxFrame(master=MainWindow)
bottomButtonsFrame=BottomButtonsFrame(master=MainWindow)
MainWindow.mainloop()


