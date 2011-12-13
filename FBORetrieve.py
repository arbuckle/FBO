from Tkinter import *
import urllib, urllib2
import win32clipboard as w, win32con, random
from BeautifulSoup import BeautifulSoup

import tkMessageBox
import cookielib

Cookie = None 


class Workers:

    d = True

    def logit (self , url):
        f = open('log.txt' , 'a')
        f . write ('%s\n' % url)
        f.close()

    def BuildRequest ( self , url ):    #(url, values)
        userAgent = 'FBORET'
        try:
            url = urllib . unquote ( url + '&tab=ivl')
            values = {}
            data = urllib . urlencode (values) # for inhouse querying

            print 'BuildRequest | request built: ' , url
            self . logit(url)## logging URL
            return urllib2 . Request ( url , data, {'User-agent': userAgent} )
        except:
            print 'BuildRequest | Error'



    def GetPage ( self , request ): #opens URL (request) and reads into 'document', records time elapsed for page load.
        try:
            global Cookie
            cj = cookielib . CookieJar()

            if Cookie == None:  #Cookie handling.  Checks for cookie, sets one up if it doesn't exist.  Appends cookie to request for all subsequent requests.
                opener = urllib2 . build_opener ( urllib2.HTTPCookieProcessor ( cj ) )
                urllib2 . install_opener ( opener )
                Cookie = cj
                cj . add_cookie_header ( request )
                print 'NEW COOKIE SET'
            else:
                cj . add_cookie_header ( request )


            response = urllib2 . urlopen ( request )
            output = response . read ()


            print 'GetPage | page loaded '
            return output # outputs the http response, the url requested, and the server response time
        except:
            print 'GetPage | Error'


    def MakeSoup ( self , document ):   # Normalize page to be accessible via objects
        try:
            soup = BeautifulSoup ( document )
            print 'MakeSoup | page converted into soup for GetLinks processing'
            return soup
        except:
            print 'MakeSoup| Error'



    def GetData ( self , soup ):
        
        ####### Search Criteria ########
        emails = soup("td" , {'headers' : 'lh_contractor_name'})
        lnames = soup("td" , {'headers' : 'lh_lname'})
        fnames = soup("td" , {'headers' : 'lh_fname'})
        
        #print fnames , '\n\n' , emails
        
        i = 0
        output = []
        fulloutput = []
        while i < len(fnames):
            try:
                coname = str( emails[i] . contents[1] . contents [0] )
                email = str ( emails[i] . contents[6]['href'] )
                fname = str( fnames[i] . contents[0] )
                lname = str( lnames[i] . contents[0] )
                phone = str( emails[i] . contents[8] )
                #print coname , email , lname , fname , phone

            except:
                print "error parsing webpage"
            
            fname= fname. strip()
            fname= fname. capitalize()
            lname= lname . strip ()
            lname= lname . capitalize()
            email = email . replace ( 'mailto:' , '')
            phone = phone . replace ('Phone: ' , '')
            
            print lname
            
            contact = email , '\t' , fname, '\n'
            fullinfo = coname , '\t' , email , '\t' , lname , '\t' , fname , '\t' , phone # to be output to clipboard...

            output . append ( contact )
            fulloutput . append ( fullinfo )
            i += 1

        if len(fnames) == len(emails):
            print 'GetData | parse successful.  results passed'
            return output , fulloutput
        else:
            print 'GetData | ERROR Array mismatch.  Emails and names may not be correctly matched.'
            return output

    def WriteData ( self , url):
        #url = 'https://www.fbo.gov/index?s=opportunity&mode=form&id=073ff6fe46d64e222fa01bad1ddeba73&tab=ivl&tabmode=list'
        result = self . GetData ( self . MakeSoup ( self . GetPage ( self . BuildRequest ( url ) ) ) )
        for i in result:
            #print i[0] , i[1] , i[2]
            pass
        print 'done'
        return result
            





class MyApp:
    def __init__(self, parent):
        self.myParent = parent

        ######### Convoluted input box frames, button
        self.inputframe = Frame(parent , padx = 50 , pady = 5)
        self.inputframe.pack()

        self.container = Frame(self.inputframe , padx = 5 , pady = 10) 
        self.container.pack(side=RIGHT)
        
        self.aboutlabel = Label(self.inputframe , text = "Enter the link to any 'interested vendors list' on FBO.Gov.\n Tip: Use Auto to follow the link in your clipboard and automatically save the results for pasting" )
        self.aboutlabel.pack (side=TOP)
        
        self.inputlabel = Label(self.inputframe , text = "Link:") #url label
        self.inputlabel.pack(side = LEFT)

        self.inputwidget = Entry(self.inputframe)  #textbox for URL input
        self.inputwidget.configure(width = 80)
        self.inputwidget.bind("<Return>",self.okClick_a)
        self.inputwidget.bind("<Button-3>",self.do_rclick)
        self.inputwidget.pack(side = LEFT)

        self.button1 = Button(self.inputframe , command=self.okClick) # ok button
        self.button1.bind("<Return>", self.okClick_a)    ### (1)
        self.button1.configure(text="OK")

        self.autobutton = Button(self.inputframe , padx = 8 , command=self.autoClick) # Auto button, automatically grabs clipboard and attempts to follow
        self.autobutton.bind("<Return>" , self.autoClick_a)
        self.autobutton.configure(text="Auto")
        self.autobutton.pack(side=RIGHT)
        self.button1.pack(side=RIGHT)
        
        ########### Right-click menus, divorced from any frame
        self.rclick = Menu(parent , tearoff=0) #####Right Click context menus for input widget
        self.rclick.add_command(label="Paste" , command = self.icbPaste) #command=...  for paste
        self.rclick.add_command(label="Copy All" , command = self.icbCopy) #command=...  for paste
        self.rclick.add_separator()
        self.rclick.add_command(label="Clear" , command = self.iClear)

        self.rclick_r = Menu(parent , tearoff=0) #####Right Click context menus for input widget
        self.rclick_r.add_command(label="Paste" , command = self.rcbPaste) #command=...  for paste
        self.rclick_r.add_command(label="Copy All" , command = self.rcbCopy) #command=...  for paste
        self.rclick_r.add_separator()
        self.rclick_r.add_command(label="Clear" , command = self.rClear)


        ######### Frame contains results textbox, scrollbar.
        self.resultsframe = Frame(parent , padx = 20 , pady = 20)
        self.resultsframe.pack()
        
        self.results = Text(self.resultsframe)
        self.results.bind("<Button-3>",self.do_rclick_r)
        self.results.pack(side=LEFT)

        self.scrollbar = Scrollbar(self.resultsframe)
        self.scrollbar.pack(side=RIGHT,fill=Y)
        self.scrollbar.config(command=self.results.yview)
        self.results.configure(yscrollcommand=self.scrollbar.set)


    


        ######### Frame containing quit button.  
        self.quitcontainer = Frame(parent , padx = 2 , pady = 2)
        self.quitcontainer.pack(side=RIGHT)

        self.button2 = Button(self.quitcontainer, command=self.QuitClick)
        self.button2.bind("<Return>", self.QuitClick_a)    ### (1)
        self.button2.configure(text="Quit")
        self.button2.pack(side=RIGHT)
        self.button2.focus_force()


################# Primary output function. Launches URL search and retrieves results
    def Output (self , url , n): ###### Output results to text field
        output  = Workers () . WriteData ( url )
        fullinfo = output[1]
        output = output[0]
        for i in output:
            self.results.insert(END , i[0])
            self.results.insert(END , "\t")
            self.results.insert(END , i[2])
            self.results.insert(END , "\n")
        
        if n == 1: self.fulltoCB(fullinfo) # autocopy after data is retrieved



################Copy/Paste/Clear functions used in right-click menus

    def fulltoCB (self , data):
        w . OpenClipboard()
        w . EmptyClipboard()
        cbstring = ''
        for i in data:
            for j in i:
                cbstring += j    # accepts data list and breaks it down into a string to be output to clipboard.
        #print cbstring
        w . SetClipboardText(cbstring)
        w . CloseClipboard()

    def icbCopy (self):
        w . OpenClipboard()
        w . EmptyClipboard()
        w . SetClipboardText(self . inputwidget . get())
        w . CloseClipboard()
    def rcbCopy (self):
        w . OpenClipboard()
        w . EmptyClipboard()
        w . SetClipboardText(self . results . get ( "@0,0" , END))
        w . CloseClipboard()

    def icbPaste (self):
        w . OpenClipboard()
        data = w . GetClipboardData(w.CF_UNICODETEXT)
        w . CloseClipboard()
        self.inputwidget.insert (INSERT , data)
    def rcbPaste (self):
        w . OpenClipboard()
        data = w . GetClipboardData(w.CF_UNICODETEXT)
        w . CloseClipboard()
        self.results.insert (INSERT , data)
        
    def iClear (self):
        self.inputwidget.delete(0,END)
    def rClear (self):
        self.results.delete("@0,0",END)
    

################## right-click event functions for launching the context menu
    def do_rclick (self , event): # launches rightclik menu
        try:
            self.rclick.tk_popup(event.x_root+40, event.y_root, 0)
            print "do_rclick event handler"
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.rclick.grab_release()

    def do_rclick_r (self , event): # launches rightclik menu
        try:
            self.rclick_r.tk_popup(event.x_root+40, event.y_root, 0)
            print "do_rclick_r event handler"
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.rclick_r.grab_release()

###################  URL Submission event handlers
    def okClick(self):  ### (2)
        print "okClick event handler"
        #Workers () . WriteData ()
        data = self.inputwidget.get().strip()
        if "fbo.gov" in data:
            self . Output ( data , 0)
        else:
            tkMessageBox.showinfo("URL Input Error", "Please enter a valid URL\n The below URL is considered invalid: \n\n (%s)" % data)
    def okClick_a(self, event):  ### (3)
        print "okClick_a event handler (a wrapper)"
        self.okClick()
        

    def autoClick(self):  ### (2)
        print "autoClick event handler"
        current = self.inputwidget.get().strip() # existing contents
        
        w . OpenClipboard()
        data = w . GetClipboardData(w.CF_UNICODETEXT)
        w . CloseClipboard()

        if "fbo.gov" in data:
            self.rClear()
            self.inputwidget.delete(0,END)
            self.inputwidget.insert (INSERT , data)
            self . Output ( data , 1)
        else:
            self.inputwidget.insert (INSERT , current)
            tkMessageBox.showinfo("URL Input Error", "Please enter a valid URL\n The below URL is considered invalid: \n\n (%s)" % data)

    def autoClick_a(self, event):  ### (3)
        print "autoClick event handler (a wrapper)"
        self.autoClick()


#################### QUIT Event Handlers
    def QuitClick(self): ### (2)
        print "QuitClick event handler"
        self.myParent.destroy()

    def QuitClick_a(self, event):  ### (3)
        print "QuitClick_a event handler (a wrapper)"
        self.QuitClick()





root = Tk()
root.title("FBO Extended Retrieval Tool")
#root.wm_iconbitmap('FBORetrieve.ico')
myapp = MyApp(root)
root.mainloop()
