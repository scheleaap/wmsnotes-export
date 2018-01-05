# coding: utf-8

import logging

class Nf3Note(object):
	def __init__(self, title, path, description, rtf):
		self.title = title
		self.path = path
		self.description = description
		self.rtf = rtf

class Nf3Reader(object):
	def read(self, file):
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
				notes.append(self._read_note(file))
		logging.info('{0} notes read.'.format(len(notes)))
		
		return notes

	def _read_note(self, file):
		title = file.readline().strip().decode('latin1')
		path = file.readline().strip().decode('latin1')
		search_terms = file.readline().strip().decode('latin1')
		r1 = file.readline().strip().decode('latin1')
		r2 = file.readline().strip().decode('latin1')
		description = file.readline().strip().decode('latin1')
		description = description.replace('$@$', '\n')
		if description == 'Hier kunt u de beschrijving van de note invoeren.':
			description = ''
		body = file.readline().strip().decode('latin1')
		body = body.replace('$@$', '\n')
		
		return Nf3Note(title, path, description, body)
