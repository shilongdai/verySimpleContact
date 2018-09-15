# verySimpleContact
This is a very simple command line contact mangement utility. It allows the user to track people's name, addresses, phone numbers, and emails.

# Installation
Simply clone the project to the location where you would like to store the contact informations. Ensure that you have python 3.x installed on your computer.

# Running
Run:

`python contact.py` to view all operations  

`python contact.py add firstname=Charle middlename=T. lastname=Root addresses=123 example DR phone_numbers=1111111111 emails=test@viperfish.net,test2@viperfish.net` to add record  

`python contact.py update [entry_number] lastname=Updated` to update record  

`python contact.py get 0 1 2 [entry_numbers]...` to get records  

`python contact.py keyword name "keyword1" "keyword2"...` to find by name  

`python contact.py remove 0 1 2 [entry_numbers]...` to remove records  
