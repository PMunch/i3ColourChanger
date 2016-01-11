from colour import Color
import wx
import wx.lib.scrolledpanel
import i3ipc
import math
import os

def colourChanged(e,oldColour):
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
		toolOpen = toolbar.AddTool(wx.ID_ANY, 'Open', artprovider.GetBitmap(wx.ART_FILE_OPEN,size=wx.Size(24,24)),"Open an i3 config file")
		toolSave = toolbar.AddTool(wx.ID_ANY, 'Save', artprovider.GetBitmap(wx.ART_FILE_SAVE,size=wx.Size(24,24)),"Save the current settings to the open file")
		toolApply = toolbar.AddTool(wx.ID_ANY, 'Apply', artprovider.GetBitmap(wx.ART_TICK_MARK,size=wx.Size(24,24)),"Apply the changes without changing file")
		toolUpdateLocal = toolbar.AddTool(wx.ID_ANY, 'Save to config', artprovider.GetBitmap(wx.ART_FILE_SAVE_AS,size=wx.Size(24,24)),"Save the current colour scheme into your current config")
		toolSnippet = toolbar.AddTool(wx.ID_ANY, 'Create colour snippet', artprovider.GetBitmap(wx.ART_NEW,size=wx.Size(24,24)),"Save the current colour scheme as a standalone colour file you can send to others")
		toolbar.AddStretchableSpace()
		toolQuit = toolbar.AddTool(wx.ID_ANY, 'Quit', artprovider.GetBitmap(wx.ART_QUIT,size=wx.Size(24,24)),"Quit the program")

		self.Bind(wx.EVT_TOOL, self.OnQuit,toolQuit)
		self.Bind(wx.EVT_TOOL, self.OnOpen,toolOpen)
		self.Bind(wx.EVT_TOOL, self.OnApply,toolApply)
		self.Bind(wx.EVT_TOOL, self.OnSave,toolSave)
		self.Bind(wx.EVT_TOOL, self.OnUpdateLocal,toolUpdateLocal)
		self.Bind(wx.EVT_TOOL, self.OnCreateSnippet,toolSnippet)

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
			setStaticBox = wx.StaticBox(self.scrolled,label="Set colours")
			setStaticBoxSizer = wx.StaticBoxSizer(setStaticBox,wx.VERTICAL)
			
			grid = wx.FlexGridSizer(math.ceil(len(config.setColours)/2),2,15,25)
			for setColour in sorted(config.setColours):
				fgs = wx.FlexGridSizer(1,2,9,25)
				fgs.Add(wx.StaticText(self.scrolled,label=setColour[1:]))
				cp = wx.ColourPickerCtrl(self.scrolled,colour=config.setColours[setColour].hex)
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, name=setColour:config.setColourChanged(e,name) ,cp)
				fgs.Add(cp)
				grid.Add(fgs,0,0)
			grid.AddGrowableCol(0,1)
			grid.AddGrowableCol(1,1)
			setStaticBoxSizer.Add(grid,proportion=0, flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.EXPAND, border = 15)
			vbox.Add(setStaticBoxSizer,proportion=0, flag=wx.RIGHT|wx.LEFT|wx.EXPAND,border=5)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		winStaticBox = wx.StaticBox(self.scrolled,label="Windows")
		winStaticBoxSizer = wx.StaticBoxSizer(winStaticBox,wx.VERTICAL)

		fgs = wx.FlexGridSizer(1,2,9,25)
		
		fgs.Add(wx.StaticText(self.scrolled,label="Background"),0,0)
		cpBackground = wx.ColourPickerCtrl(self.scrolled,colour=config.background.hex)
		self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.backgroundChanged,cpBackground)
		fgs.Add(cpBackground,0,0)

		fgs.AddGrowableCol(1,1)
		winStaticBoxSizer.Add(fgs,proportion=0, flag=wx.TOP|wx.LEFT|wx.EXPAND, border = 15)
		for colourClass in sorted(config.colourClasses):
			sb = wx.StaticBox(self.scrolled, label=colourClass.replace("client.","").replace("_"," ").capitalize())
			boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
			fgs = wx.FlexGridSizer(4,2,9,25)

			for label in ["Border","Background","Text","Indicator"]:
				fgs.Add(wx.StaticText(sb,label=label),0,0)
				cp = wx.ColourPickerCtrl(sb,colour=config.colourClasses[colourClass].namedColour(label).hex)
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, colourClass=colourClass,name=label:config.colourClassChanged(e,colourClass,name),cp)
				fgs.Add(cp,0,0)
			
			fgs.AddGrowableCol(1,1)
			boxsizer.Add(fgs,flag=wx.LEFT|wx.BOTTOM|wx.TOP,border=5)
			winStaticBoxSizer.Add(boxsizer,proportion=1, flag=wx.ALL|wx.EXPAND, border = 15)
		hbox.Add(winStaticBoxSizer,proportion=1, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.EXPAND,border=5)

		barStaticBox = wx.StaticBox(self.scrolled,label="i3Bar")
		barStaticBoxSizer = wx.StaticBoxSizer(barStaticBox,wx.VERTICAL)

		fgs = wx.FlexGridSizer(3,2,9,25)

		for label in ["Background","Status line","Separator"]:
			fgs.Add(wx.StaticText(self.scrolled,label=label),0,0)
			cp = wx.ColourPickerCtrl(self.scrolled,colour=config.i3bar.namedColour(label).hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,(lambda e, name=label:config.i3barChanged(e,name)),cp)
			fgs.Add(cp,0,0)
		
		fgs.AddGrowableCol(1,1)
		barStaticBoxSizer.Add(fgs,proportion=0, flag=wx.ALL|wx.EXPAND, border = 15)

		for colourClass in sorted(config.i3bar.colourClasses):
			sb = wx.StaticBox(self.scrolled, label=colourClass.replace("_"," ").capitalize())
			boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
			fgs = wx.FlexGridSizer(3,2,9,25)

			for label in ["Border","Background","Text"]:
				fgs.Add(wx.StaticText(sb,label=label),0,0)
				cp = wx.ColourPickerCtrl(sb,colour=config.i3bar.colourClasses[colourClass].namedColour(label).hex)
				self.Bind(wx.EVT_COLOURPICKER_CHANGED,lambda e, colourClass=colourClass,name=label,i3bar=True:config.colourClassChanged(e,colourClass,name,i3bar),cp)
				fgs.Add(cp,0,0)

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
			self.config.updateConfig(os.path.expanduser('~/.i3/config'))
			os.system("mv '"+os.path.expanduser('~/.i3/config')+"' '/tmp/i3bacconfig'")
			os.system("mv '/tmp/i3tmpconf' '"+os.path.expanduser('~/.i3/config')+"'")
			i3ipc.Connection().command("reload")
			os.system("rm '"+os.path.expanduser('~/.i3/config')+"'")
			os.system("mv '/tmp/i3bacconfig' '"+os.path.expanduser('~/.i3/config')+"'")

	def OnSave(self,event):
		if self.config != None:
			self.config.updateConfig()
			os.system("mv '"+self.config.openFilename+"' '/tmp/i3bacconfig'")
			os.system("mv '/tmp/i3tmpconf' '"+self.config.openFilename+"'")

	def OnUpdateLocal(self,event):
		if self.config != None and os.path.isfile(os.path.expanduser('~/.i3/config')):
			self.config.updateConfig(os.path.expanduser('~/.i3/config'))
			os.system("rm '"+os.path.expanduser('~/.i3/config')+"'")
			os.system("mv '/tmp/i3tmpconf' '"+os.path.expanduser('~/.i3/config')+"'")
			i3ipc.Connection().command("reload")

	def OnCreateSnippet(self,event):
		openFileDialog = wx.FileDialog(self, "Save i3 Colour snippet file", os.path.expanduser("~/.i3/"), "","i3 Colour snippet file |*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return
		open(openFileDialog.GetPath(), 'w').close()
		self.config.updateConfig(openFileDialog.GetPath())
		os.system("rm '"+openFileDialog.GetPath()+"'")
		os.system("mv '/tmp/i3tmpconf' '"+openFileDialog.GetPath()+"'")

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
									if l[0] == "background":
										self.i3bar.background = Color(l[1])
									elif l[0] == "statusline":
										self.i3bar.statusline = Color(l[1])
									elif l[0] == "separator":
										self.i3bar.separator = Color(l[1])
									elif l[0] in self.i3bar.colourClasses:
										self.i3bar.colourClasses[l[0]].border = Color(l[1])
										self.i3bar.colourClasses[l[0]].background = Color(l[2])
										self.i3bar.colourClasses[l[0]].text = Color(l[3])
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
							for colourClass in self.colourClasses:
								if colourClass==l[0]:
									if len(l)>=5:
										for i,colour in enumerate(l[1:5]):
											try:
												if i==0:
													self.colourClasses[colourClass].border = Color(colour)
												elif i==1:
													self.colourClasses[colourClass].background = Color(colour)
												elif i==2:
													self.colourClasses[colourClass].text = Color(colour)
												elif i==3:
													self.colourClasses[colourClass].indicator = Color(colour)
											except ValueError as e:
												messager.Send("Colour for colour class \""+colourClass+"\" " + e,1)
									else:
										if colourClass=="client.background":
											try:
												self.background = Color(l[1])
											except ValueError as e:
												messager.Send("Colour for colour class \""+colourClass+"\" " + e,1)
										else:
											messager.Send("Format of the colours for colour class \""+colourClass+"\" not recognized",1)
	
	def backgroundChanged(self,e):
		self.background = colourChanged(e,self.background)
	def setColourChanged(self,e,name=None):
		if name!=None:
			self.setColours[name] = colourChanged(e,self.setColours[name])

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
		out += "\t\tbackground #{0}\n\t\tstatusline #{1}\n\t\tseparator #{2}\n".format(self.colorToHex(self.i3bar.background),self.colorToHex(self.i3bar.statusline),self.colorToHex(self.i3bar.separator))
		for colourClass in self.i3bar.colourClasses:
			out+= "\t\t{0} #{1} #{2} #{3}\n".format(colourClass,self.colorToHex(self.i3bar.colourClasses[colourClass].border),self.colorToHex(self.i3bar.colourClasses[colourClass].background),self.colorToHex(self.i3bar.colourClasses[colourClass].text))
		out += "\t}\n"
		return out
	def colorToHex(self,color):
		return "%0.2X%0.2X%0.2X" % (int(math.ceil(color.red*255)),int(math.ceil(color.green*255)),int(math.ceil(color.blue*255)))
	def updateConfig(self,filename=None):
		barMode=False
		colorMode=False
		brackets=1
		writtenColours=[]
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
							tmp.write(split[0]+" #"+self.colorToHex(colourClass.border)+" #"+self.colorToHex(colourClass.background)+" #"+self.colorToHex(colourClass.text)+" #"+self.colorToHex(colourClass.indicator)+"\n")
							writtenColours.append(split[0])
						elif len(split)!=0 and split[0]=="client.background":
							tmp.write("client.background #"+self.colorToHex(self.background)+"\n")
							writtenColours.append("client.background")
						else:
							tmp.write(line)
				if writtenBar==False:
					tmp.write("bar {\n"+self.createBarBlock()+"}")
				if len(writtenColours)!=len(self.colourClasses)+1:
					tmp.write("\n\n#Colours not previously found in file:\n")
					for colourClassName in [item for item in self.colourClasses if item not in writtenColours]:
						colourClass = self.colourClasses[colourClassName]
						tmp.write(colourClassName+" #"+self.colorToHex(colourClass.border)+" #"+self.colorToHex(colourClass.background)+" #"+self.colorToHex(colourClass.text)+" #"+self.colorToHex(colourClass.indicator)+"\n")
					if "client.background" not in writtenColours:
						tmp.write("client.background #"+self.colorToHex(self.background)+"\n")

app = wx.App()
mainWindow = MainWindow(None)
mainWindow.messager.Lable(["ERROR","Warning","Info","Debug"])
mainWindow.messager.Iconify([wx.ICON_ERROR,wx.ICON_EXCLAMATION,wx.ICON_QUESTION,wx.ICON_INFORMATION])
cfg = Config(mainWindow.messager,os.path.expanduser('~/.i3/config'))
#cfg.updateConfig("/home/peter/.i3/config")i3.command("reload")
mainWindow.LoadConfig(cfg)
#print(i3.command("reload"))
app.MainLoop()