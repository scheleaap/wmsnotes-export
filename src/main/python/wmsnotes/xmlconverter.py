# coding: utf-8
"""Converts a Nf3Note into an XML structure."""

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from wmsnotes import rtf2xmlconverter


class Nf3NoteToXmlConverter(object):
    def convert(self, note):
        wmsnotes_xml = Element('note')
        wmsnotes_xml.set('title', note.title)

        path_el = SubElement(wmsnotes_xml, 'path')
        path_el.text = note.path

        description_el = SubElement(wmsnotes_xml, 'description')
        description_el.text = note.description

        wmsnotes_body_el = SubElement(wmsnotes_xml, 'body')
        rtf2xml_xml_string = rtf2xmlconverter.Rtf2XmlConverter().convert(note.rtf)
        rtf2xml_xml = ElementTree.fromstring(rtf2xml_xml_string)
        self._convert_rtf2xml_xml_to_wmsnotes_xml(rtf2xml_xml, wmsnotes_body_el)

        return wmsnotes_xml

    def _convert_rtf2xml_xml_to_wmsnotes_xml(self, rtf2xml_xml, wmsnotes_xml_root):
        rtf_body_el = rtf2xml_xml.find('{http://rtf2xml.sourceforge.net/}body')
        if rtf_body_el is None: raise Exception('<body> not found')
        if len(rtf_body_el) > 1: raise NotImplementedError('More than 1 sub element of <body> not supported')
        section_el = rtf_body_el.find('{http://rtf2xml.sourceforge.net/}section')
        if section_el is None: raise Exception('<section> not found')

        active_list = None
        for paragraph_definition_el in section_el:
            if paragraph_definition_el.tag != '{http://rtf2xml.sourceforge.net/}paragraph-definition':
                raise NotImplementedError('Unknown tag {0}'.format(paragraph_definition_el.tag))

            for para_el in paragraph_definition_el:
                if para_el.tag != '{http://rtf2xml.sourceforge.net/}para':
                    raise NotImplementedError('Unknown tag {0}'.format(para_el.tag))

                # Make an element to contain this line.
                # This will be a <p>, unless this line is a bulleted item, in which case it will be a <li>.
                if len(para_el) > 0 and para_el[0].tag == '{http://rtf2xml.sourceforge.net/}list-text':
                    if active_list is None:
                        # Create a list element.
                        active_list = SubElement(wmsnotes_xml_root, 'ul')
                    parent_el = SubElement(active_list, 'li')
                    parent_el.text = para_el.text
                    parent_el.tail = para_el.tail

                    # Remove the <list-text> element (which contains the bullet).
                    parent_el.text = '{1}{2}{0}'.format(
                        para_el[0].text if para_el[0].text is not None else '',
                        para_el[0].tail if para_el[0].tail is not None else '',
                        parent_el.text if parent_el.text is not None else ''
                    )
                    para_el.remove(para_el[0])
                else:
                    active_list = None
                    parent_el = SubElement(wmsnotes_xml_root, 'p')
                    parent_el.text = para_el.text
                    parent_el.tail = para_el.tail

                # Used to append text to.
                last_el = parent_el

                for inline_el in para_el:
                    if inline_el.tag not in ['{http://rtf2xml.sourceforge.net/}inline',
                                             '{http://rtf2xml.sourceforge.net/}list-text']:
                        raise NotImplementedError('Unknown tag {0}'.format(inline_el.tag))

                    style = []

                    font_size = inline_el.get('font-size')
                    if font_size is not None and float(font_size) != 8.5:
                        style.append('font-size: {0}pt;'.format(font_size))

                    font_style = inline_el.get('font-style')
                    if font_style is not None and font_style != 'Arial':
                        style.append('font-family: {0};'.format(font_style))

                    bold = inline_el.get('bold')
                    if bold == 'true':
                        style.append('font-weight: bold;')

                    italic = inline_el.get('italics')
                    if italic == 'true':
                        style.append('font-style: italic;')

                    if (inline_el.text != '' or inline_el.tail is not None) and len(style) > 0:
                        # Make a new <span> element.
                        span_el = SubElement(parent_el, 'span')
                        span_el.text = inline_el.text
                        span_el.tail = inline_el.tail
                        span_el.set('style', ' '.join(style))

                        # Used to append text to.
                        last_el = span_el
                    else:
                        # Append to the last element.
                        if last_el == parent_el:
                            # Append to last element's text
                            last_el.text = '{0}{1}{2}'.format(
                                last_el.text if last_el.text is not None else '',
                                inline_el.text,
                                inline_el.tail if inline_el.tail is not None else ''
                            )
                        else:
                            # Append to last element's tail
                            last_el.tail = '{0}{1}{2}'.format(
                                last_el.tail if last_el.tail is not None else '',
                                inline_el.text,
                                inline_el.tail if inline_el.tail is not None else ''
                            )
