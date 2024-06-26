'''
Text Pygame: Draw text with pygame

.. warning::

    Pygame has been deprecated and will be removed in the release after Kivy
    1.11.0.
'''

__all__ = ('LabelPygame', )

from kivy.core.text import LabelBase
from kivy.core.image import ImageData
from kivy.utils import deprecated

try:
    import pygame
except:
    raise

pygame_cache = {}
pygame_font_handles = {}
pygame_cache_order = []

# init pygame font
try:
    pygame.ftfont.init()
except:
    pygame.font.init()


class LabelPygame(LabelBase):

    @deprecated(
        msg='Pygame has been deprecated and will be removed after 1.11.0')
    def __init__(self, *largs, **kwargs):
        super(LabelPygame, self).__init__(*largs, **kwargs)

    def _get_font_id(self):
        return '|'.join([str(self.options[x]) for x in
                         ('font_size', 'font_name_r', 'bold', 'italic')])

    def _get_font(self):
        fontid = self._get_font_id()
        if fontid not in pygame_cache:
            # try first the file if it's a filename
            font_handle = fontobject = None
            fontname = self.options['font_name_r']
            ext = fontname.rsplit('.', 1)
            if len(ext) == 2:
                # try to open the font if it has an extension
                font_handle = open(fontname, 'rb')
                fontobject = pygame.font.Font(font_handle,
                                              int(self.options['font_size']))

            # fallback to search a system font
            if fontobject is None:
                # try to search the font
                font = pygame.font.match_font(
                    self.options['font_name_r'].replace(' ', ''),
                    bold=self.options['bold'],
                    italic=self.options['italic'])

                # fontobject
                fontobject = pygame.font.Font(font,
                                              int(self.options['font_size']))
            pygame_cache[fontid] = fontobject
            pygame_font_handles[fontid] = font_handle
            pygame_cache_order.append(fontid)

        # to prevent too much file open, limit the number of opened fonts to 64
        while len(pygame_cache_order) > 64:
            popid = pygame_cache_order.pop(0)
            del pygame_cache[popid]
            font_handle = pygame_font_handles.pop(popid)
            if font_handle is not None:
                font_handle.close()

        return pygame_cache[fontid]

    def get_ascent(self):
        return self._get_font().get_ascent()

    def get_descent(self):
        return self._get_font().get_descent()

    def get_extents(self, text):
        return self._get_font().size(text)

    def get_cached_extents(self):
        return self._get_font().size

    def _render_begin(self):
        self._pygame_surface = pygame.Surface(self._size, pygame.SRCALPHA, 32)
        self._pygame_surface.fill((0, 0, 0, 0))

    def _render_text(self, text, x, y):
        font = self._get_font()
        color = [c * 255 for c in self.options['color']]
        color[0], color[2] = color[2], color[0]
        try:
            text = font.render(text, True, color)
            text.set_colorkey(color)
            self._pygame_surface.blit(text, (x, y), None,
                                      pygame.BLEND_RGBA_ADD)
        except pygame.error:
            pass

    def _render_end(self):
        w, h = self._size
        data = ImageData(w, h,
                         'rgba', self._pygame_surface.get_buffer().raw)

        del self._pygame_surface

        return data
