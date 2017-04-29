import sys

def query_multiple(queries):
	results = {}
	for name in queries:
		if queries['type'] == "float":
			results[name] = query_float(queries[name]['prompt'])
		elif queries['type'] == "bool":
			results[name] = query_float(queries[name]['prompt'])
		elif queries['type'] == "int":
			results[name] = query_int(queries[name]['prompt'])
		else:
			results[name] = query_string(question)

def query_string(question, default="", input_func = input):
	ans = input_func(question)
	if ans == "":
		return default

def query_yes_no(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".

	From: http://code.activestate.com/recipes/577058/
	"""
	valid = {"yes": True, "y": True, "ye": True,
			 "no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' "
							 "(or 'y' or 'n').\n")


def is_float(the_string):
	try:
		x = float(the_string)
		return True
	except ValueError:
		return False

def is_int(the_string):
	try:
		x = int(the_string)
		return True
	except ValueError:
		return False


def query_float(question, default=None):
	"""Ask a question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be any float or None

	The "answer" return value is a float value.
	"""

	while True:
		sys.stdout.write(question)
		choice = raw_input()
		if default is not None and choice == '':
			return default
		elif is_float(choice):
			return float(choice)
		else:
			sys.stdout.write("Please respond with a valid number.\n")

def query_int(question, default=None, min_num=None, max_num=None):
	"""Ask a question via raw_input() and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be any float or None

	The "answer" return value is a float value.
	"""
	valid = False
	while True:
		sys.stdout.write(question)
		choice = raw_input()
		if default is not None and choice == '':
			return default
		if is_int(choice):
			choice = int(choice)
			if min_num is None and max_num is None:
				return choice
			elif min_num is None and choice <= max_num:
				return choice
			elif  max_num is None and choice >= min_num:
				return choice
			elif min_num <= choice <= max_num:
				return choice
		sys.stdout.write("Please respond with a valid number.\n")


def query_min_max(question, min_num=0.0, max_num=1.0):
	"""Ask a question via raw_input() where "min", "max", "off" or a number in a range are valid and return their answer.

	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is True for "yes" or False for "no".

	From: http://code.activestate.com/recipes/577058/
	"""
	prompt = " [min/max/off/{}-{}] ".format(min_num, max_num)

	while True:
		sys.stdout.write(question + prompt)
		choice = raw_input().lower()
		if choice == 'min' or choice == 'max' or choice == 'off':
			return choice
		elif is_float(choice) and min_num <= float(choice) <= max_num:
			return float(choice)
		else:
			sys.stdout.write("Please respond with 'min', 'max', 'off' or a number between {} and {}. \n".format(min_num, max_num))
