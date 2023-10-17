#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from packaging import version
import time
import subprocess
from gi.repository import Gtk
SPEAKERS_MODE = ("Speakers")
HEADPHONES_MODE = ("Headphone")


def get_output(commands):
    process = subprocess.Popen(
        commands, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out, err = process.communicate()
    return out.decode('utf-8').strip()


class Tray:
    MODE = HEADPHONES_MODE
    PCIID = "0000\:05\:00.0"

    def __init__(self):
        self.icon = Gtk.StatusIcon()
        self.icon.set_from_icon_name('audio-speakers')
        self.icon.connect("popup-menu", self.right_click_event)
        self.icon.connect("activate", self.left_click_event)
        
        self.PCIID = subprocess.check_output(
            "lspci -D | grep 'Creative Labs'", shell=True).decode("UTF-8").strip().split(" Audio ")[0]
        self.PCIID = self.PCIID.replace(":", "_")
        #self.icon.set_name("SBZ")

        self.card = subprocess.check_output(
            "aplay -l | grep Creative", shell=True).decode("UTF-8").strip().split(": ")[0]
        self.card = self.card[self.card.__len__()-1]
        
        try:
            self.active_output = subprocess.check_output(
                "amixer -c "+self.card+" sget 'Output Select' | grep -i 'Item0'", shell=True).decode("UTF-8").strip().split(": ")[1]
        except:
            pass
        if (self.active_output == "'Speakers'"):
            self.icon.set_from_icon_name("audio-speakers")
            self.MODE = SPEAKERS_MODE
        elif (self.active_output == "'Headphone'"):
            self.icon.set_from_icon_name("audio-headphones")
            self.MODE = HEADPHONES_MODE
        else:
            self.icon.set_from_icon_name("dialog-error-symbolic")
            self.MODE = ("Unknown mode")
        subprocess.call(executable="/usr/bin/amixer",
                        args=[self.card, "sset", "Front", 'on'], shell=True)
        
    def left_click_event(self, status_icon):
        print("left click triggered")
        self.switch()
        
    def right_click_event(self, status_icon, button, time):
        
        position = Gtk.StatusIcon.position_menu
        self.menu().popup(None, None, position, status_icon, button, time)
    
    def menu(self):
        #speakers = Gtk.MenuItem(label=("Switch to: %s") % SPEAKERS_MODE)
        #speakers.connect("activate", self.switch, SPEAKERS_MODE, self.card)

        #headphones = Gtk.MenuItem(label=("Switch to: %s") % HEADPHONES_MODE)
        #headphones.connect("activate", self.switch, HEADPHONES_MODE, self.card)

        
        

        #self.icon.set_tooltip_text("%s\n%s" % ("Creative Sound Blaster Z", self.MODE))

        #halndler_id = self.icon.connect("activate", self.switch, self.card)
        menu = Gtk.Menu()
        InFX = "off" not in str(subprocess.check_output(
            "/usr/bin/amixer -c "+str(self.card)+" sget 'Enable InFX'", shell=True))
        
        SwitchOtput = Gtk.MenuItem(label="Switch output")
        SwitchOtput.connect("activate", lambda _, :self.switch())
        
        ToggleInFX = Gtk.MenuItem(label="Toggle InFX (%s)" %
                                  ("ON" if InFX else "OFF"))
        ToggleInFX.connect("activate", self.toggle_infx, ToggleInFX)

        OutFX = "off" not in str(subprocess.check_output(
            "/usr/bin/amixer -c "+str(self.card)+" sget 'Enable OutFX'", shell=True))
        ToggleOutFX = Gtk.MenuItem(
            label="Toggle OutFX (%s)" % ("ON" if OutFX else "OFF"))
        ToggleOutFX.connect("activate", self.toggle_outfx, ToggleOutFX)

        ResetSC = Gtk.MenuItem(label="Reset SC")
        ResetSC.connect("activate", self.ResetSC, ToggleInFX)
        exit = Gtk.MenuItem(label="Exit")
        exit.connect("activate", self.terminate)
        menu.append(SwitchOtput)
        menu.append(ToggleInFX)
        menu.append(ToggleOutFX)
        menu.append(ResetSC)
        menu.append(exit)
        menu.show_all()
        return menu
        # menu.show_all()
        #self.icon.set_secondary_menu(menu)
        #self.icon.set_primary_menu(None)
        

    #def dialog_closed(self, widget, event):
    #    return Gtk.ResponseType.NO

    def ResetSC(self, args, toggleinfx):
        #subprocess.call(executable="/usr/bin/virsh", args=["qemu:///system", "start","ResetSC"], shell=True)
        self.toggle_infx(args, toggleinfx)
        subprocess.call(executable="sh", args=["pkexec sh -c 'echo 1 > /sys/bus/pci/devices/" +
                        self.PCIID.replace("_", "\:")+"/remove; echo 1 > /sys/bus/pci/rescan'"], shell=True)
        time.sleep(3)
        subprocess.call(executable="sh", args=["pulseaudio -k"], shell=True)
        subprocess.call(executable="sh", args=["pulseaudio -D"], shell=True)
        #subprocess.call(executable="sh", args=["pacmd unload-module module-udev-detect && pacmd load-module module-udev-detect"], shell=True)

        subprocess.call(executable="sh", args=[
                        "/usr/bin/pactl set-default-sink alsa_output.pci-"+self.PCIID+".analog-stereo"], shell=True)
        subprocess.call(executable="sh", args=[
                        "/usr/bin/pactl set-default-source alsa_input.pci-"+self.PCIID+".analog-stereo"], shell=True)
        subprocess.call(executable="/usr/bin/amixer",
                        args=[self.card, "sset", "Front", 'on'], shell=True)
        subprocess.call(executable="sh", args=[
                        "/usr/bin/pactl set-default-sink alsa_output.pci-"+self.PCIID+".analog-stereo"], shell=True)
        subprocess.call(executable="sh", args=[
                        "/usr/bin/pactl set-default-source alsa_input.pci-"+self.PCIID+".analog-stereo"], shell=True)
        if (self.MODE == HEADPHONES_MODE):
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "'Output Select'", 'Headphone'], shell=True)
        elif (self.MODE == SPEAKERS_MODE):
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "'Output Select'", 'Speakers'], shell=True)
        subprocess.call(executable="/usr/bin/amixer",
                        args=[self.card, "sset", "'Enable InFX'", 'toggle'], shell=True)
        toggleinfx.set_label("Toggle InFX (On)")

    def toggle_infx(self, args, toggleinfx):
        subprocess.call(executable="/usr/bin/amixer",
                        args=[self.card, "sset", "'Enable InFX'", 'toggle'], shell=True)
        infx = "ON" if "off" not in str(subprocess.check_output(
            "/usr/bin/amixer -c "+str(self.card)+" sget 'Enable InFX'", shell=True)) else "OFF"
        toggleinfx.set_label("Toggle InFX (%s)" % infx)

    def toggle_outfx(self, args, toggleoutfx):
        subprocess.call(executable="/usr/bin/amixer",
                        args=[self.card, "sset", "'Enable OutFX'", 'toggle'], shell=True)
        outfx = "ON" if "off" not in str(subprocess.check_output(
            "/usr/bin/amixer -c "+str(self.card) + " sget 'Enable OutFX'", shell=True)) else "OFF"
        toggleoutfx.set_label("Toggle OutFX (%s)" % outfx)

    def switch(self):

        if (self.MODE == HEADPHONES_MODE):
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "'Output Select'", 'Speakers'], shell=True)
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "Front", 'on'], shell=True)
            subprocess.call(executable="sh", args=[
                            "/usr/bin/pactl set-default-sink alsa_output.pci-"+self.PCIID+".analog-stereo"], shell=True)
            subprocess.call(executable="sh", args=[
                            "/usr/bin/pactl set-default-source alsa_input.pci-"+self.PCIID+".analog-stereo"], shell=True)
            self.icon.set_from_icon_name("audio-speakers")
            self.MODE = SPEAKERS_MODE

        elif (self.MODE == SPEAKERS_MODE):
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "'Output Select'", 'Headphone'], shell=True)
            subprocess.call(executable="/usr/bin/amixer",
                            args=[self.card, "sset", "Front", 'on'], shell=True)
            subprocess.call(executable="sh", args=[
                            "/usr/bin/pactl set-default-sink alsa_output.pci-"+self.PCIID.replace("\:", "_")+".analog-stereo"], shell=True)
            subprocess.call(executable="sh", args=[
                            "/usr/bin/pactl set-default-source alsa_input.pci-"+self.PCIID.replace("\:", "_")+".analog-stereo"], shell=True)

            self.icon.set_from_icon_name("audio-headphones")
            self.MODE = HEADPHONES_MODE

        else:
            self.icon.set_from_icon_name("dialog-error-symbolic")
        return self

    def terminate(self, window=None, data=None):
        Gtk.main_quit()

def start():
    
    
    try:
        Tray()
        Gtk.main()
    finally:
        card = subprocess.check_output("aplay -l | grep Creative", shell=True).decode("UTF-8").strip().split(": ")[0]
        card = card[card.__len__()-1]
        if "off" not in str(subprocess.check_output("/usr/bin/amixer -c "+str(card)+" sget 'Enable InFX'", shell=True)):
            subprocess.call(executable="/usr/bin/amixer", args=[card, "sset", "'Enable InFX'", 'toggle'], shell=True)
    
        



start()