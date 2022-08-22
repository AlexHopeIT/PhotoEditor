from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from PIL import Image, ImageTk, ImageOps
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

        string_menu.add_cascade(label='File', menu=menu_file)

        self.root.configure(menu=string_menu)

        edit_menu = Menu(string_menu, tearoff=0)

        transform_menu = Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label='Transform', menu=transform_menu)
        rotate_menu = Menu(transform_menu, tearoff=0)
        rotate_menu.add_command(label='Rotate left by 90', command=lambda: self.rotate_current_image(90))
        rotate_menu.add_command(label='Rotate right by 90', command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_command(label='Rotate left by 180', command=lambda: self.rotate_current_image(180))
        rotate_menu.add_command(label='Rotate right by 180', command=lambda: self.rotate_current_image(-180))
        transform_menu.add_cascade(label='Rotate', menu=rotate_menu)

        flip_menu = Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(label='Flip', menu=flip_menu)
        flip_menu.add_command(label='Flip horizontally', command=lambda: self.flip_image('horizontally'))
        flip_menu.add_command(label='Flip vertically', command=lambda: self.flip_image('vertically'))

        string_menu.add_cascade(label='Edit', menu=edit_menu)

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

    def save_image_in_program(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        path, image = self.opened_images[tab_number]
        if path[-1] == '*':
            path = path[:-1]
        self.opened_images[tab_number][0] = path
        image.save(path)
        self.image_tabs.add(current_tab, text=path.split('/')[-1])

    def save_image_as(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        old_path, old_ext = os.path.splitext(self.opened_images[tab_number][0])
        if old_path[-1] == '*':
            old_path = old_path[:-1]
        path_for_save = fd.asksaveasfilename(initialdir=old_path,
                                             filetypes=(('Images', '*.jpeg;*.png;*.jpg;*.bmp;*.ico'), ))
        if not path_for_save:
            return

        path_for_save, new_ext = os.path.splitext(path_for_save)
        if not new_ext:
            new_ext = old_ext
        elif old_ext != new_ext:
            mb.showerror('ERROR! Incorrect extension', f'New extension: {new_ext},'
                                                       f' and old extension: {old_ext}')
            return
        image = self.opened_images[tab_number][1]
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
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        image = self.opened_images[tab_number][1]
        image = image.rotate(degrees)

        self.update_image_in_app(current_tab, image)

    def flip_image(self, flip_type):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)
        image = self.opened_images[tab_number][1]
        if flip_type == 'horizontally':
            image = ImageOps.mirror(image)
        elif flip_type == 'vertically':
            image = ImageOps.flip(image)

        self.update_image_in_app(current_tab, image)


    def _close(self, event=None):
        self.root.quit()


if __name__ == '__main__':
    PhotoEditor().run()
