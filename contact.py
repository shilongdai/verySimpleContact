import sys
import traceback

from peopleBook import PeopleBook
from peopleBook import Person


def print_help():
	"""
	prints the help message for this application
	:return: None
	"""

	print("python contact.py add|update|get|find|remove operations")
	print(
		'add operations: [firstname=first name | middlename=middle name | lastname=last name | addresses=address1,address2,...,addressn | phone_numbers=phone1,phone2,...,phonen | emails=email1,email2,...,emailn | note=note]')
	print(
		'update operations: entry_number [firstname="first name" | middlename="middle name" | lastname="last name" | addresses="address1","address2",...,"addressn" | phone_numbers="phone1","phone2",...,"phonen" | emails="email1","email2",...,"emailn" | note="note"]')
	print("get operations: entry_number1 entry_number2 ...")
	print('find operations: keyword name "part of name" "part of name 2" ...')
	print("remove operation: entry_number1 entry_number2 ...")


def get_equivalence_expressions(strings):
	"""
	get a list of strings in the format of name=some expression from a list of strings. It is expected that a whole string is split by space to form the input string list
	:param strings: the input string list. It is assumed to be once a whole string with space delimiter
	:return: a list of strings in the format name=some expression
	"""

	result = []
	equal_indexes = []

	# identify the index of all segments with equal sign
	for counter, value in enumerate(strings):
		if '=' in value:
			equal_indexes.append(counter)

	if len(equal_indexes) == 0:
		return result

	# regroup the original lists into segments seperated by the equal sign indexes
	equal_indexes.append(len(strings))
	last_index = 0
	for i in equal_indexes:
		result.append(" ".join(strings[last_index:i]))
		last_index = i
	result.pop(0)
	return result


def equiv2handler_mapper(person):
	"""
	creates the handler table for handling add and update operations
	:param person: the person record that is being operated on
	:return: the handler table
	"""

	def set_first(name):
		person.firstName = name

	def set_middle(name):
		person.middleName = name

	def set_last(name):
		person.lastName = name

	def set_addresses(addresses):
		person.addresses = [i.strip() for i in addresses.split(',')]

	def set_phones(phone_numbers):
		person.phoneNumbers = [i.strip() for i in phone_numbers.split(',')]

	def set_emails(emails):
		person.emailAddresses = [i.strip() for i in emails.split(',')]

	def set_note(note):
		person.note = note

	value_mapper = {"firstname": set_first,
	                "middlename": set_middle,
	                "lastname": set_last,
	                "addresses": set_addresses,
	                "phone_numbers": set_phones,
	                "emails": set_emails,
	                "note": set_note}
	return value_mapper


def handle_equivalence_expression(expression, person = Person()):
	"""
	translate the name=expression format into a person record. It make use of the getEquivalenceExpressions function and the operation table generated by the equiv2HandlerMapper.
	:param expression: the expression to evaluate
	:param person: the record to update information in
	:return: the record
	"""

	equivalence_expressions = get_equivalence_expressions(expression)
	value_mapper = equiv2handler_mapper(person)

	for exp in equivalence_expressions:
		parts = exp.split('=')
		handler = value_mapper.get(parts[0], None)
		if handler is None:
			print("%s is not a valid field" % parts[0])
			return None
		handler(parts[1])
	return person


def handle_get(contact, entryNumbers):
	"""
	handles the get operation.
	:param contact: the contact book to get from
	:param entryNumbers: a list of entry numbers to look up
	:return: None
	"""

	for entryNumber in entryNumbers:
		person = contact.get(entryNumber)
		if person is None:
			print("The address with entry number: %s does not exists" % entryNumber)
			continue
		print("-" * 80)
		print(person)


def handle_find(contact, keywords):
	"""
	handles the find operation
	:param contact: the contact book to search
	:param keywords: the name keywords tokenized by space to search
	:return: None
	"""

	keyword = " ".join(keywords)
	for i in contact.find(keyword):
		print("-" * 80)
		print(i)


def handle_add(contact, addStrings):
	"""
	handles the add operation
	:param contact: the contact book to add records to
	:param addStrings: the add expression string tokenized by space
	:return: None
	"""

	person = handle_equivalence_expression(addStrings)
	if person is None:
		return
	contact.save(person)
	print("Entry %s saved" % person.entryNumber)


def handle_update(contact, updateStrings):
	"""
	handles the update operation
	:param contact: the contact book to update records in
	:param updateStrings: the update operation expression tokenized by space in the format of entry_number name=value name2=value2 etc...
	:return: None
	"""

	if len(updateStrings) < 1:
		print_help()
		return
	entry_number = updateStrings[0]
	expression_strs = updateStrings[1:]
	person = contact.get(entry_number)
	if person is None:
		print("Entry %s does not exists" % entry_number)

	person = handle_equivalence_expression(expression_strs, person)
	person.setEntryNumber(int(entry_number))
	contact.save(person)
	print("Entry %s updated" % person.entryNumber)


def handle_remove(contact, entries):
	"""
	handles the remove operation
	:param contact: the contact book to remove from
	:param entries: the entry numbers to remove
	:return: None
	"""

	for i in entries:
		contact.delete(i)
		print("Entry %s removed" % i)


def construct_handler_chain():
	"""
	constructs the handler chain which maps user inputs to handler functions
	:return: the handler chain
	"""

	handlers = dict()
	handlers["add"] = handle_add
	handlers["update"] = handle_update
	handlers["get"] = handle_get
	handlers["find"] = dict()
	handlers["find"]["keyword"] = dict()
	handlers["find"]["keyword"]["name"] = handle_find
	handlers["remove"] = handle_remove
	return handlers


def main(argv):
	"""
	the main starting function
	:param argv: the command line arguments
	:return: None
	"""
	contact_book = PeopleBook()
	try:
		contact_book.open()
		handlers = construct_handler_chain()
		current_handler = handlers
		# trace to the handler function based on user input
		while len(argv) != 0:
			to_process = argv[:1]
			argv = argv[1:]

			current_handler = current_handler.get(to_process[0], None)
			if current_handler is None:
				print("Unsupported Operation: %s" % to_process[0])
				return
			if type(current_handler) == dict:
				continue
			# handles the user input with the handler mapped
			current_handler(contact_book, argv)
			return
		print_help()
	except:
		print("Error Occurred")
		traceback.print_exc()
	finally:
		contact_book.close()


if __name__ == "__main__":
	arguments = sys.argv
	# remove the python file argument if launched with python
	if len(sys.argv) != 0 and sys.argv[0].endswith(".py"):
		arguments = sys.argv[1:]
	if len(arguments) == 0:
		print_help()
	else:
		main(arguments)
