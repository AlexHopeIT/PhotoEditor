from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from PIL import Image, ImageTk, ImageOps, ImageFilter
from tkinter.ttk import Notebook
import os


class PhotoEditor:
    def __init__(self):
        self.root = Tk()
        # self.root.configure(height=150, width=150, bg='#943232') ?????????? how????
        self.image_tabs = Notebook(self.root)
        self.opened_images = []
        self.init()

    def init(self):
        self.root.title('PhotoEditor V 1.0')
        self.root.iconphoto(True, PhotoImage(file='resourses/icon.png'))

        self.image_tabs.enable_traversal()
        self.root.bind('<Escape>', self._close)

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        string_menu = Menu(self.root)

        menu_file = Menu(string_menu, tearoff=0)
        menu_file.add_command(label='Open', command=self.open_several_images)
        menu_file.add_separator()
        menu_file.add_command(label='Save as', command=self.save_image_as)
        menu_file.add_command(label='Save', command=self.save_image_in_program)
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


        string_menu.add_cascade(label='File', menu=menu_file)
        string_menu.add_cascade(label='Edit', menu=edit_menu)
        transform_menu.add_cascade(label='Rotate', menu=rotate_menu)
        edit_menu.add_cascade(label='Transform', menu=transform_menu)
        edit_menu.add_cascade(label='Flip', menu=flip_menu)
        edit_menu.add_cascade(label='Resize', menu=resize_menu)
        edit_menu.add_cascade(label='Filters', menu=filter_menu)

    def draw_widgets(self):
        self.image_tabs.pack(fill='both', expand=1)

    def open_several_images(self):
        paths_to_images = fd.askopenfilenames(filetypes=(('Images', '*.jpeg;*.png;*.jpg;*.bmp;*.ico'),))
        for path in paths_to_images:
            self.add_new_image(path)

    def add_new_image(self, paths_to_images):
        image = Image.open(paths_to_images)
        image_tk = ImageTk.PhotoImage(image)
        self.opened_images.append([paths_to_images, image])

        image_tab = Frame(self.image_tabs)

        image_label = Label(image_tab, image=image_tk)
        image_label.image = image_tk
        image_label.pack(side='bottom', fill='both', expand=True)

        self.image_tabs.add(image_tab, text=paths_to_images.split('/')[-1])
        self.image_tabs.select(image_tab)

    def get_things_for_work(self):
        """:returns current (tab, path, image)
        """
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None, None, None
        tab_number = self.image_tabs.index(current_tab)
        path, image = self.opened_images[tab_number]
        return current_tab, path, image

    def save_image_in_program(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        if path[-1] == '*':
            path = path[:-1]
        self.opened_images[tab_number][0] = path
        image.save(path)
        self.image_tabs.add(current_tab, text=path.split('/')[-1])

    def save_image_as(self):
        current_tab, path, image = self.get_things_for_work()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        old_path, old_ext = os.path.splitext(path)
        if old_path[-1] == '*':
            old_path = old_path[:-1]
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


    def update_image_in_app(self, current_tab, image):
        tab_number = self.image_tabs.index(current_tab)
        tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
        label = tab_frame.children['!label']
        self.opened_images[tab_number][1] = image
        image_tk = ImageTk.PhotoImage(image)
        label.configure(image=image_tk)
        label.image = image_tk

        image_path = self.opened_images[tab_number][0]
        if image_path[-1] != '*':
            image_path += '*'
            self.opened_images[tab_number][0] = image_path
            image_name = image_path.split('/')[-1]
            self.image_tabs.tab(current_tab, text=image_name)

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

    def _close(self, event=None):
        self.root.quit()


if __name__ == '__main__':
    PhotoEditor().run()
