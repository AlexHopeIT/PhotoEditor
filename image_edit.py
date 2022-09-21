from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
import numpy as np


class ImageEdit:
    def __init__(self, image):
        self.original_image = image
        self.image = image.copy()

        self.canvas = None
        self.image_container = None
        self.zoom_container = None

        self.imscale = 1.0
        self.zoom_delta = 1.3

        self.sel_start_x = 0
        self.sel_start_y = 0
        self.sel_stop_x = 0
        self.sel_stop_y = 0
        self.sel_rect = None

    @property
    def image_tk(self):
        return ImageTk.PhotoImage(self.image)

    def set_canvas(self, canvas):
        self.canvas = canvas
        self._bind_zoom()
        self.zoom_container = self.canvas.create_rectangle(0, 0, self.image.width,
                                                           self.image.height, widht=0)
        self._show_zoomed_image()

    def rotate(self, degrees):
        self.image = self.image.rotate(degrees)

    def flip(self, mode):
        self.image = self.image.transpose(mode)

    def resize(self, percents):
        w, h = self.image.size
        w = (w * percents) // 100
        h = (h * percents) // 100

        self.image = self.image.resize((w, h), Image.ANTIALIAS)

    def filter(self, filter_type):
        self.image = self.image.filter(filter_type)

    def convert(self, mode):
        if mode == "roll":
            if self.image.mode != "RGB":
                raise ValueError(f"Can't roll image with not RGB mode '{self.image.mode}'")

            self.image = Image.fromarray(np.array(self.image)[:, :, ::-1])
            return
        elif mode in "R G B".split(' '):
            if self.image.mode != "RGB":
                raise ValueError(f"Can't split channel of image with not RGB mode '{self.image.mode}'")

            a = np.array(self.image)
            a[:, :, (mode != "R", mode != "G", mode != "B")] *= 0
            self.image = Image.fromarray(a)
            return

        try:
            self.image = self.image.convert(mode)
        except ValueError as e:
            raise ValueError(f'Conversion error: "{e}"')

    def start_crop_selection(self):
        self.sel_rect = self.canvas.create_rectangle(
            self.sel_start_x, self.sel_start_y,
            self.sel_stop_x, self.sel_stop_y,
            dash=(10, 10), fill="cyan", width=1,
            stipple="gray25", outline="black"
        )

        self.canvas.bind("<Button-1>", self._get_selection_start)
        self.canvas.bind("<B1-Motion>", self._update_selection_stop)

    def _get_selection_start(self, event):
        self.sel_start_x, self.sel_start_y = event.x, event.y

    def _update_selection_stop(self, event):
        self.sel_stop_x, self.sel_stop_y = event.x, event.y
        self.canvas.coords(self.sel_rect, self.sel_start_x, self.sel_start_y, self.sel_stop_x, self.sel_stop_y)

    def crop_selected_area(self):
        if self.sel_rect is None:
            raise ValueError("Got no selection area for Crop operation")

        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.delete(self.sel_rect)

        if self.sel_start_x > self.sel_stop_x:
            self.sel_start_x, self.sel_stop_x = self.sel_stop_x, self.sel_start_x
        if self.sel_start_y > self.sel_stop_y:
            self.sel_start_y, self.sel_stop_y = self.sel_stop_y, self.sel_start_y

        self.image = self.image.crop([self.sel_start_x, self.sel_start_y, self.sel_stop_x, self.sel_stop_y])

        self.sel_rect = None
        self.sel_start_x, self.sel_start_y = 0, 0
        self.sel_stop_x, self.sel_stop_y = 0, 0

    def get_enhancer(self, enhancer):
        return enhancer(self.image)

    def set_image(self, image):
        self.image = image

    def _bind_zoom(self):
        self.canvas.bind('ButtonPress-1', self._move_from)
        self.canvas.bind('B1-Motion', self._move_to)
        self.canvas.bind('MouseWheel', self._zoom_with_wheel)  # for Windows and MacOS
        self.canvas.bind('Button-4', self._zoom_with_wheel)  # dor Linux
        self.canvas.bind('Button-5', self._zoom_with_wheel)  # dor Linux

    def _unbind_zoom(self):
        self.canvas.unbind('ButtonPress-1')
        self.canvas.unbind('B1-Motion')
        self.canvas.unbind('MouseWheel')
        self.canvas.unbind('Button-4')
        self.canvas.unbind('Button-5')

    def _move_from(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _move_to(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._show_zoomed_image()

    def _zoom_with_wheel(self, event):
        pass
