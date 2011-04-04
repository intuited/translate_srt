#!/usr/bin/env python
"""Translate a .srt file using the Google Translate API."""
import sys
import re
import functools
import pprint
import argparse

import pytranslate

from functools import partial

def indent(text):
    return '\n'.join('    ' + line for line in text.split('\n'))

def dump(title, data, out=sys.stderr):
    text = data if type(data) == str else pprint.pformat(data)
    out.write(title + ':\n')
    out.write(indent(text) + '\n')

dump_original = functools.partial(dump, 'Original')

def no_op(*args, **kwargs):
    pass

# Comment out to enable debugging
dump_original = no_op

def convert_enc(text, encoding='latin1'):
    return text.decode(encoding).encode('utf-8')

def make_caption_regexp():
    """Return the regular expression used to match captions.

    Captions seem to be in this format::

        Lines  Content          Format          Example
        1      Caption ID       ^[0-9]+$        1
        2      Timecode         ^[0-9:, ->]+$   00:00:27,920 --> 00:00:29,810
        3      Content          .*              They killed Fritz!
        4...   Content (cont.)                  Those dirty stinking yellow
    """
    parts = {}
    parts['id'] = r'(?P<id>\d+)'
    timepart = r'\d+:\d{2}:\d{2},\d{3}'
    parts['timecode'] = r'(?P<timecode>{0} --> {0})'.format(timepart)
    until_double_newline = r'(?:(?!\n\n).)*'
    parts['content'] = r'(?P<content>{0})'.format(until_double_newline)

    template = r'{id}\n{timecode}\n{content}'
    return re.compile(template.format(**parts), re.DOTALL)

def translate_caption(caption,
                      translate=partial(pytranslate.translate, tl='english'),
                      regexp=make_caption_regexp()):
    """Hook up with google to translate a single caption."""
    dump_original(caption)

    match = regexp.match(caption)
    if match is None:
        dump('Failed match', caption)
        return None

    parts = match.groupdict()

    content = ' '.join(line.strip() for line in parts['content'].split('\n'))
    parts['content'] = translate(content)

    template = '{id}\n{timecode}\n{content}'
    return template.format(**parts)

def translate_file(file_, encoding='latin1', out=sys.stdout,
                   translate_caption=translate_caption):
    text = file_.read()
    text = convert_enc(text, encoding)

    # Captions are delimited by two or more newlines.
    captions = re.split(r'\n{2,}', text)

    translations = (translate_caption(caption) for caption in captions)

    # Drop malformed captions.
    translations = (t for t in translations if t is not None)

    for translation in translations:
        out.write(translation + '\n\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--to', help='Target language',
                        default='english')
    parser.add_argument('-f', '--from', help='Source language',
                        dest='from_',
                        default='auto')
    parser.add_argument('file', help='Name of file to translate',
                        type=argparse.FileType('U'))
    options = parser.parse_args()

    translate = partial(pytranslate.translate,
                        sl=options.from_, tl=options.to)
    translate_caption = partial(translate_caption,
                                translate=translate)

    translate_file(options.file,
                   translate_caption=translate_caption)
