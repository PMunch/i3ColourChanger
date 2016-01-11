from colour import Color
import wx
import wx.lib.scrolledpanel
import i3ipc
import math
import os
import shutil

class ColourClass:
	def __init__(self,border,background,text,indicator=None):
		self.border = border
		self.background = background
		self.text = text
		self.indicator = indicator
	def borderChanged(self,e):
		nc = e.GetColour()
		self.border.red = nc[0]/255
		self.border.green = nc[1]/255
		self.border.blue = nc[2]/255
	def backgroundChanged(self,e):
		nc = e.GetColour()
		self.background.red = nc[0]/255
		self.background.green = nc[1]/255
		self.background.blue = nc[2]/255
	def textChanged(self,e):
		nc = e.GetColour()
		self.text.red = nc[0]/255
		self.text.green = nc[1]/255
		self.text.blue = nc[2]/255
	def indicatorChanged(self,e):
		nc = e.GetColour()
		self.indicator.red = nc[0]/255
		self.indicator.green = nc[1]/255
		self.indicator.blue = nc[2]/255

class I3bar:
	def __init__(self,background,statusline,separator,colourClasses):
		self.background = background
		self.statusline = statusline
		self.separator = separator
		self.colourClasses = colourClasses
	def backgroundChanged(self,e):
		nc = e.GetColour()
		self.background.red = nc[0]/255
		self.background.green = nc[1]/255
		self.background.blue = nc[2]/255
	def statuslineChanged(self,e):
		nc = e.GetColour()
		self.statusline.red = nc[0]/255
		self.statusline.green = nc[1]/255
		self.statusline.blue = nc[2]/255
	def separatorChanged(self,e):
		nc = e.GetColour()
		self.separator.red = nc[0]/255
		self.separator.green = nc[1]/255
		self.separator.blue = nc[2]/255

class MainWindow(wx.Frame):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args,**kwargs,title="i3 Colour Changer")
		self.InitUI()
		self.messager = Messager(100,1, self)
		self.config = None

	def InitUI(self,config=None):
		artprovider = wx.ArtProvider()
		toolbar = self.CreateToolBar(style=wx.TB_TEXT|wx.TB_HORZ_LAYOUT)
		toolOpen = toolbar.AddTool(wx.ID_ANY, 'Open', artprovider.GetBitmap(wx.ART_FILE_OPEN,size=wx.Size(24,24)),"Open an i3 config file")
		toolSave = toolbar.AddTool(wx.ID_ANY, 'Save', artprovider.GetBitmap(wx.ART_FILE_SAVE,size=wx.Size(24,24)),"Save the current settings to the open file")
		toolApply = toolbar.AddTool(wx.ID_ANY, 'Apply', artprovider.GetBitmap(wx.ART_TICK_MARK,size=wx.Size(24,24)),"Apply the changes without changing file")
		toolbar.AddStretchableSpace()
		toolQuit = toolbar.AddTool(wx.ID_ANY, 'Quit', artprovider.GetBitmap(wx.ART_QUIT,size=wx.Size(24,24)),"Quit the program")

		self.Bind(wx.EVT_TOOL, self.OnQuit,toolQuit)
		self.Bind(wx.EVT_TOOL, self.OnOpen,toolOpen)
		self.Bind(wx.EVT_TOOL, self.OnApply,toolApply)
		self.Bind(wx.EVT_TOOL, self.OnSave,toolSave)

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
			
			fgs.Add(wx.StaticText(sb,label="Border"),0,0)
			cpBorder = wx.ColourPickerCtrl(sb,colour=config.colourClasses[colourClass].border.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.colourClasses[colourClass].borderChanged,cpBorder)
			fgs.Add(cpBorder,0,0)
			
			fgs.Add(wx.StaticText(sb,label="Background"),0,0)
			cpBackground = wx.ColourPickerCtrl(sb,colour=config.colourClasses[colourClass].background.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.colourClasses[colourClass].backgroundChanged,cpBackground)
			fgs.Add(cpBackground,0,0)

			fgs.Add(wx.StaticText(sb,label="Text"),0,0)
			cpText = wx.ColourPickerCtrl(sb,colour=config.colourClasses[colourClass].text.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.colourClasses[colourClass].textChanged,cpText)
			fgs.Add(cpText,0,0)
			
			fgs.Add(wx.StaticText(sb,label="Indicator"),0,0)
			cpIndicator = wx.ColourPickerCtrl(sb,colour=config.colourClasses[colourClass].indicator.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.colourClasses[colourClass].indicatorChanged,cpIndicator)
			fgs.Add(cpIndicator,0,0)
			
			fgs.AddGrowableCol(1,1)
			boxsizer.Add(fgs,flag=wx.LEFT|wx.BOTTOM|wx.TOP,border=5)
			winStaticBoxSizer.Add(boxsizer,proportion=1, flag=wx.ALL|wx.EXPAND, border = 15)
		hbox.Add(winStaticBoxSizer,proportion=1, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.EXPAND,border=5)

		barStaticBox = wx.StaticBox(self.scrolled,label="i3Bar")
		barStaticBoxSizer = wx.StaticBoxSizer(barStaticBox,wx.VERTICAL)

		fgs = wx.FlexGridSizer(3,2,9,25)
		
		fgs.Add(wx.StaticText(self.scrolled,label="Background"),0,0)
		cpBackground = wx.ColourPickerCtrl(self.scrolled,colour=config.i3bar.background.hex)
		self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.backgroundChanged,cpBackground)
		fgs.Add(cpBackground,0,0)

		fgs.Add(wx.StaticText(self.scrolled,label="Status line"),0,0)
		cpStatusline = wx.ColourPickerCtrl(self.scrolled,colour=config.i3bar.statusline.hex)
		self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.statuslineChanged,cpStatusline)
		fgs.Add(cpStatusline,0,0)

		fgs.Add(wx.StaticText(self.scrolled,label="Separator"),0,0)
		cpSeparator = wx.ColourPickerCtrl(self.scrolled,colour=config.i3bar.separator.hex)
		self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.separatorChanged,cpSeparator)
		fgs.Add(cpSeparator,0,0)
		
		fgs.AddGrowableCol(1,1)
		barStaticBoxSizer.Add(fgs,proportion=0, flag=wx.ALL|wx.EXPAND, border = 15)

		for colourClass in sorted(config.i3bar.colourClasses):
			sb = wx.StaticBox(self.scrolled, label=colourClass.replace("_"," ").capitalize())
			boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
			fgs = wx.FlexGridSizer(3,2,9,25)

			fgs.Add(wx.StaticText(sb,label="Border"),0,0)
			cpBorder = wx.ColourPickerCtrl(sb,colour=config.i3bar.colourClasses[colourClass].border.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.colourClasses[colourClass].borderChanged,cpBorder)
			fgs.Add(cpBorder,0,0)

			fgs.Add(wx.StaticText(sb,label="Background"),0,0)
			cpBackground = wx.ColourPickerCtrl(sb,colour=config.i3bar.colourClasses[colourClass].background.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.colourClasses[colourClass].backgroundChanged,cpBackground)
			fgs.Add(cpBackground,0,0)

			fgs.Add(wx.StaticText(sb,label="Text"),0,0)
			cpText = wx.ColourPickerCtrl(sb,colour=config.i3bar.colourClasses[colourClass].text.hex)
			self.Bind(wx.EVT_COLOURPICKER_CHANGED,config.i3bar.colourClasses[colourClass].textChanged,cpText)
			fgs.Add(cpText,0,0)

			fgs.AddGrowableCol(1,1)
			boxsizer.Add(fgs,flag=wx.LEFT|wx.BOTTOM|wx.TOP,border=5)
			barStaticBoxSizer.Add(boxsizer,proportion=0, flag=wx.ALL|wx.EXPAND, border = 15)
		hbox.Add(barStaticBoxSizer,proportion=1,  flag=wx.ALL|wx.EXPAND,border=5)

		self.scrolled.SetSizer(hbox)
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
			os.system("mv "+os.path.expanduser('~/.i3/config')+" /tmp/i3bacconfig")
			os.system("mv /tmp/i3tmpconf "+os.path.expanduser('~/.i3/config'))
			i3ipc.Connection().command("reload")
			os.system("rm "+os.path.expanduser('~/.i3/config'))
			os.system("mv /tmp/i3bacconfig "+os.path.expanduser('~/.i3/config'))

	def OnSave(self,event):
		if self.config != None:
			self.config.updateConfig()
			os.system("mv "+self.config.openFilename+" /tmp/i3bacconfig")
			os.system("mv /tmp/i3tmpconf "+self.config.openFilename)

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
							for colourClass in self.colourClasses:
								if colourClass==line.strip().split()[0]:
									colours = "".join(line[line.find(colourClass)+len(colourClass):].split()).split("#")[1:]
									if len(colours)>=4:
										for i,colour in enumerate(colours[:4]):
											try:
												if i==0:
													self.colourClasses[colourClass].border = Color("#"+colour)
												elif i==1:
													self.colourClasses[colourClass].background = Color("#"+colour)
												elif i==2:
													self.colourClasses[colourClass].text = Color("#"+colour)
												elif i==3:
													self.colourClasses[colourClass].indicator = Color("#"+colour)
											except ValueError as e:
												messager.Send("Colour for colour class \""+colourClass+"\" " + e,1)
									else:
										if colourClass=="client.background":
											self.background = Color("#"+colours[0])
										else:
											messager.Send("Format of the colours for colour class \""+colourClass+"\" not recognized",1)
	
	def backgroundChanged(self,e):
		nc = e.GetColour()
		self.background.red = nc[0]/255
		self.background.green = nc[1]/255
		self.background.blue = nc[2]/255
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
				if len(writtenColours)!=len(self.colourClasses)+1:
					tmp.write("\n\n#Colours not previously found in file:\n")
					for colourClassName in [item for item in self.colourClasses if item not in writtenColours]:
						colourClass = self.colourClasses[colourClassName]
						tmp.write(colourClassName+" #"+self.colorToHex(colourClass.border)+" #"+self.colorToHex(colourClass.background)+" #"+self.colorToHex(colourClass.text)+" #"+self.colorToHex(colourClass.indicator)+"\n")
					if "client.background" not in writtenColours:
						tmp.write("client.background #"+self.colorToHex(self.background)+"\n")
		#shutil.copy2("/tmp/i3tmpconf",filename)

app = wx.App()
mainWindow = MainWindow(None)
mainWindow.messager.Lable(["ERROR","Warning","Info","Debug"])
mainWindow.messager.Iconify([wx.ICON_ERROR,wx.ICON_EXCLAMATION,wx.ICON_QUESTION,wx.ICON_INFORMATION])
cfg = Config(mainWindow.messager,os.path.expanduser('~/.i3/config'))
#cfg.updateConfig("/home/peter/.i3/config")i3.command("reload")
mainWindow.LoadConfig(cfg)
#print(i3.command("reload"))
app.MainLoop()