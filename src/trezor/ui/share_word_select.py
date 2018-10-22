from micropython import const

from trezor import loop, ui
from trezor.ui import Widget
from trezor.ui.button import BTN_CLICKED, Button

if __debug__:
    from apps.debug import input_signal


_W15 = const(15)
_W21 = const(21)


class ShareWordSelector(Widget):
    def __init__(self, content):
        self.content = content
        self.w15 = Button(
            ui.grid(13, n_y=4, n_x=6, cells_y=2, cells_x=2), str(_W15), style=ui.BTN_KEY
        )
        self.w21 = Button(
            ui.grid(15, n_y=4, n_x=6, cells_y=2, cells_x=2), str(_W21), style=ui.BTN_KEY
        )

    def render(self):
        self.w15.render()
        self.w21.render()

    def touch(self, event, pos):
        if self.w15.touch(event, pos) == BTN_CLICKED:
            return _W15
        if self.w21.touch(event, pos) == BTN_CLICKED:
            return _W21

    async def __iter__(self):
        if __debug__:
            result = await loop.spawn(super().__iter__(), self.content, input_signal)
            if isinstance(result, str):
                return int(result)
            else:
                return result
        else:
            return await loop.spawn(super().__iter__(), self.content)
