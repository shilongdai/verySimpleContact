"""
This module contains the classes used by the contact program and the unit tests for each individual classes.
"""

import os
import shelve
import unittest


class Person:
	"""
	This class represents the contact information of a person. It is a simple record that just holds data.
	This class does not support any operators beside the constructor
	"""

	def __init__(self, entryNumber = -1, firstName = "", middleName = "", lastName = "", addresses = (),
	             phoneNumbers = (),
	             emailAddresses = (), note = ""):
		"""
		creates a new Person.
		:param entryNumber: the id number in database
		:param firstName: the first name of the person
		:param middleName: the middle name of the person
		:param lastName: the last name of the person
		:param addresses: the addresses of the person
		:param phoneNumbers: the phone numbers of the person
		:param emailAddresses: the email addresses of the person
		:param note: the note about this person
		"""

		self.entryNumber = entryNumber
		self.firstName = firstName
		self.middleName = middleName
		self.lastName = lastName
		self.addresses = list(addresses)
		self.phoneNumbers = list(phoneNumbers)
		self.emailAddresses = list(emailAddresses)
		self.note = note

	def full_name(self):
		"""
		gets the full name of a person in the form of First Middle Last
		:return: the full name of the person
		"""

		result = self.firstName
		if len(self.middleName) != 0:
			result += " " + self.middleName
		if len(self.lastName) != 0:
			result += " " + self.lastName
		return result

	def from_full_name(self, name):
		"""
		sets the full name of the person. This method will priortize first name > last name > middle name.
		In another word, if only one part of the name is present, it assumes it is the first name of the person.
		:param name: the full name of the person
		:return: None
		"""

		name_parts = name.split(" ")

		# fill parts of name with empty strings if not exists
		while len(name_parts) < 3:
			name_parts.append("")

		self.firstName, self.middleName, self.lastName = tuple([n for n in name_parts])

		# if only two parts are specified, assume FirstName Lastname
		if len(name_parts) == 2:
			self.lastName, self.middleName = self.middleName, self.lastName

	def add_address(self, *address):
		self.addresses.extend(address)

	def add_phone(self, *phoneNumber):
		self.phoneNumbers.extend(phoneNumber)

	def add_email(self, *email):
		self.emailAddresses.extend(email)

	def __str__(self):
		"""
		returns an aligned, pretty print version of the data in this class for display purposes
		:return: an aligned, pretty print data string
		"""

		template = "{0:>15}: {1} \n"
		return template.format("Name", self.full_name()) + \
		       template.format("Addresses", ", ".join(self.addresses)) + \
		       template.format("Phone Numbers", ", ".join(self.phoneNumbers)) + \
		       template.format("Emails", ", ".join(self.emailAddresses)) + \
		       template.format("Note", self.note)

	def __eq__(self, other):
		if self.firstName != other.firstName:
			return False
		if self.middleName != other.middleName:
			return False
		if self.lastName != other.lastName:
			return False
		if self.phoneNumbers != other.phoneNumbers:
			return False
		if self.addresses != other.addresses:
			return False
		if self.emailAddresses != other.emailAddresses:
			return False
		if self.note != other.note:
			return False
		return True


class PeopleBook:
	"""
	This class manages all the People instances and provides CRUD operations.
	It is the data object that is responsible for persisting and tracking all the people by entry number.
	Before an instance of this class can be used, the open method must be called. When an instance is no longer used, the close method must be called.
	This class does not support any of the operators beside the constructor.
	"""

	def save(self, *people):
		"""
		persists person records. It will updates any records that have an entry number already existing in the contact
		:param people: the records to persist
		:return: None
		"""

		for i in people:
			if str(i.entryNumber) not in self._storage:
				i.entryNumber = self._currentID
			self._currentID += 1
			self._storage[str(i.entryNumber)] = i

	def count(self):
		"""
		counts the number of records in the contact
		:return: the number of records
		"""

		return len(self._storage.keys())

	def get(self, entry_number):
		"""
		gets a person record by its entry number
		:param entry_number: the entry number to query
		:return: the person, or None if no record found
		"""

		return self._storage.get(str(entry_number), None)

	def find(self, keyword):
		"""
		finds any person records with the nameKeyword contained in the full name.
		:param keyword: the portion of full name to search for
		:return: a list of person with the nameKeyword matching part of full name
		"""

		return [result for result in self._storage.values() if keyword in result.full_name()]

	def delete(self, entry_number):
		"""
		removes a person record by entry number. This method will not do anything if the record does not exists.
		:param entry_number: the entry number to remove
		:return: None
		"""

		if str(entry_number) in self._storage:
			del self._storage[str(entry_number)]

	def open(self, target = "addresses"):
		"""
		loads all contacts. This method must be called before the instance can be used.
		:param target: the location to load the contacts from
		:return: None
		"""

		self._storage = shelve.open(target, writeback = True)
		self._currentID = self.count()

	def close(self):
		"""
		closes and flush all the contacts. This method must be called when the specific instance is no longer used.
		:return: None
		"""

		self._storage.close()


class TestAddress(unittest.TestCase):
	"""
	This class tests the AddressBook and Address
	"""

	def tearDown(self):
		os.remove("./addresses")

	@classmethod
	def setUpClass(cls):
		if os.path.isfile("./addresses"):
			os.remove("./addresses")

	def testCreateFind(self):
		"""
		Tests if the address book can save a single address and find it again given the person's name
		:return: None
		"""
		book = PeopleBook()
		book.open()
		new_person = self._createTestData()

		book.save(new_person)

		self.assertEqual(1, book.count(), msg = "The count of address book is not equal to 1")

		retrieved = book.get(new_person.entryNumber)

		self._testAddressEqual(new_person, retrieved)
		book.close()

	def testCreateFindMultipleAddr(self):
		"""
		Tests if the address book can save multiple addresses of people with the same name and gets all the records with the name
		:return: None
		"""
		book = PeopleBook()
		book.open()
		first_person = self._createTestData()
		second_person = self._createTestData()

		book.save(first_person, second_person)

		first_retrieved = book.get(first_person.entryNumber)
		second_retrieved = book.get(second_person.entryNumber)

		self._testAddressEqual(first_person, first_retrieved)
		self._testAddressEqual(second_person, second_retrieved)
		book.close()

	def testFind(self):
		"""
		tests if the find method works as documented
		:return: None
		"""

		book = PeopleBook()
		book.open()
		first_person_found = self._createTestData()
		second_person_found = self._createTestData()
		person_not_found = self._createTestData()
		second_person_found.from_full_name("Charle King")
		person_not_found.from_full_name("Geralt of Rivia")

		book.save(first_person_found, second_person_found, person_not_found)

		retrieved_people = book.find("Charle")

		self.assertEqual(2, len(retrieved_people))
		self.assertNotIn(person_not_found, retrieved_people, msg = "Geralt of Rivia should not match Charle")
		self.assertIn(first_person_found, retrieved_people)
		self.assertIn(second_person_found, retrieved_people)
		book.close()

	def testDelete(self):
		"""
		tests if the delete truly removes record
		:return: None
		"""

		book = PeopleBook()
		book.open()
		to_delete = self._createTestData()

		book.save(to_delete)
		book.delete(to_delete.entryNumber)

		retrieved = book.get(to_delete.entryNumber)
		found = book.find("Charle")

		self.assertEqual(None, retrieved)
		self.assertEqual(0, len(found))
		book.close()

	def testUpdate(self):
		"""
		tests if the update operation updates the record and does not change the entry number
		:return: None
		"""

		book = PeopleBook()
		book.open()
		to_edit = self._createTestData()

		book.save(to_edit)
		original = to_edit.entryNumber
		edited = Person()
		edited.firstName = "Fire Keeper"
		edited.add_address("Firelink Shrine")
		edited.entryNumber = to_edit.entryNumber
		book.save(edited)

		nothing = book.find("Charle")
		fireKeeper = book.find("Fire Keeper")

		self.assertEqual(0, len(nothing))
		self.assertEqual(1, len(fireKeeper))
		self._testAddressEqual(edited, fireKeeper[0])
		self.assertEqual(original, fireKeeper[0].entryNumber)
		book.close()

	def testPersist(self):
		"""
		tests if the records are persisted, that old records from previous sessions can be reloaded.
		:return:
		"""

		book = PeopleBook()
		book.open()
		toAdd = self._createTestData()

		book.save(toAdd)
		entry_number = toAdd.entryNumber
		book.close()

		book = PeopleBook()
		book.open()
		persisted = book.get(entry_number)
		book.close()
		self._testAddressEqual(toAdd, persisted)

	def _createTestData(self):
		"""
		Creates a new Address record with identical values on each run for testing
		:return: a new Address record with identical values
		"""

		person = Person()

		# sets all the testing parameters
		person.from_full_name("Charle Root")
		person.add_address("111 test DR", "222 secondary address DR")
		person.add_phone("9191111111", "1112223333")
		person.add_email("test@viperfish.net", "test2@viperfish.net")
		person.note = "This person can do whatever on Linux"

		return person

	def _testAddressEqual(self, addr1, addr2):
		"""
		Runs tests to make sure that the two specified addresses are indeed equal
		:param addr1: the first address to test
		:param addr2: the second address to test
		:return: None
		"""
		self.assertEqual(addr1, addr2)


if __name__ == "__main__":
	unittest.main()
