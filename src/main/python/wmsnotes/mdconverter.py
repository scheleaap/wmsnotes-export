# coding: utf-8
"""Converts a Nf3Note into Markdown text."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from StringIO import StringIO
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from . import rtf2xmlconverter


class Nf3NoteToMarkdownConverter(object):
    def convert(self, note):
        md_buffer = StringIO()

        md_buffer.write('# {title}\n'.format(title=note.title))
        md_buffer.write('\n')
        if note.description != '':
            md_buffer.write('{description}\n'.format(description=note.description))
            md_buffer.write('\n')
        md_buffer.write('`{path}`\n'.format(path=note.path))
        md_buffer.write('\n')

        body_rtf2xml_xml_string = rtf2xmlconverter.Rtf2XmlConverter().convert(note.rtf)
        body_markdown = self._convert_rtf2xml_xml_to_markdown(body_rtf2xml_xml_string)

        md_buffer.write(body_markdown)

        return md_buffer.getvalue()

    def _convert_rtf2xml_xml_to_markdown(self, rtf2xml_xml_string):
        result = StringIO()

        skip_para = False
        is_list_active = False
        is_list_text_active = False
        number_next_list = False

        supported_event_types = ['start', 'end']
        for (event, el) in ElementTree.iterparse(source=StringIO(rtf2xml_xml_string), events=supported_event_types):
            if event not in supported_event_types:
                raise NotImplementedError('Unsupported event type {event}'.format(event=event))

            # logging.debug('<{tag}> {event}'.format(event=event, tag=el.tag))

            if (event, el.tag) == ('start', '{http://rtf2xml.sourceforge.net/}para'):
                skip_para = False

                # Write a newline after the previous paragraph, if necessary
                if not self._is_list_para(el):
                    if is_list_active:
                        logging.debug('Newline after list')
                        result.write('\n')
                        number_next_list = False
                        is_list_active = False

                if self._is_empty_para(el) is None:
                    # In the future, <para/> elements could be used to distinguish between line breaks and paragraph breaks.
                    logging.debug('Empty paragraph found')
                    skip_para = True

                elif len(el) == 1 and el[0].text == '(De opsomming hoort genummerd te zijn.)':
                    logging.debug('Numbered list indicator found')
                    number_next_list = True
                    skip_para = True

                elif len(el) == 1 \
                        and el[0].tag == '{http://rtf2xml.sourceforge.net/}inline' \
                        and el[0].get('bold') == 'true' \
                        and el.get('italic') is None:
                    logging.debug('Bold header found ("{text}")'.format(text=el.text))
                    result.write('## {title}\n\n'.format(title=el[0].text))
                    skip_para = True

                elif len(el) == 1 \
                        and el[0].tag == '{http://rtf2xml.sourceforge.net/}inline' \
                        and el[0].get('italics') == 'true' \
                        and el.get('bold') is None:
                    logging.debug('Italic header found ("{text}")'.format(text=el.text))
                    result.write('### {title}\n\n'.format(title=el[0].text))
                    skip_para = True

                elif len(el) == 2 \
                        and el[0].text == 'Benodigdheden' \
                        and el[1].text == ' (of: "wat heb ik de laatste keer gebruikt?")':
                    logging.debug('"Benodigdheden" header found ("{text}", "{tail})"'.format(text=el.text, tail=el.tail))
                    result.write('## {title}\n\n'.format(title=''.join([el[0].text, el[1].text])))
                    skip_para = True

                elif self._is_list_para(el):
                    # This is a list item
                    if number_next_list:
                        logging.debug('Starting numbered list item')
                        result.write('1. ')
                    else:
                        logging.debug('Starting bulleted list item')
                        result.write('* ')
                    is_list_active = True
                else:
                    # This is a normal paragraph
                    logging.debug('Starting normal paragraph'.format(text=el.text, tail=el.tail))
                    # if is_list_active:
                    #     logging.debug('Newline after paragraph')
                    #     result.write('\n')
                    #     number_next_list = False
                    #     is_list_active = False

                    if el.text is not None:
                        result.write(el.text)

            elif (event, el.tag) == ('end', '{http://rtf2xml.sourceforge.net/}para'):
                if not skip_para:
                    logging.debug('Ending current line')
                    result.write('\n')
                    if not is_list_active:
                        logging.debug('Newline after paragraph')
                        result.write('\n')

            elif (event, el.tag) == ('start', '{http://rtf2xml.sourceforge.net/}list-text'):
                if not skip_para:
                    is_list_text_active = True

            elif (event, el.tag) == ('end', '{http://rtf2xml.sourceforge.net/}list-text'):
                if not skip_para:
                    is_list_text_active = False

            elif (event, el.tag) == ('start', '{http://rtf2xml.sourceforge.net/}inline'):
                if skip_para or is_list_text_active:
                    pass
                else:
                    is_bold = el.get('bold') == 'true'
                    is_italic = el.get('italics') == 'true'
                    if is_italic:
                        result.write('*')
                    if is_bold:
                        result.write('**')

            elif (event, el.tag) == ('end', '{http://rtf2xml.sourceforge.net/}inline'):
                if skip_para or is_list_text_active:
                    pass
                else:
                    logging.debug('Inline ("{text}", "{tail}")'.format(text=el.text, tail=el.tail))
                    result.write(el.text)

                    is_bold = el.get('bold') == 'true'
                    is_italic = el.get('italics') == 'true'
                    if is_italic:
                        result.write('*')
                    if is_bold:
                        result.write('**')

                    result.write(el.tail)

        return result.getvalue()

    def _is_empty_para(self, el):
        return len(el) == 0 and el.text

    def _is_list_para(self, el):
        return len(el) > 0 and el[0].tag == '{http://rtf2xml.sourceforge.net/}list-text'
