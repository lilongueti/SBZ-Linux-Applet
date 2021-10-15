#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, XApp
#import gi
import subprocess
import time
from packaging import version

#gi.require_version('Gtk', '4.0')
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
            self.MODE = SPEAKERS_MODE
        elif (active_output == "'Headphone'"):
            self.icon.set_icon_name("audio-headphones")
            self.MODE = HEADPHONES_MODE
        else:
            self.icon.set_icon_name("dialog-error-symbolic")
            self.MODE = ("Unknown mode")

        self.icon.set_tooltip_text("%s\n%s" % ("Creative Sound Blaster Z", self.MODE))
        
        halndler_id=self.icon.connect("activate",self.switch, card)
        
        menu = Gtk.Menu()
        InFX =  "off" not in str(subprocess.check_output("/usr/bin/amixer -c 1 sget 'Enable InFX'", shell=True))
        ToggleInFX = Gtk.MenuItem(label="Toggle InFX (%s)" % ("ON" if InFX else "OFF"))
        ToggleInFX.connect("activate", self.toggle_infx, card, ToggleInFX)
        
        OutFX =  "off" not in str(subprocess.check_output("/usr/bin/amixer -c 1 sget 'Enable OutFX'", shell=True))
        ToggleOutFX = Gtk.MenuItem(label="Toggle OutFX (%s)" % ("ON" if OutFX else "OFF"))
        ToggleOutFX.connect("activate", self.toggle_outfx, card, ToggleOutFX)
        
        ResetSC = Gtk.MenuItem(label="Reset SC")
        ResetSC.connect("activate", self.ResetSC,card)
        exit = Gtk.MenuItem(label="Exit")
        exit.connect("activate", self.terminate)        
        menu.append(ToggleInFX)
        menu.append(ToggleOutFX)
        menu.append(ResetSC)
        menu.append(exit)
        menu.show_all()
            
        #menu.show_all()
        self.icon.set_secondary_menu(menu)
        self.icon.set_primary_menu(None)
        subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","Front", 'on'], shell=True)
        

    

    def dialog_closed(self, widget, event):
        return Gtk.ResponseType.NO
    
    def ResetSC(self, args, card):
        subprocess.call(executable="/usr/bin/virsh", args=["qemu:///system", "start","ResetSC"], shell=True)
        time.sleep(4)
        subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-sink alsa_output.pci-0000_06_00.0.analog-stereo"], shell=True)
        subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-source alsa_input.pci-0000_06_00.0.analog-stereo"], shell=True)
        subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","Front", 'on'], shell=True)
        subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-sink alsa_output.pci-0000_06_00.0.analog-stereo"], shell=True)
        subprocess.call(executable="sh", args=["/usr/bin/pactl set-default-source alsa_input.pci-0000_06_00.0.analog-stereo"], shell=True)

    def toggle_infx(self, args, card, toggleinfx):
        subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Enable InFX'", 'toggle'], shell=True)
        infx="ON" if "off" not in str(subprocess.check_output("/usr/bin/amixer -c "+str(card)+" sget 'Enable InFX'", shell=True)) else "OFF"
        toggleinfx.set_label("Toggle InFX (%s)" %  infx )

    def toggle_outfx(self, args, card, toggleoutfx):
        subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Enable OutFX'", 'toggle'], shell=True)
        outfx="ON" if "off" not in str(subprocess.check_output("/usr/bin/amixer -c "+str(card)+ " sget 'Enable OutFX'", shell=True)) else "OFF"
        toggleoutfx.set_label("Toggle OutFX (%s)" %  outfx)
        

    def switch(self,args,id, widget, card):
        
            
            if (self.MODE == HEADPHONES_MODE):
				#Todo veo la version de la kernel para saber si lo pongo en Surround o Speakers
                subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Speakers'], shell=True)
                #subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'Output Select'", 'Surround'], shell=True)
                #subprocess.call(executable="/usr/bin/amixer", args=[card, "sset","'FX: Crystalizer'", '0'], shell=True)
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
