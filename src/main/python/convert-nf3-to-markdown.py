# coding: utf-8

import argparse
import logging

import sys

from wmsnotes import nf3reader
from wmsnotes import mdconverter

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

    converter = mdconverter.Nf3NoteToMarkdownConverter()
    for note in notes:
        markdown_note = converter.convert(note)
        print markdown_note


# Initialization.

if __name__ == '__main__':
    main(sys.argv[1:])
