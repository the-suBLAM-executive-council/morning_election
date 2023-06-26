import sys
import json
import uuid
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel, QStackedWidget, QFormLayout, QLineEdit
from functools import partial
from dataclasses import dataclass, asdict

class PeopleIndexView(QtWidgets.QWidget):
    def __init__(self, peopleRepo):
        super().__init__()
        self.repo = peopleRepo
        self.setupTable()
        self._renderTable()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        
        newPersonBtn = QPushButton(text="Add New Person", parent=self)
        newPersonBtn.clicked.connect(self.addNewPerson)
        self.layout.addWidget(newPersonBtn)
        
        self.setLayout(self.layout)

    #Create table
    def setupTable(self):
        self.tableWidget = QTableWidget()

        #Column count
        self.tableWidget.setColumnCount(4)

        #Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _renderTable(self, people=None):
        people = people or self.repo.getAll()
        self.tableWidget.clear()

        #Row count
        self.tableWidget.setRowCount(len(people) + 1) 

        # Set headings
        self.tableWidget.setItem(0,0, QTableWidgetItem("ID"))
        self.tableWidget.setItem(0,1, QTableWidgetItem("Name"))

        for index, person in enumerate(people):
            self.tableWidget.setItem(index + 1, 0, QTableWidgetItem(person.id))
            self.tableWidget.setItem(index + 1, 1, QTableWidgetItem(person.name))

            deleteBtn = QPushButton(text="Delete", parent=self.tableWidget)
            deleteBtn.clicked.connect(partial(self.deletePerson, person.id, index+1))
            self.tableWidget.setCellWidget(index + 1, 2, deleteBtn)     
            
            editBtn = QPushButton(text="Edit", parent=self.tableWidget)
            editBtn.clicked.connect(partial(self.editPerson, person.id))
            self.tableWidget.setCellWidget(index + 1, 3, editBtn)  

    def deletePerson(self, id, rowIdx):
        self.repo.deleteById(id)
        self._renderTable(self.repo.getAll())


    def editPerson(self, id):
        masterLayout.showEditView(id)

    def addNewPerson(self):
        masterLayout.showNewView()

    def reRender(self):
        self._renderTable()

class NewPersonView(QtWidgets.QWidget):
    def __init__(self, peopleRepo):
        super().__init__()
        self.repo = peopleRepo
        self.layout = QFormLayout()
        self.nameLineEdit = QLineEdit()
        self.layout.addRow(QLabel("Name"), self.nameLineEdit)

        createPersonBtn = QPushButton(text="Create", parent=self)
        createPersonBtn.clicked.connect(self.create)
        self.layout.addRow(createPersonBtn)

        self.setLayout(self.layout)


    def create(self):
        self.repo.create(Person(id = str(uuid.uuid4()), name = self.nameLineEdit.text()))
        masterLayout.showIndexView()


class EditPersonView(QtWidgets.QWidget):
    def __init__(self, peopleRepo):
        super().__init__()
        self.repo = peopleRepo
        self.layout = QFormLayout()
        self.nameLineEdit = QLineEdit()
        self.layout.addRow(QLabel("Name"), self.nameLineEdit)

        updatePersonBtn = QPushButton(text="Update", parent=self)
        updatePersonBtn.clicked.connect(self.update)
        self.layout.addRow(updatePersonBtn)

        self.setLayout(self.layout)


    def update(self):
        self.person.name = self.nameLineEdit.text()
        self.repo.update(self.person)
        masterLayout.showIndexView()

    def loadPerson(self, id):
        self.person = self.repo.findById(id)
        self.nameLineEdit.setText(self.person.name)



@dataclass
class Person:
    id: str
    name: str

class PeopleRepository():
    def __init__(self, jsonFile):
        self.jsonFile = jsonFile

    def getAll(self):
        people = []
        
        for personData in json.load(open(self.jsonFile)):
            people.append(Person(id=personData["id"], name = personData["name"]))

        return people
    
    def findById(self, id):
        for person in self.getAll():
            if person.id == id:
                return person
            
        raise(f"Didn't find Person with ID: {id}")

    def deleteById(self, id):
        allPeople = self.getAll()
        for person in allPeople:
            if person.id == id:
                allPeople.remove(person)
                self._saveToFile(allPeople)
                return

        raise(f"Didn't find Person with ID: {id}")

    def create(self, person):
        allPeople = self.getAll()
        allPeople.append(person)
        self._saveToFile(allPeople)

    def update(self, editedPerson):
        allPeople = self.getAll()
        for person in allPeople:
            if person.id == editedPerson.id:
                allPeople.remove(person)
                allPeople.append(editedPerson)
                self._saveToFile(allPeople)
                return
        
        raise(f"Didn't find Person with ID: {editedPerson.id}")

    def _saveToFile(self, people):
        with open(self.jsonFile, "w") as outfile:
            peopleDicts = [asdict(person) for person in people]
            outfile.write(json.dumps(peopleDicts))
    
class MasterLayout(QStackedWidget):
    def __init__(self, peopleRepo, peopleIndexView, newPersonView, editPersonView):
        super().__init__()

        self.indexIndex = 0
        self.newIndex = 1
        self.editIndex = 2
        self.addWidget(peopleIndexView)
        self.addWidget(newPersonView)
        self.addWidget(editPersonView)
        self.resize(800, 600)

    def showIndexView(self):
        self.setCurrentIndex(self.indexIndex)
        self.currentWidget().reRender()

    def showNewView(self):
        self.setCurrentIndex(self.newIndex)

    def showEditView(self, id):
        self.setCurrentIndex(self.editIndex)
        self.currentWidget().loadPerson(id)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    peopleRepo = PeopleRepository("people.json")
    masterLayout = MasterLayout(
        peopleRepo,
        peopleIndexView=PeopleIndexView(peopleRepo),
        newPersonView=NewPersonView(peopleRepo),
        editPersonView=EditPersonView(peopleRepo)
    )
    
    masterLayout.show()

    sys.exit(app.exec_())



## CRUD TODO ##
# handle duplicate names/ids
# handle validation (name/id cant be empty)
# pre-load everyone
# use Proper IDs for everyone
# change order of buttons
# don't display ID
# add avatars to table
# pick avatars from list in edit
# add avatars to repo
# add tests for repo
# investigate how to test views
# make enter submit form

## NEXT ITEMS ##
# "spin" and select a winner
# store wins against a person
# initiate a celebration upon win
# virtual keyboard
# Set viewport to correct size for pi
# investigate how to style layouts
# API calls for syncing people repo and standup repo