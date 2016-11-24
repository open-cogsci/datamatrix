# -*- coding: utf-8 -*-

"""
This file is part of datamatrix.

datamatrix is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

datamatrix is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with datamatrix.  If not, see <http://www.gnu.org/licenses/>.
"""

def run_all_tests(tests=None, N=1000):
	
	def dummy(*args, **kwargs): pass
	
	if tests is None:
		tests = ['basics', 'desc_stats', 'extra_operations', 'io', 'iteration',
			'operations', 'order', 'select_merge', 'series_operations']
			
	from testcases import test_tools
	test_tools.check_col = dummy
	test_tools.check_series = dummy
	test_tools.check_integrity = dummy
			
	for test in tests:		
		mod = __import__('testcases.test_%s' % test)
		mod = getattr(mod, 'test_%s' % test)
		for name, obj in mod.__dict__.items():
			if name.startswith('test_') and callable(obj):
				print(name)
				for i in range(N):
					obj()
