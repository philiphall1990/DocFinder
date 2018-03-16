import PyQt5
from PyQt5 import Qt
from PyQt5 import *
from PyQt5.Qt import QPoint, QCursor, QGuiApplication, QWindow,QApplication, QMainWindow,QWebView, QLineEdit,QInputMethodEvent, QInputEvent, QFocusEvent,QMetaMethod,QObject,QUrl
from PyQt5.QtCore import pyqtBoundSignal,pyqtSignal, pyqtSlot
from urllib import urlopen
import sys, json
import re
import functools
import time

class MyMainWindow(QMainWindow):
    def __init__(self,Parent=None):
        QMainWindow.__init__(self) #self? MyMainWindow.__init
        self.setWindowOpacity(0.6)
        self.setBaseSize(3000,3000) 
        self.setVisible(True)
        self.setMinimumSize(400,400)

        
class MyWebView(QWebView):
    
    newClpbdTextData = pyqtSignal(str,name='newClpbdTextData',arguments='txt')
     
    def __init__(self,Parent=None):
        QWebView.__init__(self)
        self.setHtml(str(myS))
        self.setVisible(True)
        self.setWindowOpacity(0.8)
        
      
        
    @pyqtSlot(name='onDataChanged')
    def onDataChanged(self):
        txt = QGuiApplication.clipboard().text()
        if txt is not None or len(txt) == 0:
            self.newClpbdTextData.emit(str(txt))
            

    def mousePosition(self,e):
        p = self.mapToGlobal(QCursor.pos())
        (px,py) = (p.x(),p.y())
        ((xy),(wh)) = self.setGeoVars()
        (x,y,w,h) = (xy.x(),xy.y(),wh.x(),wh.y())
        if (px in range(x,w) or py in range(y,h)):
            self.setWindowOpacity(0.9)
        self.beginFade()
        
    
    def setGeoVars(self):
            return (self.mapToGlobal(self.pos()), self.mapToGlobal(QPoint(self.pos().x()+self.width(),self.pos().y() + self.height())))  
        
        
    def mouseMoveEvent(self,e):
        if self.hasFocus():
            self.mousePosition(e)
            return super(MyWebView,self).mouseMoveEvent(e)

    
    @pyqtSlot(str,name='handleText')
    def handleText(self,input):
        sources = [] 
        html = ""
        repo_part = ""
        keywords = input.split('.')
        js = buildReqString(keywords[1],keywords[0])
        sources.append(parser(js))
        otherhtml = githubget(keywords[1],keywords[0], repo_part)
        sources.append(otherhtml)
        for items in sources:
            html += items
        self.setHtml(html)
        self.beginFade()


    def beginFade(self):
        opac = self.windowOpacity()
        intervals = opac / 100
        for i in range(0,100):
            app.sendPostedEvents()
            if self.windowOpacity() >= 0.4:
                opac -= intervals   
                self.setWindowOpacity(opac)
                time.sleep(0.05)


  
class MyLineEdit(QLineEdit):
    
    inputTyped = pyqtSignal(str, name='self.inputTyped',arguments='input')
 
    def __init__(self,Parent=None):
        QLineEdit.__init__(self)
        self.setVisible(True)
        self.setEnabled(True)
        self.previousText = ""
       
       
    def focusOutEvent(self, e):
        if e.lostFocus() and len(self.text()) > 0 and self.text() != self.previousText: 
            self.inputTyped.emit(self.text())
            self.previousText = self.text()
            return super(MyLineEdit,self).focusOutEvent(e)
        return None


    @pyqtSlot(str,name='handleClpbrdText')
    def handleClpbrdText(self,txt):
        self.setText(txt)
        self.inputTyped.emit(self.text())
        


    
        
def buildReqString(query,proj,vers="latest",command="docsearch",language="en"):		
    base= "http://readthedocs.org/api/v2/{0}/?{1}"
    var_pattern= "{0}={1}&"
    base_var_names = ["q","project","version", "language"]
    names_ordered = True
    vals = [query,proj,vers,language]
    s = ""
    for n in range(len(base_var_names)):
        s += str.format(var_pattern,base_var_names[n],vals[n]).lower()
    s = s.rstrip('&')      
    try:
        return urlopen(str.format(base,command,s)).read()
    except: 
        return None


def parser(json_result):
    outstr = ""
    if (json_result is None) or ("Project not found" in str(json_result)) or (not "{" in  str(json_result) and not ":" in str(json_result)):
        return "<h3>No results, sorry.</h3>"
    try:
        results = json.loads(json_result)['results']['hits']['hits']
    except:
        print("sorry, could not parse results.")
    for r in results:
        if r['_type'] == 'page':
            outstr +='<h3>' + str(r['fields']['title'][0].replace("['","")) + '</h3>'

            for e in r['highlight']['content']:
               outstr += e + '</br>'
            outstr += r['fields']['link']
    return outstr


def searchRepo(query, proj, repo_part,  plang='Python', base_url = "http://readthedocs.org/api/v1/project/"):
    prefix = "<h3> Snippets from library repo <h3></br>" 
    try:
        html = prefix + str(urlopen('https://github.com/{0}/search?utf8=true&q={1}&l={2}'.format(repo_part,query,plang)).read())
    except:
        return "<h3>No results, sorry.</h3>"
    return html



def format_github(html, repo_part):
    patt = re.compile("<div class=\"code-list-item.*?\"code-list-item")
    matches= re.findall(patt,html)
    newhtml = ""
    for x in matches:
        newhtml += "<code>" +  x.replace("\\n","").rpartition("</div>")[0] + "</code>"
    return newhtml

def categorise(code,query):
    counter = {'module' : 0, 'class': 0,'withparams': 0, 'woutparams' : 0, 'variable':0}
    pattern = re.compile(str.format("(.){0}(.)(.)",query))
    pattern2 = re.compile(str.format("^.*{0}.*$",query))
    result = re.findall(pattern,code)
    for e in result:
        if e[0] == " ":
            counter.update({query: 'module'})
        elif e[0] == "\.":
            if e[1] == "\(":
                 if e[2] == "\)":
                    counter.update({query: 'woutparams'})
                 else:
                    counter.update({query: 'withparams'})
            else:
                 counter['class']+=1
    #    if e[1] in [" ","\n"]:
    #if counter{'module'} == max(counter):

    return result
        
def google_codesearch(keywords):
    for word in keywords:
        print(urlopen("https://www.duckduckgo.com/search?q=%2B%22" + word + "%22+AND+%28%28%22%7B%22+OR+%22%3A%22+OR+%22%28%22+OR+%22%5B%22%29+OR+%28%22function%28%22+OR+%22def%22+OR+%22void%22+OR+%22int%22+OR+%22string%22%29++OR+%28%22class%22+OR+%22new%22%29%29").read())


def githubget(q,p, repo_part):
    base_url='http://readthedocs.org/api/v1/project/' + p
    try:
        repo_part = json.loads(urlopen(base_url).read())['repo'].replace("http://github.com","").strip("/")
    except:
        return "<h3>No results, sorry.</h3>"
    html = searchRepo(q,p,repo_part,base_url=base_url)
    output = format_github(html,repo_part)
    categorise(output,q)
    output = '<div onMouseOver=\"this.style.backgroundColor = \'#FFF0FF\';\" onMouseOut=\"this.style.backgroundColor = \'#FFFFFF\';\">' + output +'</div>'
    return output



app = QApplication(sys.argv)
myS = "<p>start</p>"
webview = MyWebView()
ledit = MyLineEdit(webview)
ledit.setFixedSize(100,40)
ledit.setEnabled(True)
ledit.setVisible(True)
ledit.inputTyped.connect(webview.handleText)
QGuiApplication.clipboard().dataChanged.connect(webview.onDataChanged)
webview.newClpbdTextData.connect(ledit.handleClpbrdText)
webview.show()
app.exec_()

