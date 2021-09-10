#!/usr/bin/python3
from gi.repository import Gtk, XApp
import gettext
import gi
import subprocess
from packaging import version

gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, XApp

SPEAKERS_MODE = _("Speakers")
HEADPHONES_MODE = _("Headphone")
MODE = "Headphone"

def get_output(commands):
    process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out, err = process.communicate()
    return out.decode('utf-8').strip()


class Tray:
    
    def __init__(self):

        self.icon = XApp.StatusIcon()
        self.icon.set_name("SBZ")

        # todo get card number from amixer
        card='1'
        # Find GPU name
        output = None
        try:
            output = subprocess.check_output("amixer -c "+card+" sget 'Output Select' | grep -i 'Item0'", shell=True).decode("UTF-8").strip().split(": ")[1]
        except:
            pass

        # Find active mode
        speakers = Gtk.MenuItem(label=("Switch to: %s") % SPEAKERS_MODE)
        speakers.connect("activate", self.switch, SPEAKERS_MODE, card)

        
        headphones = Gtk.MenuItem(label=("Switch to: %s") % HEADPHONES_MODE)
        headphones.connect("activate", self.switch, HEADPHONES_MODE, card)

        #active_output = get_output("/usr/bin/amixer -c "+card+" sget 'Output Select' | grep -i 'Item0'").decode("UTF-8").strip().split(": ")[1]
        active_output=output
        if (active_output == "'Speakers'"):
            self.icon.set_icon_name("audio-speakers")
            MODE = SPEAKERS_MODE
        elif (active_output == "'Headphone'"):
            self.icon.set_icon_name("audio-headphones")
            MODE = HEADPHONES_MODE
        else:
            self.icon.set_icon_name("dialog-error-symbolic")
            MODE = ("Unknown mode")

        
        self.icon.set_tooltip_text("%s\n%s" % ("Creative Sound Blaster Z", MODE))
        
        halndler_id=self.icon.connect("activate",self.switch, card)
        self.icon.set_primary_menu(None)
        

    

    def dialog_closed(self, widget, event):
        return Gtk.ResponseType.NO

    def switch(self,args,id, widget, card):
        
            
            if (MODE == HEADPHONES_MODE):
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Speakers'], shell=True)
                self.icon.set_icon_name("audio-speakers")
                MODE=SPEAKERS_MODE
                
            elif (MODE == SPEAKERS_MODE):
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Headphone'], shell=True)
                self.icon.set_icon_name("audio-headphones")
                MODE=HEADPHONES_MODE
                
            else:
                self.icon.set_icon_name("dialog-error-symbolic")
            
                
            
            
            

    
    def terminate(self, window=None, data=None):
        Gtk.main_quit()


if __name__ == "__main__":

    Tray()
    Gtk.main()
