# encoding=utf-8

import os
import re
import sys
sys.path.insert(0, '/home/sebastiaan/git/academicmarkdown')
sys.path.insert(0, '/home/sebastiaan/git/cachedurlget')
import cachedurlget
import yaml
from yamldoc._yaml import orderedLoad
from pelican import signals
from pelican.readers import MarkdownReader
from markdown import Markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.tables import TableExtension
from academicmarkdown import build, HTMLFilter, _FigureParser
if 'publishconf.py' in sys.argv:
	from publishconf import *
else:
	from pelicanconf import *
	
_FigureParser.figureTemplate[u'jekyll'] = u"""
![%%(source)s](/%s%%(source)s)

__Figure %%(nFig)d.__ %%(caption)s\n{: .fig-caption #%%(id)s}\n
""" % BRANCH

ITEM_TYPES = [
	'SKETCHPAD', 'FEEDBACK', 'SEQUENCE', 'LOOP', 'SAMPLER', 'SYNTH', 'LOGGER',
	'INLINE_SCRIPT', 'RESET_FEEDBACK', 'COROUTINES', 'KEYBOARD_RESPONSE',
	'MOUSE_RESPONSE', 'JOYSTICK', 'SRBOX', 'TEXT_DISPLAY', 'FORM_BASE',
	'FORM_TEXT_INPUT', 'FORM_TEXT_DISPLAY', 'FORM_MULTIPLE_CHOICE',
	'FORM_CONSENT', 'FORM', 'MEDIA_PLAYER_VLC', 'MEDIA_PLAYER_GST',
	'MEDIA_PLAYER_MPY', 'MOUSETRAP', 'SOUND_START_RECORDING',
	'SOUND_STOP_RECORDING', 'TOUCH_RESPONSE', 'PYGAZE_INIT', 'PYGAZE_LOG',
	'PYGAZE_WAIT', 'PYGAZE_DRIFT_CORRECT', 'PYGAZE_STOP_RECORDING',
	'PYGAZE_START_RECORDING', 'THIS_STYLE'
	]

root = os.path.dirname(os.path.dirname(__file__)) + '/content'

with open('constants.yaml') as f:
	const = yaml.load(f)

links = {}
duplicate_names = []

class AcademicMarkdownReader(MarkdownReader):

	enabled = True

	def read(self, source_path):

		"""Parse content and metadata of markdown files"""

		self._source_path = source_path
		self._md = Markdown(
			extensions=[
				'markdown.extensions.toc',
				'markdown.extensions.tables',
				'markdown.extensions.meta',
				'markdown.extensions.headerid',
				'markdown.extensions.extra',
				'markdown.extensions.codehilite(css_class=highlight)',
				],
			)		
		# self._md = Markdown(
		# 	extensions=self.extensions + [TocExtension(title='Overview'),
		# 		TableExtension()],
		# 	extpeension_configs=self.extensions)
		img_path = os.path.dirname(source_path) + '/img/' \
			+ os.path.basename(source_path)[:-3]
		lst_path = os.path.dirname(source_path) + '/lst/' \
			+ os.path.basename(source_path)[:-3]
		tbl_path = os.path.dirname(source_path) + '/tbl/' \
			+ os.path.basename(source_path)[:-3]
		build.path = [img_path, lst_path, tbl_path] + build.path
		with open(source_path) as fd:
			text = fd.read().decode('utf-8')
			text = build.MD(text)
			# Process internal links
			for m in re.finditer('%link:(?P<link>[\w/-]+)%', text):
				full = m.group(0)
				link = m.group('link')
				print('link', link, full)
				if link not in links:
					raise Exception(u'%s not a key in %s' % (link, links))
				text = text.replace(full, '<%s/%s>' % (SITEURL, links[link]))
			for m in re.finditer('%url:(?P<link>[\w/-]+)%', text):
				full = m.group(0)
				link = m.group('link')
				print('url', link, full)
				if link not in links:
					raise Exception(u'%s not a key in %s' % (link, links))
				text = text.replace(full, '%s/%s' % (SITEURL, links[link]))
			for m in re.finditer('%static:(?P<link>[\w/.-]+)%', text):
				full = m.group(0)
				link = m.group('link')
				print('static', link, full)
				text = text.replace(full, '<%s/%s>' % (SITEURL, link))
			text = text.replace(root, u'')
			text = HTMLFilter.DOI(text)
			content = self._md.convert(text)
			for var, val in const.items():
				content = content.replace(u'$%s$' % var, str(val))
			for item_type in ITEM_TYPES:
				content = content.replace(item_type,
					u'<span class="item-type">%s</span>' % item_type.lower())			
		metadata = self._parse_metadata(self._md.Meta)
		build.path = build.path[3:]
		return content, metadata


def init_academicmarkdown(sender):

	build.postMarkdownFilters = []
	build.figureTemplate = 'jekyll'
	build.tableTemplate = 'kramdown'
	build.figureSourcePrefix = SITEURL
	build.path += u'include'
	build.extensions.remove('toc')
	build.extensions.insert(0, 'toc')
	with open('sitemap.yaml') as f:
		d = orderedLoad(f)
	process_links(d)


def isseparator(pagename):

	for ch in pagename:
		if ch != '_':
			return False
	return True


def process_links(d):

	for pagename, entry in d.items():
		if isinstance(entry, list):
			entry = entry[0]
		if isseparator(pagename) or entry in [None, '']:
			continue
		if isinstance(entry, dict):
			process_links(entry)
			continue
		name = entry.split('/')[-1]
		if not name.strip():
			continue
		links[entry] = entry
		if entry == name or name in duplicate_names:
			continue
		if name not in links:
			links[name] = entry
			continue
		duplicate_names.append(name)
		del links[name]
		print('Duplicate name: %s' % name)


def add_reader(readers):

	readers.reader_classes['md'] = AcademicMarkdownReader


def register():

	signals.readers_init.connect(add_reader)
	signals.initialized.connect(init_academicmarkdown)
