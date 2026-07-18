import sys
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio

class ProgressWindow(Adw.ApplicationWindow):
    def __init__(self, app, title, text):
        super().__init__(application=app, title=title)
        self.set_default_size(400, 150)
        self.set_resizable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(32)
        box.set_margin_bottom(32)
        box.set_margin_start(32)
        box.set_margin_end(32)

        label = Gtk.Label(label=text)
        label.add_css_class("title-4")
        box.append(label)

        self.pbar = Gtk.ProgressBar()
        box.append(self.pbar)
        
        self.set_content(box)

        GLib.timeout_add(50, self.pulse)

    def pulse(self):
        self.pbar.pulse()
        return True

class ProgressApp(Adw.Application):
    def __init__(self, title, text):
        super().__init__(application_id='com.github.tanaybhomia.Progress', flags=Gio.ApplicationFlags.NON_UNIQUE)
        self.title_str = title
        self.text_str = text
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = ProgressWindow(self, self.title_str, self.text_str)
        win.present()

def read_stdin(app):
    for _ in sys.stdin:
        pass
    GLib.idle_add(app.quit)

if __name__ == '__main__':
    title = sys.argv[1] if len(sys.argv) > 1 else "Converting..."
    text = sys.argv[2] if len(sys.argv) > 2 else "Please wait..."
    app = ProgressApp(title, text)
    
    t = threading.Thread(target=read_stdin, args=(app,), daemon=True)
    t.start()
    
    app.run(None)
