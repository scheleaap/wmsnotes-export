# coding: utf-8
# TODO:
# - Courier New
# - Tabs / tables

import argparse
import io
import logging
import os
import sys

from wmsnotes import mdconverter
from wmsnotes import nf3reader

EXPORT_NOTE_PATH_PREFIXES = (
    '',
    # u'Koken\\',
    # u'Ideeën',
    # u'Algemeen',
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
        level=logging.INFO,
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
        if target == '-':
            sys.stdout.write(markdown_note)
            sys.stdout.write('====================\n')
        else:
            note_dir = os.path.join(target, *note.path.split('\\'))
            if not os.path.exists(note_dir):
                os.makedirs(note_dir)
            with(io.open(os.path.join(note_dir, note.title + '.md'), 'w', encoding='utf-8', newline='\n')) as f:
                f.write(markdown_note)


# Initialization.

if __name__ == '__main__':
    main(sys.argv[1:])
