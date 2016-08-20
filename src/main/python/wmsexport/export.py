# coding: utf-8

from collections import namedtuple
from ftplib import FTP
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import logging
import os
import rtf2xml.ParseRtf
import string
import sys
import wmsnotesreader

#FILE_WMSNOTES = 'test\\Test.nf3'
#FILE_WMSNOTES = 'test\\Notes.nf3'
FILE_WMSNOTES = 'D:\\Programma\'s\\VB6 free\\WMSNotes\\Notes.nf3'
EXPORT_NOTE_PATH_PREFIXES = (
	'Koken\\',
#	'Ideeën\\',
	)
UPLOAD = ('maaskant.info', 'wmsnotes', 'wmsnotes')

class Note(object):
	def __init__(self, title, path, description, rtf, rtf_xml = None, xml = None):
		self.title = title
		self.path = path
		self.description = description
		self.rtf = rtf
		self.rtf_xml = rtf_xml
		self.xml = xml

def main(args):
	try:
		logging.basicConfig(
			level = logging.DEBUG,
			format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s() %(message)s',
			)
	except EnvironmentError as e:
		print >> sys.stderr, e
		print >> sys.stderr, 'Unable to initialize logging.'
		sys.exit()
	
	try:
		process()
	except EnvironmentError as e:
		logging.exception(e)
		#raise
	except Exception as e:
		logging.exception(e)
		#raise

def process():
	# Lees alle notes in uit het WMS Notes-bestand.
	with open(FILE_WMSNOTES, 'rb') as f:
		notes = wmsnotesreader.read(f)
	
	# Filter the notes.
	notes_filtered = []
	for note in notes:
		if note.path.startswith(EXPORT_NOTE_PATH_PREFIXES):
			notes_filtered.append(note)
	notes = notes_filtered
	del notes_filtered
	logging.info('{0} notes after filtering.'.format(len(notes)))
	
	# Sort the notes.
	notes.sort(key = lambda note: (note.path, note.title))
	
	for note in notes:
		# Converteer de RTF naar een RTF-XML-boom.
		convert_note_to_rtf_xml(note)
		if len(os.listdir('D:\\Programma\'s\\Python\\wmsexport\\tmp')) > 2:
			raise NotImplementedError('Additional media detected in the RTF->XML output dir, which is not supported. Note {0}'.format(note.title))
			exit()
#		print ElementTree.tostring(note.rtf_xml)
#		sys.exit()

		# Converteer de RTF-XML naar mijn eigen XML.
		convert_note_to_xml(note)
#		print ElementTree.tostring(note.xml)
#		sys.exit()
	
	# Maak een grote XML-boom met alle notes.
	# TODO: Folderstructuur
	xml_tree = Element('notes')
	for note in notes:
		xml_tree.append(note.xml)
	indent(xml_tree)
	
	# Schrijf de XML-structuur weg als bestand.
	with open('rc\\notes.xml', 'wb') as f:
		f.write('<?xml version="1.0" encoding="iso-8859-1" ?>\n')
		f.write('<?xml-stylesheet type="text/xsl" href="transform.xsl" ?>')
		f.write(ElementTree.tostring(xml_tree))
	
	# Upload het bestand naar maaskant.info.
	try:
		ftp = FTP(UPLOAD[0])
		ftp.login(UPLOAD[1], UPLOAD[2])
		
		with open('rc\\notes.xml', 'rb') as f:
			ftp.storbinary('STOR index.xml', f)
		with open('rc\\transform.xsl', 'rb') as f:
			ftp.storbinary('STOR transform.xsl', f)
		with open('rc\\style.css', 'rb') as f:
			ftp.storbinary('STOR style.css', f)
	finally:
		ftp.close()

def convert_note_to_rtf_xml(note):
	# Write the note to a temporary RTF file.
	with open('tmp\\in.rtf', 'wb') as f:
		f.write(note.rtf)
	
	# Converteer de RTF naar een XML-string.
	parse_obj = rtf2xml.ParseRtf.ParseRtf(
		in_file = 'tmp\\in.rtf',
		out_file = 'tmp\\out.xml', # determine the output file
		run_level = 1, # determine the run level. The default is 1.
		indent = 1, # Indent resulting XML. Default is 0 (no indent).
		headings_to_sections = 1, # Convert headings to sections. Default is 0.
		group_styles = 0, # Group paragraphs with the same style name. Default is 1.
		empty_paragraphs = 1, # Write or do not write paragraphs. Default is 0.
		)
	parse_obj.parse_rtf()
	with open('tmp\\out.xml', 'rb') as f:
		rtf_xmlstring = f.read()
#	print rtf_xmlstring
#	sys.exit()
	
	# Converteer de RTF naar een RTF-XML-boom.
	rtf_xml = ElementTree.fromstring(rtf_xmlstring)
	
	note.rtf_xml = rtf_xml

def convert_note_to_xml(note):
	rtf_xml = note.rtf_xml
	
	own_xml = Element('note')
	own_xml.set('title', note.title)
	
	path_el = SubElement(own_xml, 'path')
	path_el.text = note.path
	
	description_el = SubElement(own_xml, 'description')
	description_el.text = note.description
	
	own_body_el = SubElement(own_xml, 'body')
	
	rtf_body_el = rtf_xml.find('{http://rtf2xml.sourceforge.net/}body')
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
					active_list = SubElement(own_body_el, 'ul')
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
				parent_el = SubElement(own_body_el, 'p')
				parent_el.text = para_el.text
				parent_el.tail = para_el.tail
			
			# Used to append text to.
			last_el = parent_el
			
			for inline_el in para_el:
				if inline_el.tag not in ['{http://rtf2xml.sourceforge.net/}inline', '{http://rtf2xml.sourceforge.net/}list-text']:
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
	
	note.xml = own_xml

def indent(elem, level = 0):
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
