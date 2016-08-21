# coding: utf-8

import argparse
from collections import namedtuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import logging
import os
import rtf2xml.ParseRtf
import string
import sys
from wmsnotes import nf3reader, xmlconverter

EXPORT_NOTE_PATH_PREFIXES = (
    'Koken\\',
    #	'Ideeën\\',
)


def main(args):
    # Parse command-line options.
    args = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    args.add_argument('source', help='The WMSNotes 3 .nf3 file to process.')
    args.add_argument('target', help='The target directory.')
    args = args.parse_args()

    # Initialize logging.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s [%(module)s.%(funcName)s()]',
    )

    try:
        process(args.source, args.target)
    except EnvironmentError as e:
        logging.exception(e)
    except Exception as e:
        logging.exception(e)


def process(source, target):
    # Lees alle notes in uit het WMS Notes-bestand.
    with open(source, 'rb') as f:
        notes = nf3reader.Nf3Reader().read(f)

    # Filter the notes.
    notes_filtered = []
    for note in notes:
        if note.path.startswith(EXPORT_NOTE_PATH_PREFIXES):
            notes_filtered.append(note)
    notes = notes_filtered
    del notes_filtered
    logging.info('{0} notes after filtering.'.format(len(notes)))

    # Sort the notes.
    notes.sort(key=lambda note: (note.path, note.title))

    # Maak een grote XML-boom met alle notes.
    # TODO: Folderstructuur
    xml_tree = Element('notes')

    converter = xmlconverter.Nf3NoteToXmlConverter()
    for note in notes:
        # Converteer de Nf3Note naar een WMSNotes-XML-boom.
        xml_note = converter.convert(note)
        #		print ElementTree.tostring(xml_note)
        #		sys.exit()

        xml_tree.append(xml_note)

        # print ElementTree.tostring(xml_tree)
    indent(xml_tree)

    # Schrijf de XML-structuur weg.
    #	with open(os.path.join(target, 'notes.xml'), 'wb') as f:
    f = sys.stdout
    f.write('<?xml version="1.0" encoding="iso-8859-1" ?>\n')
    f.write('<?xml-stylesheet type="text/xsl" href="transform.xsl" ?>')
    f.write(ElementTree.tostring(xml_tree))


def indent(elem, level=0):
    '''
    In-place prettyprint formatter.

    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    '''
    i = '\n' + level * '\t'
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '\t'
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# Initialization code.

if __name__ == '__main__':
    main(sys.argv[1:])
