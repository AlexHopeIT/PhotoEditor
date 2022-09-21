from tkinter import *


class EnhanceSliderWindow(Toplevel):
    def __init__(self, root, name, enhance, image_info, update_method):
        super().__init__(root)

        self.name = name
        self.image_info = image_info
        self.enhancer = image_info.get_enhancer(enhance)
        self.original = image_info.image
        self.update_method = update_method

        self.init()

        self.factor = DoubleVar(value=1.0)
        self.scroll = Scale(
            self, label=self.name,
            from_=0.0, to=3.0, resolution=0.1, variable=self.factor,
            orient='horizontal',
            command=self.value_changed
        )
        self.apply = Button(self, text='Apply', command=self.apply)
        self.cancel = Button(self, text='Cancel', command=self.cancel)

        self.draw_widgets()

    def init(self):
        self.title(f'Enhance {self.name}')
        self.grab_focus()

    def grab_focus(self):
        self.grab_set()
        self.focus_force()

    def draw_widgets(self):
        self.scroll.pack(fill='x', expand=1, padx=5, pady=5)
        self.apply.pack(side='left', expand=1, padx=5, pady=5)
        self.cancel.pack(side='left', expand=1, padx=5, pady=5)

    def value_changed(self, value):
        image = self.enhancer.enhance(self.factor.get())
        self.image_info.set_image(image)
        self.image_info.update_image_on_canvas()

    def apply(self):
        self.image_info.unsaved = True
        self.update_method(self.image_info)
        self.close()

    def cancel(self):
        self.image_info.set_image(self.original)
        self.image_info.update_image_on_canvas()
        self.update_method(self.image_info)
        self.close()

    def close(self):
        self.destroy()
