import sys
import json
import uuid
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel, QStackedWidget, QFormLayout, QLineEdit
from functools import partial
from dataclasses import dataclass, asdict

class PeopleIndexView(QtWidgets.QWidget):
    VIEW_INDEX=0

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
        self.tableWidget.setColumnCount(3)

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

            btn = QPushButton(text="Delete", parent=self.tableWidget)
            btn.clicked.connect(partial(self.deletePerson, person.id, index+1))
            self.tableWidget.setCellWidget(index + 1, 2, btn)     

    def deletePerson(self, id, rowIdx):
        self.repo.deleteById(id)
        self._renderTable(self.repo.getAll())

    def addNewPerson(self):
        masterLayout.setCurrentIndex(NewPersonView.VIEW_INDEX)

    def displayed(self):
        self._renderTable()

class NewPersonView(QtWidgets.QWidget):
    VIEW_INDEX=1

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
        masterLayout.setCurrentIndex(PeopleIndexView.VIEW_INDEX)
        peopleIndex._renderTable(self.repo.getAll())

    def displayed(self):
        None



@dataclass
class Person:
    id: str
    name: str

class PeopleRepository():
    def __init__(self, jsonFile):
        self.jsonFile = jsonFile
        self.peopleData = json.load(open(jsonFile))

    def getAll(self):
        people = []
        
        for personData in self.peopleData:
            people.append(Person(id=personData["id"], name = personData["name"]))

        return people

    def deleteById(self, id):
        personIndex = list([index for index, person in enumerate(self.peopleData) if person["id"] == id])[0]
        del self.peopleData[personIndex]
        self._saveToFile()

    def create(self, person):
        print(person)
        self.peopleData.append(asdict(person))
        self._saveToFile()

    def _saveToFile(self):
        with open(self.jsonFile, "w") as outfile:
            json_object = json.dumps(self.peopleData)
            outfile.write(json_object)

def display(currentIndex):
    # print(f"display: {currentIndex}")
    masterLayout.currentWidget().displayed()
    
    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    peopleRepo = PeopleRepository("people.json")
    masterLayout = QStackedWidget()
    peopleIndex = PeopleIndexView(peopleRepo)
    newPersonView = NewPersonView(peopleRepo)
    masterLayout.addWidget(peopleIndex)
    masterLayout.addWidget(newPersonView)
    
    masterLayout.currentChanged.connect(display)
    
    masterLayout.resize(800, 600)
    masterLayout.show()

    sys.exit(app.exec_())


# Display JSON file of people DONE
    # Display Name of each person DONE
    # Add delete button to each person DONE
    # Pressing delete button removes from JSON file DONE
    # Pressing delete button removes from screen DONE
# Display add new person button
    # Clicking add new person renders form DONE
    # Form has name attribute DONE
    # Display create button DONE
    # Clicking create saves person to the JSON file DONE
    # handle duplicate names/ids
    # handle validation (name/id cant be empty)
    # change master layout to a class, move "display" method inside
# Display edit button next to each person
    # Clicking edit loads form
    # Name is pre-populated with a name
    # Display update button
    # Clicking update saves name changes to JSON file