from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window
from windows.message_window import Message_window

class Edit_sequence_window(QWidget,uic.loadUiType(os.path.join("windows/ui","edit_sequence_window.ui"))[0]):
    def __init__(self,light_display,database_manager,sequence_window):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.sequence_window = sequence_window
        self.setWindowTitle("Edit Sequence Window")
        self.initUI()

    def initUI(self):
        self.update_button.clicked.connect(self.update_pressed)
        self.delete_button.clicked.connect(self.delete_pressed)
        sequence_id = self.sequence_window.get_sequence_id()
        if sequence_id is None:
            self.error_window = Error_window("There is no sequence opened. Please try openeing or saving one before trying to edit one.")
            self.close()
            return
        else:
            self.show()
            self.table = TableWidget(self)
            self.layout.addWidget(self.table)
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["number","time delay (s)","select"])
            self.playbacks = self.database_manager.query_db("SELECT p.playback_name,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ?",(sequence_id,))
            self.table.setRowCount(len(self.playbacks))
            header = self.table.horizontalHeader()
            for i in range(2):
                header.setSectionResizeMode(i,QtWidgets.QHeaderView.Stretch)

            self.check_boxes = []
            for i,dict in enumerate(self.playbacks):
                playback_name = dict["playback_name"]
                time_delay = dict["time_delay"]

                no = self.extract_playback_number(playback_name)
                number_item = QTableWidgetItem(str(no))
                number_item.setFlags(number_item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(i,0,number_item)
                time_delay_item = QTableWidgetItem(str(time_delay))
                time_delay_item.setFlags(time_delay_item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(i,1,time_delay_item)

                check_box_item = QTableWidgetItem()
                check_box_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_box_item.setTextAlignment(Qt.AlignCenter)
                check_box_item.setCheckState(Qt.Unchecked)

                self.table.setItem(i,2,check_box_item)
                self.check_boxes.append(check_box_item)

            self.table.resizeRowsToContents()
            self.table.resizeColumnsToContents()


    def extract_playback_number(self,playback_name): #returns the number after no
        for i in range(len(playback_name),0,-1):
            if playback_name[i:i+2] == "no":
                pos = i+2
        return playback_name[pos:len(playback_name)]

    def update_pressed(self):
        rig_id = self.light_display.get_rig_id()
        reordered_playback_names = [None]*len(self.playbacks)
        playback_order = []
        for row in range(len(self.playbacks)):
            number = self.table.item(row,0).text()
            playback_order.append(number)
        for i,number in enumerate(playback_order):
            for playback in self.playbacks:
                if self.extract_playback_number(playback["playback_name"]) == number:
                    reordered_playback_names[i] = playback["playback_name"]

        playback_ids = []
        for i,dict in enumerate(self.playbacks):
            playback_name = dict["playback_name"]
            playback_id = self.database_manager.query_db("SELECT playback_id FROM Playbacks WHERE rig_id = ? AND playback_name = ?",(rig_id,playback_name))
            playback_ids.append(playback_id)
        for i,id in enumerate(playback_ids):
            self.database_manager.query_db("UPDATE Playbacks SET playback_name = ? WHERE playback_id = ?",(reordered_playback_names[i],id[0]["playback_id"]))

        sequence_id = self.sequence_window.get_sequence_id()
        sequence_playbacks = self.database_manager.query_db("SELECT s.playback_id,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ? ORDER BY p.playback_name ",(sequence_id,))
        self.sequence_window.update_sequence_playbacks(sequence_playbacks)
        self.message_window = Message_window("The sequence was updated")
        self.close()

    def delete_pressed(self):
        qm = QMessageBox
        result = qm.question(self,'Delete Playbacks?', "Are you sure you want to delete the playbacks?", qm.Yes | qm.No)
        if result == qm.Yes:
            rig_id = self.light_display.get_rig_id()
            for i,dict in enumerate(self.playbacks):
                playback_name = dict["playback_name"]
                if self.table.item(i,2).checkState():
                    self.database_manager.query_db("DELETE FROM Playbacks WHERE playback_name = ? AND rig_id = ?",(playback_name,rig_id))

            sequence_id = self.sequence_window.get_sequence_id()
            sequence_playbacks = self.database_manager.query_db("SELECT s.playback_id,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ? ORDER BY p.playback_name ",(sequence_id,))
            self.sequence_window.update_sequence_playbacks(sequence_playbacks)
            self.message_window = Message_window("The sequence was updated")
            self.close()




class TableWidget(QTableWidget):  #taken from https://stackoverflow.com/questions/26227885/drag-and-drop-rows-within-qtablewidget
    def __init__(self,parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.setStyleSheet("background-color:white;color:black;")

    def dropEvent(self, event: QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]
            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()
            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()
