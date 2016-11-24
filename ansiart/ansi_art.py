import sys
from PIL import Image

USAGE_DOC = """
***ANSI ART***
Usage:
    ansi_art <path-to-image> [block-size] [palette (%s)] [inverse (True|False)]
Example:
    ansi_art /tmp/image.png 10 Default True
Only .png, .jpg and .jpeg is allowed
"""
BLOCK_SIZE = 30
DEFAULT = ['  ', '. ', '..', '.-', '--', '-+', '++', '**', 'HH', 'H#', '##']
SIMPLE = ['  ', '. ', '..', '--', '-+', '++']
DUAL = ['  ', '##']
ROSA = ["  ", "' ", "''", "..", "::", "**", "@@"]
PALETTE_MAP = {'Default': DEFAULT, 'Dual': DUAL, 'Rosa': ROSA}


def get_art(path, b_size=BLOCK_SIZE, inverse=True, palette=DEFAULT):
    im = Image.open(path)
    if not inverse:
        palette = list(reversed(palette))
        palette.append(palette[-1])
    shadow_step = 255 * 3 / (len(palette) - 1)
    im = im.resize((im.width / b_size, im.height / b_size))
    text = ""
    for i in range(im.height):
        for j in range(im.width):
            p = im.getpixel((j, i))
            text += palette[sum(p) / shadow_step]
        text += "\n"
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE_DOC % '|'.join(PALETTE_MAP.keys())
        exit()
    path = sys.argv[1] if len(sys.argv) > 1 else 'mix.jpg'
    block_size = int(sys.argv[2]) if len(sys.argv) > 2 else BLOCK_SIZE
    print get_art(path, b_size=block_size, inverse=True, palette=DEFAULT)
