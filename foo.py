import sys
import json
import uuid
import os
import random
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel, QStackedWidget, QFormLayout, QLineEdit, QLineEdit
from functools import partial
from dataclasses import dataclass, asdict
from typing import List

os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

class StandupCreateView(QtWidgets.QWidget):
    def __init__(self, peopleRepo):
        super().__init__()
        self.repo = peopleRepo
        self.layout = QFormLayout()

        self.setupTable()
        self._renderTable()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        
        editPeopleBtn = QPushButton(text="Edit People", parent=self)
        editPeopleBtn.clicked.connect(self.editPeople)
        self.layout.addWidget(editPeopleBtn) 

        startStandupBtn = QPushButton(text="Start Standup", parent=self)
        startStandupBtn.clicked.connect(self.startStandup)
        self.layout.addWidget(startStandupBtn)
        
        self.setLayout(self.layout)

        self._chosenPeople = {}
        for person in self.repo.getAll():
            self._chosenPeople[person.id] = True

    #Create table
    def setupTable(self):
        self.tableWidget = QTableWidget()

        #Column count
        self.tableWidget.setColumnCount(1)

        #Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tableWidget.itemClicked.connect(self.handlePersonClicked)

    def _renderTable(self, people=None):
        people = people or self.repo.getAll()
        self.tableWidget.clear()

        #Row count
        self.tableWidget.setRowCount(len(people) + 1) 

        # Set headings
        self.tableWidget.setItem(0,0, QTableWidgetItem("Here?"))

        for index, person in enumerate(people):
            personHere = QTableWidgetItem(person.name)
            personHere.personId = person.id
            personHere.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled) 
            personHere.setCheckState(QtCore.Qt.Checked)
            self.tableWidget.setItem(index + 1, 0, personHere)

    def handlePersonClicked(self, personRow):
        self._chosenPeople[personRow.personId] = personRow.checkState() == QtCore.Qt.Checked

    def editPeople(self):
        masterLayout.showPeopleIndexView()

    def startStandup(self):
        standup = self.createStandup()
        masterLayout.showStandupShowView(standup)

    def createStandup(self):
        people = []
        for id in self._chosenPeople.keys():
            if self._chosenPeople[id] == True:
                people.append(self.repo.findById(id))

        return Standup(people=people, winner=random.choice(people))

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

        createStandupBtn = QPushButton(text="Back to Stand Up", parent=self)
        createStandupBtn.clicked.connect(self.goBackToStandup)
        self.layout.addWidget(createStandupBtn)
        
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
        masterLayout.showEditPersonView(id)

    def addNewPerson(self):
        masterLayout.showNewPersonView()

    def goBackToStandup(self):
        masterLayout.showStandupCreateView()

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
        masterLayout.showPeopleIndexView()


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
        masterLayout.showPeopleIndexView()

    def loadPerson(self, id):
        self.person = self.repo.findById(id)
        self.nameLineEdit.setText(self.person.name)

class StandupShowView(QtWidgets.QWidget):
    def __init__(self, peopleRepo):
        super().__init__()
        self.repo = peopleRepo
        self.layout = QFormLayout()
        self.winnerLabel = QLabel()
        self.layout.addRow(self.winnerLabel)
        backBtn = QPushButton(text="Back", parent=self)
        backBtn.clicked.connect(self.goBack)
        self.layout.addRow(backBtn)
        self.setLayout(self.layout)

    def show(self, standup):
        self.winnerLabel.setText(standup.winner.name)
    
    def goBack(self):
        masterLayout.showStandupCreateView()



@dataclass
class Person:
    id: str
    name: str

@dataclass
class Standup:
    people: List[Person]
    winner: Person

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
    def __init__(self, standupCreateView, peopleIndexView, newPersonView, editPersonView, standupShowView):
        super().__init__()

        self._standupCreateIndex = 0
        self._peopleIndexIndex = 1
        self._newPersonIndex = 2
        self._editPersonIndex = 3
        self._showStandupIndex = 4
        self.addWidget(standupCreateView)
        self.addWidget(peopleIndexView)
        self.addWidget(newPersonView)
        self.addWidget(editPersonView)
        self.addWidget(standupShowView)
        self.resize(800, 600)
    
    def showStandupCreateView(self):
        self.setCurrentIndex(self._standupCreateIndex)

    def showPeopleIndexView(self):
        self.setCurrentIndex(self._peopleIndexIndex)
        self.currentWidget().reRender()

    def showNewPersonView(self):
        self.setCurrentIndex(self._newPersonIndex)

    def showEditPersonView(self, id):
        self.setCurrentIndex(self._editPersonIndex)
        self.currentWidget().loadPerson(id)

    def showStandupShowView(self, standup):
        self.setCurrentIndex(self._showStandupIndex)
        self.currentWidget().show(standup)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    peopleRepo = PeopleRepository("people.json")
    masterLayout = MasterLayout(
        standupCreateView=StandupCreateView(peopleRepo),
        peopleIndexView=PeopleIndexView(peopleRepo),
        newPersonView=NewPersonView(peopleRepo),
        editPersonView=EditPersonView(peopleRepo),
        standupShowView=StandupShowView(peopleRepo)
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
# store standups
# initiate a celebration upon win
# Set viewport to correct size for pi
# investigate how to style layouts
