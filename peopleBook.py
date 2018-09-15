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

    def __init__(self, entryNumber=-1, firstName="", middleName="", lastName="", addresses=[], phoneNumbers=[],
                 emailAddresses=[], note=""):
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

        self._entryNumber = entryNumber
        self._firstName = firstName
        self._middleName = middleName
        self._lastName = lastName
        self._addresses = list(addresses)
        self._phoneNumbers = list(phoneNumbers)
        self._emailAddresses = list(emailAddresses)
        self._note = note

    #
    # Those are getters and setters
    #

    def getEntryNumber(self):
        return self._entryNumber

    def setEntryNumber(self, entryNumber):
        self._entryNumber = entryNumber

    def getFirstName(self):
        return self._firstName

    def getLastName(self):
        return self._lastName

    def getMiddleName(self):
        return self._middleName

    def getPhoneNumbers(self):
        return self._phoneNumbers

    def getEmailAddresses(self):
        return self._emailAddresses

    def getAddresses(self):
        return self._addresses

    def getNote(self):
        return self._note

    def setAddresses(self, addresses):
        self._addresses = addresses

    def setPhoneNumbers(self, phoneNumbers):
        self._phoneNumbers = phoneNumbers

    def setEmailAddresses(self, emails):
        self._emailAddresses = emails

    def setNote(self, note):
        self._note = note

    def setFirstName(self, firstName):
        self._firstName = firstName

    def setMiddleName(self, middleName):
        self._middleName = middleName

    def setLastname(self, lastname):
        self._lastName = lastname

    def getName(self):
        """
        gets the full name of a person in the form of First Middle Last
        :return: the full name of the person
        """

        result = self._firstName
        if len(self._middleName) != 0:
            result += " " + self._middleName
        if len(self._lastName) != 0:
            result += " " + self._lastName
        return result

    def setName(self, name):
        """
        sets the full name of the person. This method will priortize first name > last name > middle name.
        In another word, if only one part of the name is present, it assumes it is the first name of the person.
        :param name: the full name of the person
        :return: None
        """

        nameParts = name.split(" ")

        # fill parts of name with empty strings if not exists
        while len(nameParts) < 3:
            nameParts.append("")

        self._firstName, self._middleName, self._lastName = tuple([n for n in nameParts])

        # if only two parts are specified, assume FirstName Lastname
        if len(nameParts) == 2:
            self._lastName, self._middleName = self._middleName, self._lastName

    def addAddress(self, *address):
        self._addresses.extend(address)

    def addPhoneNumber(self, *phoneNumber):
        self._phoneNumbers.extend(phoneNumber)

    def addEmailAddress(self, *email):
        self._emailAddresses.extend(email)

    def __str__(self):
        """
        returns an aligned, pretty print version of the data in this class for display purposes
        :return: an aligned, pretty print data string
        """

        template = "{0:>15}: {1} \n"
        return template.format("Name", self.getName()) + \
               template.format("Addresses", ", ".join(self.getAddresses())) + \
               template.format("Phone Numbers", ", ".join(self.getPhoneNumbers())) + \
               template.format("Emails", ", ".join(self.getEmailAddresses())) + \
               template.format("Note", self.getNote())


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
            if str(i.getEntryNumber()) not in self._storage:
                i.setEntryNumber(self._currentID)
                self._currentID += 1
            self._storage[str(i.getEntryNumber())] = i

    def count(self):
        """
        counts the number of records in the contact
        :return: the number of records
        """

        return len(self._storage.keys())

    def getPerson(self, entryNumber):
        """
        gets a person record by its entry number
        :param entryNumber: the entry number to query
        :return: the person, or None if no record found
        """

        return self._storage.get(str(entryNumber), None)

    def find(self, nameKeyword):
        """
        finds any person records with the nameKeyword contained in the full name.
        :param nameKeyword: the portion of full name to search for
        :return: a list of person with the nameKeyword matching part of full name
        """

        return [result for result in self._storage.values() if nameKeyword in result.getName()]

    def delete(self, entryNumber):
        """
        removes a person record by entry number. This method will not do anything if the record does not exists.
        :param entryNumber: the entry number to remove
        :return: None
        """

        if (str(entryNumber) in self._storage):
            del self._storage[str(entryNumber)]

    def open(self, target="addresses"):
        """
        loads all contacts. This method must be called before the instance can be used.
        :param target: the location to load the contacts from
        :return: None
        """

        self._storage = shelve.open(target, writeback=True)
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
        if (os.path.isfile("./addresses")):
            os.remove("./addresses")

    def testCreateFind(self):
        """
        Tests if the address book can save a single address and find it again given the person's name
        :return: None
        """
        book2Test = PeopleBook()
        book2Test.open()
        person2Add = self._createTestData()

        book2Test.save(person2Add)

        self.assertEqual(1, book2Test.count(), msg="The count of address book is not equal to 1")

        retrievedAddress = book2Test.getPerson(person2Add.getEntryNumber())

        self._testAddressEqual(person2Add, retrievedAddress)
        book2Test.close()

    def testCreateFindMultipleAddr(self):
        """
        Tests if the address book can save multiple addresses of people with the same name and gets all the records with the name
        :return: None
        """
        book2Test = PeopleBook()
        book2Test.open()
        firstperson = self._createTestData()
        secondPerson = self._createTestData()

        book2Test.save(firstperson, secondPerson)

        firstRetrieved = book2Test.getPerson(firstperson.getEntryNumber())
        secondRetrieved = book2Test.getPerson(secondPerson.getEntryNumber())

        self._testAddressEqual(firstperson, firstRetrieved)
        self._testAddressEqual(secondPerson, secondRetrieved)
        book2Test.close()

    def testFind(self):
        """
        tests if the find method works as documented
        :return: None
        """

        book2Test = PeopleBook()
        book2Test.open()
        firstPersonFound = self._createTestData()
        secondPersonFound = self._createTestData()
        personNotFound = self._createTestData()
        secondPersonFound.setName("Charle King")
        personNotFound.setName("Geralt of Rivia")

        book2Test.save(firstPersonFound, secondPersonFound, personNotFound)

        retrievedPeople = book2Test.find("Charle")

        self.assertEqual(2, len(retrievedPeople))
        self.assertNotIn(personNotFound, retrievedPeople, msg="Geralt of Rivia should not match Charle")
        self.assertIn(firstPersonFound, retrievedPeople)
        self.assertIn(secondPersonFound, retrievedPeople)
        book2Test.close()

    def testDelete(self):
        """
        tests if the delete truly removes record
        :return: None
        """

        book2Test = PeopleBook()
        book2Test.open()
        toDelete = self._createTestData()

        book2Test.save(toDelete)
        book2Test.delete(toDelete.getEntryNumber())

        retrievedPeople = book2Test.getPerson(toDelete.getEntryNumber())
        foundPeople = book2Test.find("Charle")

        self.assertEqual(None, retrievedPeople)
        self.assertEqual(0, len(foundPeople))
        book2Test.close()

    def testUpdate(self):
        """
        tests if the update operation updates the record and does not change the entry number
        :return: None
        """

        book2Test = PeopleBook()
        book2Test.open()
        toEdit = self._createTestData()

        book2Test.save(toEdit)
        originalEntryNumber = toEdit.getEntryNumber()
        edited = Person()
        edited.setFirstName("Fire Keeper")
        edited.addAddress("Firelink Shrine")
        edited.setEntryNumber(toEdit.getEntryNumber())
        book2Test.save(edited)

        shouldBeEmpty = book2Test.find("Charle")
        fireKeeper = book2Test.find("Fire Keeper")

        self.assertEqual(0, len(shouldBeEmpty))
        self.assertEqual(1, len(fireKeeper))
        self._testAddressEqual(edited, fireKeeper[0])
        self.assertEqual(originalEntryNumber, fireKeeper[0].getEntryNumber())
        book2Test.close()

    def testPersist(self):
        """
        tests if the records are persisted, that old records from previous sessions can be reloaded.
        :return:
        """

        book2Test = PeopleBook()
        book2Test.open()
        toAdd = self._createTestData()

        book2Test.save(toAdd)
        entryNumber = toAdd.getEntryNumber()
        book2Test.close()

        book2Test = PeopleBook()
        book2Test.open()
        persisted = book2Test.getPerson(entryNumber)
        book2Test.close()
        self._testAddressEqual(toAdd, persisted)

    def _createTestData(self):
        """
        Creates a new Address record with identical values on each run for testing
        :return: a new Address record with identical values
        """

        address2Add = Person()

        # sets all the testing parameters
        address2Add.setName("Charle Root")
        address2Add.addAddress("111 test DR", "222 secondary address DR")
        address2Add.addPhoneNumber("9191111111", "1112223333")
        address2Add.addEmailAddress("test@viperfish.net", "test2@viperfish.net")
        address2Add.setNote("This person can do whatever on Linux")

        return address2Add

    def _testAddressEqual(self, addr1, addr2):
        """
        Runs tests to make sure that the two specified addresses are indeed equal
        :param addr1: the first address to test
        :param addr2: the second address to test
        :return: None
        """

        self.assertEqual(addr1.getFirstName(), addr2.getFirstName())
        self.assertEqual(addr1.getMiddleName(), addr2.getMiddleName())
        self.assertEqual(addr1.getLastName(), addr2.getLastName())
        self.assertListEqual(addr1.getAddresses(), addr2.getAddresses())
        self.assertListEqual(addr1.getPhoneNumbers(), addr2.getPhoneNumbers())
        self.assertListEqual(addr1.getEmailAddresses(), addr2.getEmailAddresses())
        self.assertEqual(addr1.getNote(), addr2.getNote())


if __name__ == "__main__":
    unittest.main()
