import os
import subprocess
import gi

try:
    gi.require_version('Nautilus', '4.0')
    gi.require_version('Gtk', '4.0')
except ValueError:
    pass
from gi.repository import Nautilus, GObject, Gtk, Gio

class MediaConverterExtension(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        if not files:
            return []
            
        is_image = False
        is_video = False
        
        for file in files:
            if file.is_directory():
                continue
            mime_type = file.get_mime_type()
            if mime_type.startswith("image/"):
                is_image = True
            elif mime_type.startswith("video/"):
                is_video = True
                
        if (is_image and is_video) or (not is_image and not is_video):
            return []

        menu_item = Nautilus.MenuItem(
            name="MediaConverter::Convert",
            label="Convert",
            tip=""
        )
        
        submenu = Nautilus.Menu()
        menu_item.set_submenu(submenu)
        
        formats = ["png", "jpg", "webp", "gif"] if is_image else ["mp4", "mkv", "webm", "gif"]
        media_type = "image" if is_image else "video"

        for fmt in formats:
            item = Nautilus.MenuItem(
                name=f"MediaConverter::{fmt}",
                label=fmt.upper(),
                tip=""
            )
            item.connect("activate", self.convert_files, files, fmt, media_type)
            submenu.append_item(item)

        return [menu_item]

    def convert_files(self, menu, files, target_fmt, media_type):
        for file in files:
            if file.is_directory():
                continue
                
            input_path = file.get_location().get_path()
            if not input_path:
                continue
                
            dir_name = os.path.dirname(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            default_name = f"{base_name}.{target_fmt}"
            
            dialog = Gtk.FileChooserNative.new(
                "Save Converted File",
                None,
                Gtk.FileChooserAction.SAVE,
                "Convert",
                "Cancel"
            )
            
            # Use current directory and suggested name
            dialog.set_current_folder(Gio.File.new_for_path(dir_name))
            dialog.set_current_name(default_name)
            
            def on_response(dialog, response_id, in_path=input_path, m_type=media_type, t_fmt=target_fmt):
                if response_id == Gtk.ResponseType.ACCEPT:
                    out_path = dialog.get_file().get_path()
                    if m_type == "image":
                        subprocess.Popen(["magick", in_path, out_path])
                        subprocess.Popen(["notify-send", "Conversion Complete", out_path])
                    elif m_type == "video":
                        cmd = f"ffmpeg -y -i '{in_path}' '{out_path}' && notify-send 'Video Conversion Complete' '{out_path}'"
                        subprocess.Popen(cmd, shell=True)
                        subprocess.Popen(["notify-send", "Video Conversion Started", f"Converting to {t_fmt.upper()}"])
            
            dialog.connect("response", on_response)
            dialog.show()
