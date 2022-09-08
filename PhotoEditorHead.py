from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import pyperclip
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
from tkinter.ttk import Notebook
import os
import json
import numpy as np

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

        self.selection_top_x = 0
        self.selection_top_y = 0
        self.selection_bottom_x = 0
        self.selection_bottom_y = 0

        self.canvas_for_selection = None
        self.selection_rect = None

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
        clipboard_menu.add_command(label='Add name of image in clipboard', command=self.save_name_in_clipboard)
        clipboard_menu.add_command(label='Add directory of image in clipboard',
                                   command=self.save_directory_in_clipboard)
        clipboard_menu.add_command(label='Add path of image in clipboard', command=self.save_path_in_clipboard)
        menu_file.add_cascade(label='Clipboard', menu=clipboard_menu)
        menu_file.add_separator()

        menu_file.add_command(label='Exit', command=self._close)

        self.root.configure(menu=string_menu)

        edit_menu = Menu(string_menu, tearoff=0)

        transform_menu = Menu(edit_menu, tearoff=0)
        rotate_menu = Menu(transform_menu, tearoff=0)
        rotate_menu.add_command(label='Rotate left by 90', command=lambda: self.rotate_current_image(90))
        rotate_menu.add_command(label='Rotate right by 90', command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_command(label='Rotate left by 180', command=lambda: self.rotate_current_image(180))
        rotate_menu.add_command(label='Rotate right by 180', command=lambda: self.rotate_current_image(-180))

        flip_menu = Menu(edit_menu, tearoff=0)
        flip_menu.add_command(label='Flip horizontally', command=lambda: self.flip_image('horizontally'))
        flip_menu.add_command(label='Flip vertically', command=lambda: self.flip_image('vertically'))

        resize_menu = Menu(edit_menu, tearoff=0)
        resize_menu.add_command(label='10% of original size', command=lambda: self.resize_image(10))
        resize_menu.add_command(label='20% of original size', command=lambda: self.resize_image(20))
        resize_menu.add_command(label='25% of original size', command=lambda: self.resize_image(25))
        resize_menu.add_command(label='40% of original size', command=lambda: self.resize_image(40))
        resize_menu.add_command(label='50% of original size', command=lambda: self.resize_image(50))
        resize_menu.add_command(label='65% of original size', command=lambda: self.resize_image(65))
        resize_menu.add_command(label='80% of original size', command=lambda: self.resize_image(80))
        resize_menu.add_command(label='120% of original size', command=lambda: self.resize_image(120))
        resize_menu.add_command(label='135% of original size', command=lambda: self.resize_image(135))
        resize_menu.add_command(label='150% of original size', command=lambda: self.resize_image(150))
        resize_menu.add_command(label='200% of original size', command=lambda: self.resize_image(200))

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
        crop_menu.add_command(label='Start selection', command=self.start_selection)
        crop_menu.add_command(label='Stop selection', command=self.stop_selection)

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
        transform_menu.add_cascade(label='Rotate', menu=rotate_menu)
        edit_menu.add_cascade(label='Transform', menu=transform_menu)
        edit_menu.add_cascade(label='Flip', menu=flip_menu)
        edit_menu.add_cascade(label='Resize', menu=resize_menu)
        edit_menu.add_cascade(label='Filters', menu=filter_menu)
        edit_menu.add_cascade(label='Crop', menu=crop_menu)
        edit_menu.add_cascade(label='Convert', menu=convert_menu)
        edit_menu.add_cascade(label='Enhance', menu=enhance_menu)

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

    def get_things_for_work(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None
        tab_number = self.image_tabs.index(current_tab)
        return self.opened_images[tab_number]

    def save_image_in_program(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        if path[-1] == '*':
            path = path[:-1]
        self.opened_images[tab_number][0] = path
        image.save(path)
        self.image_tabs.add(current_tab, text=os.path.split(path)[1])

    def save_image_as(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        old_path, old_ext = os.path.splitext(path)
        if old_ext[-1] == '*':
            old_ext = old_ext[:-1]
        path_for_save = fd.asksaveasfilename(initialdir=old_path,
                                             filetypes=(('Images', '*.jpeg;*.png;*.jpg;*.bmp;*.ico'),))
        if not path_for_save:
            return

        path_for_save, new_ext = os.path.splitext(path_for_save)
        if not new_ext:
            new_ext = old_ext
        elif old_ext != new_ext:
            mb.showerror('ERROR! Incorrect extension', f'New extension: {new_ext},'
                                                       f' and old extension: {old_ext}')
            return

        image.save(path_for_save + new_ext)
        image.close()

        del self.opened_images[tab_number]
        self.image_tabs.forget(current_tab)

        self.add_new_image(path_for_save + new_ext)

    def save_all_images(self):
        for index, (path, image) in enumerate(self.opened_images):
            if path[-1] != '*':
                continue
            path = path[:-1]
            self.opened_images[index][0] = path
            image.save(path)
            self.image_tabs.tab(index, text=os.path.split(path)[1])

    def update_image_in_app(self, current_tab, image):
        tab_number = self.image_tabs.index(current_tab)
        tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
        canvas = tab_frame.children['!canvas']
        self.opened_images[tab_number][1] = image
        image_tk = ImageTk.PhotoImage(image)

        canvas.delete('all')
        canvas.image = image_tk
        canvas.configure(width=image_tk.width(), height=image_tk.height())
        canvas.create_image(0, 0, image=image_tk, anchor='nw')

        image_path = self.opened_images[tab_number][0]
        if image_path[-1] != '*':
            image_path += '*'
            self.opened_images[tab_number][0] = image_path
            image_name = os.path.split(image_path)[1]
            self.image_tabs.tab(current_tab, text=image_name)

    def close_current_image(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        index = self.image_tabs.index(current_tab)

        image.close()

        del self.opened_images[index]
        self.image_tabs.forget(current_tab)

    def delete_current_image(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        index = self.image_tabs.index(current_tab)

        if not mb.askokcancel('Delete image', 'Are you sure you wanna delete this image?\n'
                                              'This operation is unrecoverable'):
            return

        image.close()
        os.remove(path)

        del self.opened_images[index]
        self.image_tabs.forget(current_tab)

    def rotate_current_image(self, degrees):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        image = image.rotate(degrees)

        self.update_image_in_app(current_tab, image)

    def flip_image(self, flip_type):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        if flip_type == 'horizontally':
            image = ImageOps.mirror(image)
        elif flip_type == 'vertically':
            image = ImageOps.flip(image)

        self.update_image_in_app(current_tab, image)

    def resize_image(self, percents):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        w, h = image.size
        w = (w * percents) // 100
        h = (h * percents) // 100

        image = image.resize((w, h), Image.ANTIALIAS)
        self.update_image_in_app(current_tab, image)

    def impose_filter(self, filter_type):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        image = image.filter(filter_type)
        self.update_image_in_app(current_tab, image)

    def start_selection(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
        canvas = tab_frame.children['!canvas']

        self.canvas_for_selection = canvas
        self.selection_rect = canvas.create_rectangle(self.selection_top_x, self.selection_top_y,
                                                      self.selection_bottom_x, self.selection_bottom_y,
                                                      dash=(10, 10), fill='', outline='yellow', width=3
                                                      )

        canvas.bind("<Button-1>", self.get_selection_start_pos)
        canvas.bind("<B1-Motion>", self.update_selection_end_pos)

    def get_selection_start_pos(self, event):
        self.selection_top_x, self.selection_top_y = event.x, event.y

    def update_selection_end_pos(self, event):
        self.selection_bottom_x, self.selection_bottom_y = event.x, event.y
        if self.canvas_for_selection is not None and self.selection_rect is not None:
            self.canvas_for_selection.coords(
                self.selection_rect,
                self.selection_top_x, self.selection_top_y,
                self.selection_bottom_x, self.selection_bottom_y
            )

    def stop_selection(self):
        self.canvas_for_selection.unbind("<Button-1>")
        self.canvas_for_selection.unbind("<B1-Motion>")

        self.canvas_for_selection.delete(self.selection_rect)

        self.crop_at_selection()

        self.selection_rect = None
        self.canvas_for_selection = None
        self.selection_top_x, self.selection_top_y = 0, 0
        self.selection_bottom_x, self.selection_bottom_y = 0, 0

    def crop_at_selection(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        image = image.crop((self.selection_top_x, self.selection_top_y,
                            self.selection_bottom_x, self.selection_bottom_y))
        self.update_image_in_app(current_tab, image)

    def convert_current_image(self, mode):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        if mode == 'roll':
            if image.mode != 'RGB':
                mb.showerror('RGB mode error', f'Can`t roll with not RGB mode "{image.mode}"')
                return

            image = Image.fromarray(np.array(image)[:, :, ::-1])
            self.update_image_in_app(current_tab, image)
            return

        elif mode in 'R G B'.split(' '):
            if image.mode != 'RGB':
                mb.showerror('RGB mode error', f'Can`t split channel with not RGB mode "{image.mode}"')
                return
            colors_channel = np.array(image)
            colors_channel[:, :, (mode != 'R', mode != 'G', mode != 'B')] *= 0
            image = Image.fromarray(colors_channel)
            self.update_image_in_app(current_tab, image)
            return

        try:
            image = image.convert(mode)
            self.update_image_in_app(current_tab, image)
        except ValueError as e:
            mb.showerror('Conversion error', f'Conversion error: {e}')

    def enhance_current_image(self, name, enhance):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        EnhanceSliderWindow(self.root, name, enhance, image, current_tab, self.update_image_in_app)

    def save_name_in_clipboard(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        name = os.path.split(path)[1]
        pyperclip.copy(name)

        mb.showinfo('Clipboard', f'Name {name} copy to clipboard')

    def save_directory_in_clipboard(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        directory = os.path.split(path)[0]
        pyperclip.copy(directory)

        mb.showinfo('Clipboard', f'Directory {directory} copy to clipboard')

    def save_path_in_clipboard(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return

        pyperclip.copy(path)

        mb.showinfo('Clipboard', f'Path {path} copy to clipboard')

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
            if not mb.askyesno('There are unsaved changes of images', 'You need to save changes. Exit anyway?'):
                return

        self.save_images_to_config()
        self.root.quit()


if __name__ == '__main__':
    PhotoEditor().run()
