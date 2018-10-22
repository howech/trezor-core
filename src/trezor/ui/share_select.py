from micropython import const

from trezor import loop, ui
from trezor.ui import Widget
from trezor.ui.button import BTN_CLICKED, Button

if __debug__:
    from apps.debug import input_signal


_W1 = const(1)
_W2 = const(2)
_W3 = const(3)
_W4 = const(4)
_W5 = const(5)
_W6 = const(6)


class ShareSelector(Widget):
    def __init__(self, content):
        self.content = content
        self.w1 = Button(
            ui.grid(6, n_y=4, n_x=3, cells_y=1), str(_W1), style=ui.BTN_KEY
        )
        self.w2 = Button(
            ui.grid(7, n_y=4, n_x=3, cells_y=1), str(_W2), style=ui.BTN_KEY
        )
        self.w3 = Button(
            ui.grid(8, n_y=4, n_x=3, cells_y=1), str(_W3), style=ui.BTN_KEY
        )
        self.w4 = Button(
            ui.grid(9, n_y=4, n_x=3, cells_y=1), str(_W4), style=ui.BTN_KEY
        )
        self.w5 = Button(
            ui.grid(10, n_y=4, n_x=3, cells_y=1), str(_W5), style=ui.BTN_KEY
        )
        self.w6 = Button(
            ui.grid(11, n_y=4, n_x=3, cells_y=1), str(_W6), style=ui.BTN_KEY
        )

    def render(self):
        self.w1.render()
        self.w2.render()
        self.w3.render()
        self.w4.render()
        self.w5.render()
        self.w6.render()

    def touch(self, event, pos):
        if self.w1.touch(event, pos) == BTN_CLICKED:
            return _W1
        if self.w2.touch(event, pos) == BTN_CLICKED:
            return _W2
        if self.w3.touch(event, pos) == BTN_CLICKED:
            return _W3
        if self.w4.touch(event, pos) == BTN_CLICKED:
            return _W4
        if self.w5.touch(event, pos) == BTN_CLICKED:
            return _W5
        if self.w6.touch(event, pos) == BTN_CLICKED:
            return _W6

    async def __iter__(self):
        if __debug__:
            result = await loop.spawn(super().__iter__(), self.content, input_signal)
            if isinstance(result, str):
                return int(result)
            else:
                return result
        else:
            return await loop.spawn(super().__iter__(), self.content)
