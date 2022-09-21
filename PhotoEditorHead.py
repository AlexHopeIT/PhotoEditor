from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import pyperclip
from PIL import Image, ImageFilter, ImageEnhance
from tkinter.ttk import Notebook
import os
import json

from enhance_slider_window import EnhanceSliderWindow
from image_info import ImageInfo

CONFIG_FILE = 'config.json'


class PhotoEditor:
    def __init__(self):
        self.root = Tk()
        # self.root.configure(height=150, width=150, bg='#943232') ?????????? how????
        self.image_tabs = Notebook(self.root)
        self.opened_images = []
        self.last_viewed_images = []

        self.open_recent_menu = None

        self.init()

    def init(self):
        self.root.title('PhotoEditor V 1.0')
        self.root.iconphoto(True, PhotoImage(file='resourses/icon.png'))

        self.image_tabs.enable_traversal()
        self.root.bind('<Escape>', self._close)
        self.root.protocol('WM_DELETE_WINDOW', self._close)

        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'opened_images': [], 'last_viewed_images': []}, f)
        else:
            self.open_images_from_config()

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        string_menu = Menu(self.root)

        menu_file = Menu(string_menu, tearoff=0)
        menu_file.add_command(label='Open', command=self.open_several_images)

        self.open_recent_menu = Menu(menu_file, tearoff=0)
        menu_file.add_cascade(label="Open Recent", menu=self.open_recent_menu)
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path, command=lambda x=path: self.add_new_image(x))

        menu_file.add_separator()

        menu_file.add_command(label='Save as', command=self.save_image_as)
        menu_file.add_command(label='Save', command=self.save_image_in_program)
        menu_file.add_command(label='Save all', command=self.save_all_images)
        menu_file.add_separator()

        menu_file.add_command(label='Close this image', command=self.close_current_image)
        menu_file.add_command(label='Close and delete this image', command=self.delete_current_image)
        menu_file.add_separator()

        clipboard_menu = Menu(menu_file, tearoff=0)
        clipboard_menu.add_command(label='Add name of image in clipboard',
                                   command=lambda: self.save_to_clipboard('name'))
        clipboard_menu.add_command(label='Add directory of image in clipboard',
                                   command=lambda: self.save_to_clipboard('dir'))
        clipboard_menu.add_command(label='Add path of image in clipboard',
                                   command=lambda: self.save_to_clipboard('path'))
        menu_file.add_cascade(label='Clipboard', menu=clipboard_menu)
        menu_file.add_separator()

        menu_file.add_command(label='Exit', command=self._close)

        self.root.configure(menu=string_menu)

        edit_menu = Menu(string_menu, tearoff=0)

        rotate_menu = Menu(edit_menu, tearoff=0)
        rotate_menu.add_command(label='Rotate left by 90', command=lambda: self.rotate_current_image(90))
        rotate_menu.add_command(label='Rotate right by 90', command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_command(label='Rotate left by 180', command=lambda: self.rotate_current_image(180))
        rotate_menu.add_command(label='Rotate right by 180', command=lambda: self.rotate_current_image(-180))

        flip_menu = Menu(edit_menu, tearoff=0)
        flip_menu.add_command(label='Flip horizontally', command=lambda: self.flip_image(Image.FLIP_LEFT_RIGHT))
        flip_menu.add_command(label='Flip vertically', command=lambda: self.flip_image(Image.FLIP_TOP_BOTTOM))

        resize_menu = Menu(edit_menu, tearoff=0)
        resize_menu.add_command(label='10% of original size', command=lambda: self.resize_current_image(10))
        resize_menu.add_command(label='20% of original size', command=lambda: self.resize_current_image(20))
        resize_menu.add_command(label='25% of original size', command=lambda: self.resize_current_image(25))
        resize_menu.add_command(label='40% of original size', command=lambda: self.resize_current_image(40))
        resize_menu.add_command(label='50% of original size', command=lambda: self.resize_current_image(50))
        resize_menu.add_command(label='65% of original size', command=lambda: self.resize_current_image(65))
        resize_menu.add_command(label='80% of original size', command=lambda: self.resize_current_image(80))
        resize_menu.add_command(label='120% of original size', command=lambda: self.resize_current_image(120))
        resize_menu.add_command(label='135% of original size', command=lambda: self.resize_current_image(135))
        resize_menu.add_command(label='150% of original size', command=lambda: self.resize_current_image(150))
        resize_menu.add_command(label='200% of original size', command=lambda: self.resize_current_image(200))

        filter_menu = Menu(edit_menu, tearoff=0)
        filter_menu.add_command(label='Blur', command=lambda: self.impose_filter(ImageFilter.BLUR))
        filter_menu.add_command(label='Contour', command=lambda: self.impose_filter(ImageFilter.CONTOUR))
        filter_menu.add_command(label='Detail', command=lambda: self.impose_filter(ImageFilter.DETAIL))
        filter_menu.add_command(label='Edge enhance', command=lambda: self.impose_filter(ImageFilter.EDGE_ENHANCE))
        filter_menu.add_command(label='Emboss', command=lambda: self.impose_filter(ImageFilter.EMBOSS))
        filter_menu.add_command(label='Find edges', command=lambda: self.impose_filter(ImageFilter.FIND_EDGES))
        filter_menu.add_command(label='Sharpen', command=lambda: self.impose_filter(ImageFilter.SHARPEN))
        filter_menu.add_command(label='Smooth', command=lambda: self.impose_filter(ImageFilter.SMOOTH))
        filter_menu.add_command(label='Smooth more', command=lambda: self.impose_filter(ImageFilter.SMOOTH_MORE))

        crop_menu = Menu(edit_menu, tearoff=0)
        crop_menu.add_command(label='Start selection', command=self.start_crop_selection_of_current_image)
        crop_menu.add_command(label='Crop selected', command=self.crop_selection_of_current_image)

        convert_menu = Menu(edit_menu, tearoff=0)
        convert_menu.add_command(label='Black and White', command=lambda: self.convert_current_image('1'))
        convert_menu.add_command(label='More Grey', command=lambda: self.convert_current_image('L'))
        convert_menu.add_command(label='RGB', command=lambda: self.convert_current_image('RGB'))
        convert_menu.add_command(label='RGBA', command=lambda: self.convert_current_image('RGBA'))
        convert_menu.add_command(label='CMYK', command=lambda: self.convert_current_image('CMYK'))
        convert_menu.add_command(label='YCbCr', command=lambda: self.convert_current_image('YCbCr'))
        convert_menu.add_command(label='LAB', command=lambda: self.convert_current_image('LAB'))
        convert_menu.add_command(label='HSV', command=lambda: self.convert_current_image('HSV'))
        convert_menu.add_command(label='32-bit signed integer pixels', command=lambda: self.convert_current_image('I'))
        convert_menu.add_command(label='32-bit floating point pixels', command=lambda: self.convert_current_image('F'))
        convert_menu.add_command(label='Roll RGB colors', command=lambda: self.convert_current_image('roll'))
        convert_menu.add_command(label='Red', command=lambda: self.convert_current_image('R'))
        convert_menu.add_command(label='Green', command=lambda: self.convert_current_image('G'))
        convert_menu.add_command(label='Blue', command=lambda: self.convert_current_image('B'))

        enhance_menu = Menu(edit_menu, tearoff=0)
        enhance_menu.add_command(label='Color', command=lambda: self.enhance_current_image('Color', ImageEnhance.Color))
        enhance_menu.add_command(label='Contrast',
                                 command=lambda: self.enhance_current_image('Contrast', ImageEnhance.Contrast))
        enhance_menu.add_command(label='Brightness',
                                 command=lambda: self.enhance_current_image('Brightness', ImageEnhance.Brightness))
        enhance_menu.add_command(label='Sharpness',
                                 command=lambda: self.enhance_current_image('Sharpness', ImageEnhance.Color))

        string_menu.add_cascade(label='File', menu=menu_file)
        string_menu.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_cascade(label='Rotate', menu=rotate_menu)
        edit_menu.add_cascade(label='Flip', menu=flip_menu)
        edit_menu.add_cascade(label='Resize', menu=resize_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label='Filters', menu=filter_menu)
        edit_menu.add_cascade(label='Enhance', menu=enhance_menu)
        edit_menu.add_cascade(label='Convert', menu=convert_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label='Crop', menu=crop_menu)

    def update_recent_menu(self):
        if self.open_recent_menu is None:
            return

        self.open_recent_menu.delete(0, 'end')
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path,
                                              command=lambda x=path: self.add_new_image(x))

    def draw_widgets(self):
        self.image_tabs.pack(fill='both', expand=1)

    def open_several_images(self):
        paths_to_images = fd.askopenfilenames(filetypes=(('Images', '*.jpeg;*.png;*.jpg;*.bmp;*.ico'),))
        for image_path in paths_to_images:
            self.add_new_image(image_path)

            if image_path not in self.last_viewed_images:
                self.last_viewed_images.append(image_path)
            else:
                self.last_viewed_images.remove(image_path)
                self.last_viewed_images.append(image_path)

            if len(self.last_viewed_images) > 5:
                del self.last_viewed_images[0]

        self.update_recent_menu()

    def open_images_from_config(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        self.last_viewed_images = config['last_viewed_images']
        paths = config['opened_images']
        for path in paths:
            self.add_new_image(path)

    def add_new_image(self, image_path):
        if not os.path.isfile(image_path):
            if image_path in self.last_viewed_images:
                self.last_viewed_images.remove(image_path)
                self.update_recent_menu()
            return

        opened_images = [info.path for info in self.opened_images]
        if image_path in opened_images:
            index = opened_images.index(image_path)
            self.image_tabs.select(index)
            return

        image = Image.open(image_path)
        image_tab = Frame(self.image_tabs)

        image_info = ImageInfo(image, image_path, image_tab)
        self.opened_images.append(image_info)

        image_tk = image_info.image_tk

        image_panel = Canvas(image_tab, width=image.width,
                             height=image.height, bd=0, highlightthickness=0)
        image_panel.image = image_tk
        image_panel.create_image(0, 0, image=image_tk, anchor='nw')
        image_panel.pack(expand="yes")

        image_info.canvas = image_panel

        self.image_tabs.add(image_tab, text=image_info.file_name())
        self.image_tabs.select(image_tab)

    def current_image(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None
        tab_number = self.image_tabs.index(current_tab)
        return self.opened_images[tab_number]

    def save_image_in_program(self):
        image = self.current_image()
        if not image:
            return
        if not image.unsaved:
            return
        image.save()
        self.image_tabs.add(image.tab, text=image.file_name())

    def save_image_as(self):
        image = self.current_image()
        if not image:
            return
        try:
            image.save_as()
            self.update_image_in_app(image)
        except ValueError as e:
            mb.showerror('Save as error', str(e))

    def save_all_images(self):
        for image_info in self.opened_images:
            if not image_info.unsaved:
                continue
            image_info.save()
            self.image_tabs.add(image_info.tab, text=image_info.file_name())

    def update_image_in_app(self, image_info):
        image_info.update_image_on_canvas()
        self.image_tabs.tab(image_info.tab, text=image_info.file_name())

    def close_current_image(self):
        if self.unsaved_images():
            if not mb.askyesno("Unsaved changes", "Got unsaved changes! Exit anyway?"):
                return

        self.save_images_to_config()
        self.root.quit()

    def delete_current_image(self):
        image = self.current_image()
        if not image:
            return

        if not mb.askokcancel('Delete image', 'Are you sure you wanna delete this image?\n'
                                              'This operation is unrecoverable'):
            return

        image.delete()
        self.image_tabs.forget(image.tab)
        self.opened_images.remove(image)

    def rotate_current_image(self, degrees):
        image = self.current_image()
        if not image:
            return

        image.rotate(degrees)
        image.unsaved = True
        self.update_image_in_app(image)

    def flip_image(self, mode):
        image = self.current_image()
        if not image:
            return

        image.flip(mode)
        image.unsaved = True
        self.update_image_in_app(image)

    def resize_current_image(self, percents):
        image = self.current_image()
        if not image:
            return

        image.resize(percents)
        image.unsaved = True
        self.update_image_in_app(image)

    def impose_filter(self, filter_type):
        image = self.current_image()
        if not image:
            return

        image.filter(filter_type)
        image.unsaved = True
        self.update_image_in_app(image)

    def start_crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        image.start_crop_selection()

    def crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return

        try:
            image.crop_selected_area()
            image.unsaved = True
            self.update_image_in_app(image)
        except ValueError as e:
            mb.showerror("Crop error", str(e))

    def convert_current_image(self, mode):
        image = self.current_image()
        if not image:
            return

        try:
            image.convert(mode)
            image.unsaved = True
            self.update_image_in_app(image)
        except ValueError as e:
            mb.showerror('Convert error', str(e))

    def enhance_current_image(self, name, enhance):
        image = self.current_image()
        if not image:
            return
        EnhanceSliderWindow(self.root, name, enhance, image, self.update_image_in_app)

    def save_to_clipboard(self, mode):
        image = self.current_image()
        if not image:
            return

        if mode == 'name':
            pyperclip.copy(image.file_name(no_star=True))
        elif mode == 'dir':
            pyperclip.copy(image.directory(no_star=True))
        elif mode == 'path':
            pyperclip.copy(image.full_path(no_star=True))

    def save_images_to_config(self):
        paths = [info.full_path(no_star=True) for info in self.opened_images]
        images = {'opened_images': paths, 'last_viewed_images': self.last_viewed_images}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(images, f, indent=4)

    def unsaved_images(self):
        for info in self.opened_images:
            if info.unsaved:
                return True
        return False

    def _close(self, event=None):
        if self.unsaved_images():
            if not mb.askyesno("Unsaved changes", "Got unsaved changes! Exit anyway?"):
                return

        self.save_images_to_config()
        self.root.quit()


if __name__ == '__main__':
    PhotoEditor().run()
