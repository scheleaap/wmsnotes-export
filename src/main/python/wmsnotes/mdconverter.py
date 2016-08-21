# coding: utf-8
"""Converts a Nf3Note into Markdown text."""

from __future__ import absolute_import, division, print_function

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

                if len(el) == 1 and el[0].text == '(De opsomming hoort genummerd te zijn.)':
                    number_next_list = True
                    skip_para = True

                elif len(el) == 1 \
                        and el[0].tag == '{http://rtf2xml.sourceforge.net/}inline' \
                        and el[0].get('bold') == 'true' \
                        and el.get('italic') is None:
                    result.write('## {title}\n\n'.format(title=el[0].text))
                    skip_para = True

                elif len(el) == 2 \
                        and el[0].text == 'Benodigdheden' \
                        and el[1].text == ' (of: "wat heb ik de laatste keer gebruikt?")':
                    result.write('## {title}\n\n'.format(title=''.join([el[0].text, el[1].text])))
                    skip_para = True

                elif len(el) > 0 and el[0].tag == '{http://rtf2xml.sourceforge.net/}list-text':
                    # This is a list item
                    if number_next_list:
                        result.write('1. ')
                    else:
                        result.write('* ')
                    is_list_active = True
                else:
                    # This is a normal paragraph
                    if is_list_active:
                        number_next_list = False
                    is_list_active = False

            elif (event, el.tag) == ('end', '{http://rtf2xml.sourceforge.net/}para'):
                if not skip_para:
                    result.write('\n')
                    if not is_list_active:
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
                    is_italic = el.get('italic') == 'true'
                    if is_italic:
                        result.write('*')
                    if is_bold:
                        result.write('**')

            elif (event, el.tag) == ('end', '{http://rtf2xml.sourceforge.net/}inline'):
                if skip_para or is_list_text_active:
                    pass
                else:
                    result.write(el.text)

                    is_bold = el.get('bold') == 'true'
                    is_italic = el.get('italic') == 'true'
                    if is_italic:
                        result.write('*')
                    if is_bold:
                        result.write('**')

                    result.write(el.tail)

        return result.getvalue()
