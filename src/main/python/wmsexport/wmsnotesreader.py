# coding: utf-8

from export import Note
import logging

def read(file):
	'''
	Reads a WMS Notes file.
	
	file: A file object to read from.
	'''
	notes = []
	
	line = '---'
	while True:
		line = file.readline()
		if line == '':
			break
		line = line.strip()
		
		# Notitie inlezen.
		if line == '<NOTE>':
			notes.append(_read_note(file))
	logging.info('{0} notes read.'.format(len(notes)))
	
	return notes

def _read_note(file):
	title = file.readline().strip().decode('latin1')
	path = file.readline().strip().decode('latin1')
	search_terms = file.readline().strip().decode('latin1')
	r1 = file.readline().strip().decode('latin1')
	r2 = file.readline().strip().decode('latin1')
	description = file.readline().strip().decode('latin1')
	description = description.replace('$@$', '\n')
	body = file.readline().strip().decode('latin1')
	body = body.replace('$@$', '\n')
	
	return Note(title, path, description, body)
