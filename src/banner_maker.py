#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""

    Banner Maker is a minimal script to automate text drawing on Image

    Usage:
            banner_maker.py  [--config=<config>] [--output=<output_path>]
            banner_maker.py -h | --help
    Options:
            -h --help               Show this screen.
            --version               Show version.
            --config=<config>       Config file path [default: ../config/config.xlsx].
            --output=<output_path>  Output path of new images [default: ../public/].
            --logs=<logs>           Output file for logs [default: ./process.logs.txt].
"""
import logging
import math
import re
from os import path

import docopt
import pandas as pd
from PIL import Image, ImageFont, ImageDraw
from webcolors import hex_to_rgb

version = 2.0


def load_image(ipath):
    return Image.open(ipath)


def resolve_centered_tex_position(text, font, box_size, offsets=(0, 0)):
    words = re.split('\n+', text)
    max_w, total_h = (0, 0)
    for word in words:
        (w, h), _ = font.font.getsize(word)
        if w > max_w:
            max_w = w
        total_h += h

    W, H = box_size
    ow, oy = offsets
    return round((W - max_w) / 2 + ow), round((H - total_h) / 2 + oy)


def add_text(image, text, location, font, fontsize=14, fontcolor=(0, 0, 0), border=0, border_color=(0, 0, 0),
             centering=(False, False),
             points=15):
    font_format = ImageFont.truetype(font, fontsize)
    drawer = ImageDraw.Draw(image)
    center_x, center_y = centering
    if center_x or center_y:
        new_location = resolve_centered_tex_position(text, font_format, image.size)
        if center_x and center_y:
            location = new_location
        elif center_y:
            location = (location[0], new_location[1])
        elif center_x:
            location = (new_location[0], location[1])
    if border:
        (x, y) = location
        for step in range(0, math.floor(border * points), 1):
            angle = step * 2 * math.pi / math.floor(border * points)
            drawer.text((x - border * math.cos(angle), y - border * math.sin(angle)), text, border_color,
                        font=font_format)
    drawer.text(location, text, fontcolor, font=font_format)
    return image


def check_file(name):
    ipath = path.abspath(name)
    if not path.exists(ipath):
        raise FileNotFoundError(f'File not found at {name}')
    return ipath


def load_config(config_file_path='../config/config.xlsx', sheet_name=0, index_col=None):
    raw_config = pd.read_excel(config_file_path, sheet_name=sheet_name, index_col=index_col)
    data, validator = dict(), dict()
    for index, row in raw_config.iterrows():
        try:
            if row.Group not in data:
                data[row.Group] = dict()
                data[row.Group]['value'] = []
                data[row.Group]['file'] = check_file(row.File)
            new_row = dict()
            new_row['fontsize'] = row.Fontsize
            new_row['text'] = str(row.Text)
            new_row['color'] = hex_to_rgb(row.Color)
            new_row['border'] = row.Border
            new_row['border_color'] = hex_to_rgb(row.Bordercolor) if row.Border else None
            new_row['location'] = (row.X, row.Y)
            new_row['font'] = check_file(row.Fonttype)
            print(row.Centering)
            new_row['centering'] = ('x' in row.Centering, 'y' in row.Centering) if row.Centering else (False, False)
            if row.Group not in validator:
                validator[row.Group] = row.File
            if not validator[row.Group] == row.File:
                raise ValueError(f'Invalid Config Group found,  all group\'s rows has to take the same File \
                expected:\'{validator[row.Group]}\',found:\'{row.File}\'')
            data[row.Group]['value'].append(new_row)
        except Exception as err:
            logging.error(err)
    return data


if __name__ == '__main__':
    args = docopt.docopt(__doc__, version=str(version))
    logging.basicConfig(filename=args['--logs'],
                        filemode='a',
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    try:
        config_path = args['--config']
        public_path = args['--output']
        logging.info(f'Loading Config from {config_path}')
        configs = load_config(config_path)
        logging.info('-----------------------')
        for config in configs.values():
            try:
                logging.info(f'Current File:"{config["file"]}"')
                image_container = load_image(config['file'])
                file_path = path.abspath(path.join(public_path, path.basename(config["file"])))
                for text_config in config['value']:
                    add_text(image_container, text_config['text'], text_config['location'], text_config['font'],
                             text_config['fontsize'], text_config['color'], text_config['border'],
                             text_config['border_color'],
                             text_config['centering'])
                image_container.save(file_path)
                logging.info(f'Output File:"{file_path}"')
                logging.info('-----------------------')
            except Exception as e:
                logging.error(e)
    except Exception as e:
        logging.error(e)

    logging.info('Process Execution End')
    logging.info('-----------------------')
