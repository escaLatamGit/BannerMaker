from PIL import Image, ImageFont, ImageDraw
from os import path


def load_image(ipath):
    return Image.open(ipath)


def add_text(image, text, location, font, fontsize=14, fontcolor=(0, 0, 0)):
    font_format = ImageFont.truetype(font, fontsize)
    drawer = ImageDraw.Draw(image)
    drawer.text(location, text, fontcolor, font=font_format)
    return image


if __name__ == '__main__':
    image_path = path.abspath('../public/test_image.jpeg')
    font_path = path.abspath('./asset/font/sweet purple.ttf')
    font_size = 500

    temp = load_image(image_path)
    add_text(temp, 'hola mundo', (10, 10), font_path, font_size)
    name, ext = path.splitext(image_path)
    temp.save(f'{name}_out{ext}')
