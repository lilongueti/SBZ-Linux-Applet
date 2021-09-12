#!/usr/bin/python3
from gi.repository import Gtk, XApp
import gi
import subprocess
from packaging import version

gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, XApp

SPEAKERS_MODE=("Speakers")
HEADPHONES_MODE=("Headphone")


def get_output(commands):
    process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out, err = process.communicate()
    return out.decode('utf-8').strip()


class Tray:
    MODE = "Headphone"
    def __init__(self):

        self.icon = XApp.StatusIcon()
        self.icon.set_name("SBZ")

        card = subprocess.check_output("aplay -l | grep Creative", shell=True).decode("UTF-8").strip().split(": ")[0]
        card=card[card.__len__()-1]
        
        
        output = None
        try:
            output = subprocess.check_output("amixer -c "+card+" sget 'Output Select' | grep -i 'Item0'", shell=True).decode("UTF-8").strip().split(": ")[1]
        except:
            pass

        
        speakers = Gtk.MenuItem(label=("Switch to: %s") % SPEAKERS_MODE)
        speakers.connect("activate", self.switch, SPEAKERS_MODE, card)

        
        headphones = Gtk.MenuItem(label=("Switch to: %s") % HEADPHONES_MODE)
        headphones.connect("activate", self.switch, HEADPHONES_MODE, card)

        
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
        
            
            if (self.MODE == HEADPHONES_MODE):
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Speakers'], shell=True)
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","Front", 'on'], shell=True)
                subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-sink alsa_output.pci-0000_06_00.0.analog-stereo"], shell=True)
                subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-source alsa_input.pci-0000_06_00.0.analog-stereo"], shell=True)
                self.icon.set_icon_name("audio-speakers")
                self.MODE=SPEAKERS_MODE
                
            elif (self.MODE == SPEAKERS_MODE):
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Headphone'], shell=True)
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","Front", 'on'], shell=True)
                #Todo search Card id on pulseaudio
                subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-sink alsa_output.pci-0000_06_00.0.analog-stereo"], shell=True)
                subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-source alsa_input.pci-0000_06_00.0.analog-stereo"], shell=True)
                
                self.icon.set_icon_name("audio-headphones")
                self.MODE=HEADPHONES_MODE
                
            else:
                self.icon.set_icon_name("dialog-error-symbolic")
            
                
            
            
            

    
    def terminate(self, window=None, data=None):
        Gtk.main_quit()


if __name__ == "__main__":

    Tray()
    Gtk.main()
