"""
A pyhton script to control the GUI application named "TCS" developed by Alluna.
Because ASCOM does not have dustcover capability, there is no way to control dust cover from CUI.
That is the reason to develop this script.

2014.5.8 Yousuke Utsumi
"""
from pywinauto import application, controls
import time

pathtoapp = "C:\Program Files\ALLUNA Optics\Telescope Control System\TCS.exe"
windowname = u'TCS V10.6T'

class Telescope:
    def __init__(self):
        pass

    def __del__(self):
        self.app.kill_()
    
    def Connect(self):
        try:
            self.app = application.Application()
            self.app.connect_(path=pathtoapp)
            print "TCS is already running... Try to fetch the handle."
        except application.ProcessNotFoundError:
            print "Try to run TCS application"
            self.app = application.Application.start(pathtoapp)
        
        self.app_form = self.app[windowname]
        self.buttonconnect = controls.win32_controls.ButtonWrapper(self.app_form[u"Connect"])
        
        if u"Connect" in self.buttonconnect.Texts():
            print "Connecting to the telescope..."
            self.buttonconnect.Click()
        else:
            print "Seems already connected"
            
        print "Get tab content to handle tabs"        
        self.tabcontrol=controls.common_controls.TabControlWrapper(self.app_form[u"TTabControl"])
        self.tabdict = dict( \
            [ (self.tabcontrol.GetTabText(i), i) for i in range(self.tabcontrol.TabCount())])

        print "Get tab content in Settings to handle tabs"        
        self.settingstabcontrol=controls.common_controls.TabControlWrapper(self.app_form[u"TTabControl2"])
        self.settingstabdict = dict( \
            [ (self.settingstabcontrol.GetTabText(i), i) for i in range(self.settingstabcontrol.TabCount())])

        self._WaitCompletion()

    def _MoveTab(self,dst):
        if self.tabcontrol.GetSelectedTab() == self.tabdict[u"%s" % dst]:
            return
        print "Then move to %s control tab" % dst
        self.tabcontrol.Select(self.tabdict[u"%s" % dst])

    def _MoveSettingTab(self,dst):
        if self.settingstabcontrol.GetSelectedTab() \
	    == self.settingstabdict[u"%s" % dst]:
            return
        print "Then move to %s control tab" % dst
        self.settingstabcontrol.Select(self.settingstabdict[u"%s" % dst])

    def _DustcoverControl(self,cmd):
        self._MoveTab("Dustcover")

        print "Try to %s dust cover" % cmd
        if cmd in self.DustcoverStatus():
            print "Now %sing" % cmd
            if self.app_form["Button2"].IsEnabled():
                self.app_form["Button2"].Click()
                while "Wait ..." in self.DustcoverStatus():
                    print "Wait completion for 1 seconds."
                    time.sleep(1)
            else:
                print "Seems lost the handle to the telescope"
        else:
            print "Seems already %sed" % cmd        

    def DustcoverStatus(self):
        self._MoveTab("Dustcover")
        return self.app_form["Button2"].Texts()
    
    def DustcoverOpen(self):
        self._DustcoverControl("Open")

    def DustcoverClose(self):
        self._DustcoverControl("Close")

    def _WaitCompletion(self):
        while self.buttonconnect.IsEnabled() != True:
            print "wait for 1 seconds"
            time.sleep(1)
        
    def FocusingTargetPosition(self,target):
        self._MoveTab("Focus")
        
        zpos=controls.win32_controls.EditWrapper(self.app_form["TJvSpinEdit17"])
        zpos.SetText("%d" % int(target))

        gotobutton=controls.win32_controls.EditWrapper(self.app_form["GoToButton2"])
        gotobutton.Click()
        self._WaitCompletion()

    def FocusingHomePosition(self):
        self._MoveTab("Focus")
        self.app_form["GoToStatic"]
        nominalbutton = controls.win32_controls.ButtonWrapper(self.app_form["GoToStatic"])
        nominalbutton.Click(coords=(26,0))
        self._WaitCompletion()

        # There was no key to describe "Homerun" button.
        # So I decited to use a "coords" extraoption to shift mouse click. 


    def FocusingPosition(self):
        self._MoveTab("Settings")
        self._MoveSettingTab("Focuser")
	# should do something around here to do switch tabs
	return float(self.app_form["TJvSpinEdit4"].GetProperties()["Texts"][0])/10000.
        

    def InspectClass(self):
        self._MoveTab("Focus")
        self._MoveTab("Climate")
        for i, child in enumerate(self.app_form.Children()):
            child.CaptureAsImage().save("%s%d.jpg" \
		% (child.FriendlyClassName(),i) )


if __name__ == "__main__":
    import time, sys, traceback
    try:
        telescope = Telescope()
        telescope.Connect()
#        print telescope.DustcoverStatus()
#        telescope.DustcoverOpen()
#        print telescope.DustcoverStatus()
#        telescope.DustcoverClose()
        telescope.FocusingTargetPosition(9884)
        print telescope.FocusingPosition()
        
    except:
        traceback.print_exc(file=sys.stdout)
	pass
#        del telescope

