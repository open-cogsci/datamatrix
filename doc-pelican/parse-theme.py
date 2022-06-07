#!/usr/bin/env python3
# coding=utf-8

import os
import yaml

with open('constants.yaml') as f:
	const = yaml.load(f, Loader=yaml.SafeLoader)


def parse_folder(dirname):

	for basename in os.listdir(dirname):
		path = os.path.join(dirname, basename)
		if os.path.isdir(path):
			parse_folder(path)
			continue
		if path.endswith('.js'):
			print('processing %s' % path)
			with open(path) as fd:
				content = fd.read()
			with open(path, 'w') as fd:
				for var, val in const.items():
					content = content.replace(u'$%s$' % var, str(val))
				fd.write(content)


parse_folder('output')
