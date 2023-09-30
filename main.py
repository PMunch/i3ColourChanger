from colour import Color
import wx
import wx.lib.scrolledpanel
import i3ipc
import math
import os
import string

def colourChanged(e,oldColour):
	if type(e)==str:
		return e
	elif type(e)==Color:
		nc = [e.red*255,e.green*255,e.blue*255]
	else:
		nc = e.GetColour()
	if type(oldColour) is not Color:
		oldColour = Color()
	oldColour.red = nc[0]/255
	oldColour.green = nc[1]/255
	oldColour.blue = nc[2]/255
	return oldColour

class ColourClass:
	def __init__(self,border,background,text,indicator=None):
		self.border = border
		self.background = background
		self.text = text
		self.indicator = indicator
	def namedColour(self,name):
		if name=="Background":
			return self.background
		elif name=="Border":
			return self.border
		elif name=="Text":
			return self.text
		elif name=="Indicator":
			return self.indicator

class I3bar:
	def __init__(self,background,statusline,separator,colourClasses):
		self.background = background
		self.statusline = statusline
		self.separator = separator
		self.colourClasses = colourClasses
	def namedColour(self,name):
		if name=="Background":
			return self.background
		elif name=="Status line":
			return self.statusline
		elif name=="Separator":
			return self.separator

class MainWindow(wx.Frame):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(title="i3 Colour Changer",*args,**kwargs)
		self.InitUI()
		self.messager = Messager(100,1, self)
		self.config = None

	def InitUI(self,config=None):
		artprovider = wx.ArtProvider()
		toolbar = self.CreateToolBar(style=wx.TB_TEXT|wx.TB_HORZ_LAYOUT)
		toolOpen = toolbar.AddTool(wx.ID_ANY, 'Open', artprovider.GetBitmap(wx.ART_FILE_OPEN,client=wx.ART_TOOLBAR),"Open an i3 config file")
		toolSave = toolbar.AddTool(wx.ID_ANY, 'Save', artprovider.GetBitmap(wx.ART_FILE_SAVE,client=wx.ART_TOOLBAR),"Save the current settings to the open file")
		toolApply = toolbar.AddTool(wx.ID_ANY, 'Apply', artprovider.GetBitmap(wx.ART_TICK_MARK,client=wx.ART_TOOLBAR),"Apply the changes without changing file")
		toolUpdateLocal = toolbar.AddTool(wx.ID_ANY, 'Save to config', artprovider.GetBitmap(wx.ART_FILE_SAVE_AS,client=wx.ART_TOOLBAR),"Save the current colour scheme into your current config")
		toolSnippet = toolbar.AddTool(wx.ID_ANY, 'Create colour snippet', artprovider.GetBitmap(wx.ART_NEW,client=wx.ART_TOOLBAR),"Save the current colour scheme as a standalone colour file you can send to others")
		toolVariable = toolbar.AddTool(wx.ID_ANY, 'Create colour variable', artprovider.GetBitmap(wx.ART_PLUS,client=wx.ART_TOOLBAR),"Create a new colour variable")
		toolbar.AddStretchableSpace()
		toolQuit = toolbar.AddTool(wx.ID_ANY, 'Quit', artprovider.GetBitmap(wx.ART_QUIT,client=wx.ART_TOOLBAR),"Quit the program")

		self.Bind(wx.EVT_TOOL, self.OnQuit,toolQuit)
		self.Bind(wx.EVT_TOOL, self.OnOpen,toolOpen)
		self.Bind(wx.EVT_TOOL, self.OnApply,toolApply)
		self.Bind(wx.EVT_TOOL, self.OnSave,toolSave)
		self.Bind(wx.EVT_TOOL, self.OnUpdateLocal,toolUpdateLocal)
		self.Bind(wx.EVT_TOOL, self.OnCreateSnippet,toolSnippet)
		self.Bind(wx.EVT_TOOL, self.OnCreateVariable,toolVariable)

		self.scrolled = wx.lib.scrolledpanel.ScrolledPanel(self,-1)
		self.scrolled.SetupScrolling()
		self.scrolled.Show()

		self.Centre()
		self.Show(True)

		if config!=None:
			self.LoadConfig(config)

	def LoadConfig(self,config):
		self.config = config
		self.scrolled.DestroyChildren()
		vbox = wx.BoxSizer(wx.VERTICAL)
		if config.setColours:
			setStaticBox = wx.StaticBox(self.scrolled,label="Colour variables")
			setStaticBoxSizer = wx.StaticBoxSizer(setStaticBox,wx.VERTICAL)
			
			fgs = wx.FlexGridSizer(math.ceil(len(config.setColours)/2),6,15,25)
			for setColour in sorted(config.setColours):
				fgs.Add(wx.StaticText(self.scrolled,label=setColour[1:]))
				colour = config.setColours[setColour]
				cp = wx.ColourPickerCtrl(self.scrolled,colour=(config.setColours[colour].hex if type(colour) != Color else colour.hex))
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, name=setColour:self.SetColourChanged(e,name) ,cp)
				fgs.Add(cp)
				b = wx.BitmapButton(self.scrolled,bitmap=wx.ArtProvider().GetBitmap(wx.ART_DELETE))
				self.Bind(wx.EVT_BUTTON,lambda e, name=setColour:self.SetColourChanged(e,name),b)
				fgs.Add(b)
			fgs.AddGrowableCol(2,1)
			fgs.AddGrowableCol(5,1)
			setStaticBoxSizer.Add(fgs,proportion=0, flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.EXPAND, border = 15)
			vbox.Add(setStaticBoxSizer,proportion=0, flag=wx.RIGHT|wx.LEFT|wx.EXPAND,border=5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		winStaticBox = wx.StaticBox(self.scrolled,label="Windows")
		winStaticBoxSizer = wx.StaticBoxSizer(winStaticBox,wx.VERTICAL)

		fgs = wx.FlexGridSizer(1,3,9,25)
		
		fgs.Add(wx.StaticText(self.scrolled,label="Background"),0,0)
		cp = wx.ColourPickerCtrl(self.scrolled,colour=config.background.hex if type(config.background) == Color else config.setColours[config.background].hex)
		self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.backgroundChanged,cp)
		fgs.Add(cp,0,0)
		cb = wx.ComboBox(self.scrolled,value="Individual colour" if type(config.background) == Color else config.background[1:],choices=["Individual colour"]+sorted(map(lambda n: n[1:],list(config.setColours.keys()))))
		fgs.Add(cb)
		self.Bind(wx.EVT_COMBOBOX,lambda e, p=cp.GetId(): self.OnColourChange(e, pickerId=p, name="Background"),cb)
		if type(config.background) != Color:
			cp.Disable()

		fgs.AddGrowableCol(2,1)
		winStaticBoxSizer.Add(fgs,proportion=0, flag=wx.TOP|wx.LEFT|wx.EXPAND, border = 15)
		for colourClass in sorted(config.colourClasses):
			sb = wx.StaticBox(self.scrolled, label=colourClass.replace("client.","").replace("_"," ").capitalize())
			boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
			fgs = wx.FlexGridSizer(4,3,9,25)

			for label in ["Border","Background","Text","Indicator"]:
				colour = config.colourClasses[colourClass].namedColour(label)
				fgs.Add(wx.StaticText(sb,label=label),0,0)
				cp = wx.ColourPickerCtrl(sb,colour=(config.setColours[colour].hex if type(colour) != Color else colour.hex))
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, colourClass=colourClass,name=label:config.colourClassChanged(e,colourClass,name),cp)
				fgs.Add(cp,0,0)
				cb = wx.ComboBox(sb,value="Individual colour" if type(colour) == Color else colour[1:],choices=["Individual colour"]+sorted(map(lambda n: n[1:],list(config.setColours.keys()))))
				fgs.Add(cb)
				self.Bind(wx.EVT_COMBOBOX,lambda e, p=cp.GetId(),l=label,c=colourClass: self.OnColourChange(e, pickerId=p, name=l, colourClass=c),cb)
				if type(colour) != Color:
					cp.Disable()
			
			fgs.AddGrowableCol(1,1)
			boxsizer.Add(fgs,flag=wx.LEFT|wx.BOTTOM|wx.TOP,border=5)
			winStaticBoxSizer.Add(boxsizer,proportion=1, flag=wx.ALL|wx.EXPAND, border = 15)
		hbox.Add(winStaticBoxSizer,proportion=1, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.EXPAND,border=5)

		barStaticBox = wx.StaticBox(self.scrolled,label="i3Bar")
		barStaticBoxSizer = wx.StaticBoxSizer(barStaticBox,wx.VERTICAL)

		fgs = wx.FlexGridSizer(3,3,9,25)

		for label in ["Background","Status line","Separator"]:
			fgs.Add(wx.StaticText(self.scrolled,label=label),0,0)
			
			colour = config.i3bar.namedColour(label)
			cp = wx.ColourPickerCtrl(self.scrolled,colour=(config.setColours[colour].hex if type(colour) != Color else colour.hex))
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, name=label:config.i3barChanged(e,name),cp)
			fgs.Add(cp,0,0)
			cb = wx.ComboBox(self.scrolled,value="Individual colour" if type(colour) == Color else colour[1:],choices=["Individual colour"]+sorted(map(lambda n: n[1:],list(config.setColours.keys()))))
			fgs.Add(cb)
			self.Bind(wx.EVT_COMBOBOX,lambda e, p=cp.GetId(),l=label: self.OnColourChange(e, pickerId=p, name=l, i3bar=True),cb)
			if type(colour) != Color:
				cp.Disable()
		
		fgs.AddGrowableCol(2,1)
		barStaticBoxSizer.Add(fgs,proportion=0, flag=wx.ALL|wx.EXPAND, border = 15)

		for colourClass in sorted(config.i3bar.colourClasses):
			sb = wx.StaticBox(self.scrolled, label=colourClass.replace("_"," ").capitalize())
			boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
			fgs = wx.FlexGridSizer(3,3,9,25)

			for label in ["Border","Background","Text"]:
				fgs.Add(wx.StaticText(sb,label=label),0,0)
				colour = config.i3bar.colourClasses[colourClass].namedColour(label)
				cp = wx.ColourPickerCtrl(sb,colour=(config.setColours[colour].hex if type(colour) != Color else colour.hex))
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, name=label,c=colourClass:config.colourClassChanged(e,c,name,True),cp)
				fgs.Add(cp,0,0)
				cb = wx.ComboBox(sb,value="Individual colour" if type(colour) == Color else colour[1:],choices=["Individual colour"]+sorted(map(lambda n: n[1:],list(config.setColours.keys()))))
				fgs.Add(cb)
				self.Bind(wx.EVT_COMBOBOX,lambda e, p=cp.GetId(),l=label,c=colourClass: self.OnColourChange(e, pickerId=p, name=l,colourClass=c, i3bar=True),cb)
				if type(colour) != Color:
					cp.Disable()

			fgs.AddGrowableCol(1,1)
			boxsizer.Add(fgs,flag=wx.LEFT|wx.BOTTOM|wx.TOP,border=5)
			barStaticBoxSizer.Add(boxsizer,proportion=0, flag=wx.ALL|wx.EXPAND, border = 15)
		hbox.Add(barStaticBoxSizer,proportion=1,  flag=wx.ALL|wx.EXPAND,border=5)
		vbox.Add(hbox,proportion=1,flag=wx.ALL|wx.EXPAND)
		self.scrolled.SetSizer(vbox)
		self.scrolled.SetupScrolling()

	def OnQuit(self,e):
		self.Close()

	def OnOpen(self, event):
		openFileDialog = wx.FileDialog(self, "Open i3 Config file", os.path.expanduser("~/.i3/"), "","i3 Config file |*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return
		cfg = Config(self.messager,openFileDialog.GetPath())
		self.LoadConfig(cfg)

	def OnApply(self, event):
		if self.config != None:
			self.config.updateConfig(os.path.expanduser('~/.config/i3/config'))
			os.system("mv '"+os.path.expanduser('~/.config/i3/config')+"' '/tmp/i3bacconfig'")
			os.system("mv '/tmp/i3tmpconf' '"+os.path.expanduser('~/.config/i3/config')+"'")
			i3ipc.Connection().command("reload")
			os.system("rm '"+os.path.expanduser('~/.config/i3/config')+"'")
			os.system("mv '/tmp/i3bacconfig' '"+os.path.expanduser('~/.config/i3/config')+"'")

	def OnSave(self,event):
		if self.config != None:
			self.config.updateConfig()
			os.system("mv '"+self.config.openFilename+"' '/tmp/i3bacconfig'")
			os.system("mv '/tmp/i3tmpconf' '"+self.config.openFilename+"'")

	def OnUpdateLocal(self,event):
		if self.config != None and os.path.isfile(os.path.expanduser('~/.config/i3/config')):
			self.config.updateConfig(os.path.expanduser('~/.config/i3/config'))
			os.system("rm '"+os.path.expanduser('~/.config/i3/config')+"'")
			os.system("mv '/tmp/i3tmpconf' '"+os.path.expanduser('~/.config/i3/config')+"'")
			i3ipc.Connection().command("reload")

	def OnCreateSnippet(self,event):
		openFileDialog = wx.FileDialog(self, "Save i3 Colour snippet file", os.path.expanduser("~/.i3/"), "","i3 Colour snippet file |*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return
		open(openFileDialog.GetPath(), 'w').close()
		self.config.updateConfig(openFileDialog.GetPath())
		os.system("rm '"+openFileDialog.GetPath()+"'")
		os.system("mv '/tmp/i3tmpconf' '"+openFileDialog.GetPath()+"'")

	def OnCreateVariable(self,event):
		openColourDialog = wx.ColourDialog(self)
		if openColourDialog.ShowModal() == wx.ID_CANCEL:
			return
		openNameChooser = wx.TextEntryDialog(self,"What would you like your new colour variable to be called?")
		if openNameChooser.ShowModal() == wx.ID_CANCEL:
			return	
		proposed = openNameChooser.GetValue()
		name = ""
		seenChar = False
		for character in proposed:
			if not seenChar:
				if character in string.ascii_letters:
					name+=character
					seenChar=True
			elif character in string.ascii_letters+string.digits:
				name+=character
		if name=="":
			i = 0
			for name in self.config.setColours:
				if name[:14]=="colourVariable":
					i+=1
			name = "colourVariable"+str(i)
		name = "$"+name
		self.config.setColourChanged(openColourDialog.GetColourData(),name)
		self.LoadConfig(self.config)


	def OnColourChange(self,event,pickerId=0,colourClass=None,name=None,i3bar=False):
		picker = self.FindWindowById(pickerId)
		if event.GetInt()==0:
			picker.Enable()
		else:
			picker.Disable()
			picker.SetColour(self.config.setColours["$"+event.GetString()].hex)
		if not i3bar:
			if colourClass!=None:
				self.config.colourClassChanged(picker if event.GetInt()==0 else "$"+event.GetString(),colourClass,name)
			elif name=="Background":
				self.config.backgroundChanged(picker if event.GetInt()==0 else "$"+event.GetString())
		else:
			if name!=None and colourClass!=None:
				self.config.colourClassChanged(picker if event.GetInt()==0 else "$"+event.GetString(),colourClass,name,True)
			elif colourClass==None and name!=None:
				self.config.i3barChanged(picker if event.GetInt()==0 else "$"+event.GetString(),name)

	def SetColourChanged(self,e,name):
		if type(e)==wx.CommandEvent:
			self.config.setColourChanged(None,name)
		else:
			self.config.setColourChanged(e,name)
		self.LoadConfig(self.config)

class Messager:
	def __init__(self,level,silencelevel,frame,log=False,logname="./i3colourchanger.log"):
		self.level = level
		self.silencelevel = silencelevel
		self.frame = frame
		self.labels=[]
		self.iconStyles=[]
		if log:
			self.logfile = open(logname, 'w')
		else:
			self.logfile = None
	def Lable(self,labels):
		self.labels = labels
	def Iconify(self,iconStyles):
		self.iconStyles = iconStyles
	def Send(self,message,level):
		message = message
		label = ('' if level>(len(self.labels)-1) else self.labels[level])
		iconStyle = (0 if level>(len(self.iconStyles)-1) else self.iconStyles[level])
		if self.logfile != None:
			self.logfile.write(label+": "+message)
		if level<=self.level:
			wx.MessageDialog(self.frame, message, label, wx.CENTRE | iconStyle).ShowModal()
		elif level<=self.silencelevel:
			self.frame.SetStatusText(label+": "+message)
	def Stop(self):
		if self.logfile != None:
			self.logfile.close()


class Config:
	def __init__(self,messager,filename=None):
		self.colourClasses={}
		self.colourClasses["client.focused"] = ColourClass(Color("#4c7899"),Color("#285577"),Color("#ffffff"),Color("#2e9ef4"))
		self.colourClasses["client.focused_inactive"] = ColourClass(Color("#333333"),Color("#5f676a"),Color("#ffffff"),Color("#484e50"))
		self.colourClasses["client.unfocused"] = ColourClass(Color("#333333"),Color("#222222"),Color("#888888"),Color("#292d2e"))
		self.colourClasses["client.urgent"] = ColourClass(Color("#2f343a"),Color("#900000"),Color("#ffffff"),Color("#900000"))
		self.colourClasses["client.placeholder"] = ColourClass(Color("#000000"),Color("#0c0c0c"),Color("#ffffff"),Color("#000000"))
		self.background = Color("#ffffff")

		self.i3bar=I3bar(Color("#000000"),Color("#ffffff"),Color("#666666"),{"focused_workspace" : ColourClass(Color("#4c7899"),Color("#285577"),Color("#ffffff")),"active_workspace" : ColourClass(Color("#333333"),Color("#5f676a"),Color("#ffffff")),"inactive_workspace" : ColourClass(Color("#333333"),Color("#222222"),Color("#888888")),"urgent_workspace" : ColourClass(Color("#2f343a"),Color("#900000"),Color("#ffffff")),"binding_mode" : ColourClass(Color("#2f343a"),Color("#900000"),Color("#ffffff"))})

		self.setColours={}

		self.openFilename = filename

		if filename:
			barMode = False
			colorMode = False
			brackets = 1
			colorVariables = []

			with open(filename, "r") as configFile:
				for line in configFile:
					if line!="\n":
						if barMode == True:
							stripped = "".join(line.split())
							if stripped[-1:] == "{":
								brackets+=1
								if stripped[:-1] == "colors":
									colorMode = True
							elif stripped == "}":
								brackets-=1
								colorMode = False
								if brackets == 0:
									barMode = False
							elif colorMode == True:
								l = line.split()
								try:
									if l[0] in self.i3bar.colourClasses:
										self.i3bar.colourClasses[l[0]].border = l[1] if l[1][0]=="$" else Color(hex=l[1])
										self.i3bar.colourClasses[l[0]].background = l[2] if l[2][0]=="$" else Color(hex=l[2])
										self.i3bar.colourClasses[l[0]].text = l[3] if l[3][0]=="$" else Color(hex=l[3])
									elif l[0] == "background":
										self.i3bar.background = l[1] if l[1][0]=="$" else Color(hex=l[1])
									elif l[0] == "statusline":
										self.i3bar.statusline = l[1] if l[1][0]=="$" else Color(hex=l[1])
									elif l[0] == "separator":
										self.i3bar.separator = l[1] if l[1][0]=="$" else Color(hex=l[1])
								except ValueError as e:
									messager.Send("Colour for i3bar " + e,1)
						elif "".join(line.split()) == "bar{":
							barMode = True
						if not barMode:
							l = line.split()
							if l[0]=="set":
								try:
									colour = Color(hex=l[2])
									self.setColours[l[1]]=colour
								except ValueError:
									pass
							for colourClass in list(self.colourClasses.keys())+["client.background"]:
								if colourClass==l[0]:
									if len(l)>=5:
										for i,colour in enumerate(l[1:5]):
											if colour[0]=="$":
												colorVariables.append(colour)
											try:
												if i==0:
													self.colourClasses[colourClass].border = colour if colour[0]=="$" else Color(hex=colour)
												elif i==1:
													self.colourClasses[colourClass].background = colour if colour[0]=="$" else Color(hex=colour)
												elif i==2:
													self.colourClasses[colourClass].text = colour if colour[0]=="$" else Color(hex=colour)
												elif i==3:
													self.colourClasses[colourClass].indicator = colour if colour[0]=="$" else Color(hex=colour)
											except ValueError as e:
												messager.Send("Colour for colour class \""+colourClass+"\" " + str(e),1)
									else:
										if colourClass=="client.background":
											try:
												self.background = l[1] if l[1][0]=="$" else Color(hex=l[1])
											except ValueError as e:
												messager.Send("Colour for colour class \""+colourClass+"\" " + str(e),1)
										else:
											messager.Send("Format of the colours for colour class \""+colourClass+"\" not recognized",1)
	
	def backgroundChanged(self,e):
		self.background = colourChanged(e,self.background)
	def setColourChanged(self,e,name=None):
		if e!=None:
			self.setColours[name] = colourChanged(e,self.setColours[name] if name in self.setColours else None)
		else:
			colour = self.setColours[name]
			self.setColours.pop(name,None)
			for colourClassName in list(self.colourClasses.keys())+list(self.i3bar.colourClasses.keys()):
				colourClass = self.colourClasses[colourClassName] if colourClassName in self.colourClasses else self.i3bar.colourClasses[colourClassName]
				if colourClass.background == name:
					colourClass.background = colour
				if colourClass.border == name:
					colourClass.border = colour
				if colourClass.text == name:
					colourClass.text = colour
				if colourClass.indicator == name:
					colourClass.indicator = colour
			if self.background == name:
				self.background = colour
			if self.i3bar.background == name:
				self.i3bar.background = colour
			if self.i3bar.statusline == name:
				self.i3bar.statusline = colour
			if self.i3bar.separator == name:
				self.i3bar.separator = colour


	def colourClassChanged(self,e,colourClass=None,name=None,inBar=False):
		if name!=None and colourClass!=None:
			if not inBar:
				if name=="Background":
					self.colourClasses[colourClass].background = colourChanged(e,self.colourClasses[colourClass].background)
				elif name=="Border":
					self.colourClasses[colourClass].border = colourChanged(e,self.colourClasses[colourClass].border)
				elif name=="Text":
					self.colourClasses[colourClass].text = colourChanged(e,self.colourClasses[colourClass].text)
				elif name=="Indicator":
					self.colourClasses[colourClass].indicator = colourChanged(e,self.colourClasses[colourClass].indicator)
			else:
				if name=="Background":
					self.i3bar.colourClasses[colourClass].background = colourChanged(e,self.i3bar.colourClasses[colourClass].background)
				elif name=="Border":
					self.i3bar.colourClasses[colourClass].border = colourChanged(e,self.i3bar.colourClasses[colourClass].border)
				elif name=="Text":
					self.i3bar.colourClasses[colourClass].text = colourChanged(e,self.i3bar.colourClasses[colourClass].text)

	def i3barChanged(self,e,name=None):
		if name!=None:
			if name=="Background":
				self.i3bar.background = colourChanged(e,self.i3bar.background)
			elif name=="Status line":
				self.i3bar.statusline = colourChanged(e,self.i3bar.statusline)
			elif name=="Separator":
				self.i3bar.separator = colourChanged(e,self.i3bar.separator)

	def createBarBlock(self):
		out = "\tcolors {\n"
		out += "\t\tbackground {0}\n\t\tstatusline {1}\n\t\tseparator {2}\n".format(self.colorToHex(self.i3bar.background),self.colorToHex(self.i3bar.statusline),self.colorToHex(self.i3bar.separator))
		for colourClass in self.i3bar.colourClasses:
			out+= "\t\t{0} {1} {2} {3}\n".format(colourClass,self.colorToHex(self.i3bar.colourClasses[colourClass].border),self.colorToHex(self.i3bar.colourClasses[colourClass].background),self.colorToHex(self.i3bar.colourClasses[colourClass].text))
		out += "\t}\n"
		return out
	def colorToHex(self,color):
		if type(color) != Color:
			return color
		return "#%0.2X%0.2X%0.2X" % (int(math.ceil(color.red*255)),int(math.ceil(color.green*255)),int(math.ceil(color.blue*255)))

	def updateConfig(self,filename=None):
		barMode=False
		colorMode=False
		brackets=1
		writtenColours=[]
		writtenSets=[]
		writtenBar=False
		if filename == None:
			filename = self.openFilename
		with open("/tmp/i3tmpconf","w") as tmp:
			with open(filename,"r") as configFile:
				for line in configFile:
					if barMode == True:
						stripped = "".join(line.split())
						if stripped[-1:] == "{":
							brackets+=1
							if stripped[:-1] == "colors":
								colorMode = True
							else:
								tmp.write(line)
						elif stripped == "}":
							if colorMode == True:
								tmp.write(self.createBarBlock())
								writtenBar=True
							brackets-=1
							colorMode = False
							if brackets == 0:
								barMode = False
								if writtenBar==False:
									tmp.write(self.createBarBlock()+"}\n")
							elif colorMode == False:
								tmp.write(line)
						elif colorMode==False:
							tmp.write(line)
					elif "".join(line.split()) == "bar{":
						tmp.write(line)
						barMode = True
					else:
						split = line.split()
						if len(split)!=0 and split[0] in self.colourClasses:
							colourClass = self.colourClasses[split[0]]
							tmp.write(split[0]+" "+self.colorToHex(colourClass.border)+" "+self.colorToHex(colourClass.background)+" "+self.colorToHex(colourClass.text)+" "+self.colorToHex(colourClass.indicator)+"\n")
							writtenColours.append(split[0])
						elif len(split)!=0 and split[0]=="client.background":
							tmp.write("client.background "+self.colorToHex(self.background)+"\n")
							writtenColours.append("client.background")
						elif len(split)!=0 and split[0]=="set":
							if split[1] in self.setColours:
								tmp.write("set {0} {1} {2}\n".format(split[1],self.colorToHex(self.setColours[split[1]]),"".join(split[3:])))
								writtenSets.append(split[1])
							else:
								try:
									colour = Color(hex=split[2])
								except ValueError:
									tmp.write(line)
						else:
							tmp.write(line)
				if writtenBar==False:
					tmp.write("bar {\n"+self.createBarBlock()+"}")
				if len(writtenColours)!=len(self.colourClasses)+1:
					tmp.write("\n\n#Colours not previously found in file:\n")
					for colourClassName in [item for item in self.colourClasses if item not in writtenColours]:
						colourClass = self.colourClasses[colourClassName]
						tmp.write(colourClassName+" "+self.colorToHex(colourClass.border)+" "+self.colorToHex(colourClass.background)+" "+self.colorToHex(colourClass.text)+" "+self.colorToHex(colourClass.indicator)+"\n")
					if "client.background" not in writtenColours:
						tmp.write("client.background "+self.colorToHex(self.background)+"\n")
				if len(writtenSets)!=len(self.setColours):
					tmp.write("\n")
					for setColour in [item for item in self.setColours if item not in writtenSets]:
						tmp.write("set {0} {1}\n".format(setColour,self.colorToHex(self.setColours[setColour])))

app = wx.App()
mainWindow = MainWindow(None)
mainWindow.messager.Lable(["ERROR","Warning","Info","Debug"])
mainWindow.messager.Iconify([wx.ICON_ERROR,wx.ICON_EXCLAMATION,wx.ICON_QUESTION,wx.ICON_INFORMATION])
cfg = Config(mainWindow.messager,os.path.expanduser('~/.config/i3/config'))
mainWindow.LoadConfig(cfg)
app.MainLoop()
