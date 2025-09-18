import os
from PIL import Image

cache = {}

# Cache sprite from file.
# Get RGBA values for each frame from left to right, top to bottom.
# size: (width, height)


def import_sprite(path, frame_size, spacing=0, name=None):

    print(f'[Sprite Cache] Importing {path}')

    with Image.open(path) as img:
        frames = []
        for y in range(0, img.height, frame_size[1] + spacing):
            for x in range(0, img.width, frame_size[0] + spacing):
                has_values = False
                frame = []
                for y2 in range(frame_size[1]):
                    frame_row = []
                    for x2 in range(frame_size[0]):
                        px = img.getpixel((x + x2, y + y2))
                        frame_row.append(px)
                        if px[3] != 0:
                            has_values = True
                    frame.append(frame_row)
                if has_values:
                    frames.append(frame)

        if name is None:
            name = os.path.splitext(os.path.basename(path))[0]

        cache[name] = frames
