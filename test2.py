import re, glob, os

#returns [base name, padding, filetype, number of files, first file, last file]
def getSeqInfo(file):
    dir = os.path.dirname(file)
    file = os.path.basename(file)
    segNum = re.findall(r'\d+', file)[-1]
    numPad = len(segNum)
    baseName = file.split(segNum)[0]
    fileType = file.split('.')[-1]
    globString = baseName
    for i in range(0,numPad):
        globString += '?'
    theGlob = glob.glob(dir+'\\'+globString+file.split(segNum)[1])
    numFrames = len(theGlob)
    firstFrame = theGlob[0]
    lastFrame = theGlob[-1]
    return [baseName, numPad, fileType, numFrames, firstFrame, lastFrame]


if __name__ == '__main__':
    t = getSeqInfo('\\\\elephant\\SleepDeprived\\shotgun\\mastertemplate\\publish\\maya\\model.main\\fakeMaya_v001.ma')
    print t







#
#
#
# # -*- coding: utf-8 -*-
# #
# # This program is free software: you can redistribute it and/or modify
# # it under the terms of the GNU General Public License as published by
# # the Free Software Foundation, either version 3 of the License, or
# # (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# '''
# App that displays a GUI that uses a model that is updated using
# a backend.
# Running this app displays how many (hundred) events have been dispatched
# between the backend-thread and the GUI.
#
# Please also read the bug report at the end of the code
#
# In real world the backend is a tornado ioloop that requests network resources
# and the GUI should process JSON from those requests. Inspired by backbone.js.
#
# The workaround is not to use threads in pyside.
# '''
#
# import atexit
# import os
# import time
# import sys
#
# from PySide.QtGui import QApplication, QWidget, QMainWindow, QVBoxLayout
# from PySide.QtCore import (
#     Qt, QLocale, QTranslator, QTimer, QThread,
#     QObject, Signal, QCoreApplication
# )
# LOOP_TIMER_NOOP = 0.01
#
#
# class many_items(QWidget):
#     '''
#     Widget that exists only to be visible and to process the backend data.
#     '''
#     def __init__(self, parent, dispatcher):
#         QWidget.__init__(self, parent)
#         dispatcher.model_changed.connect(self.handler)
#         self.event_handled = 0
#
#     def handler(self, model_json):
#         # process data from the backend thread
#         data = ''
#         for c in model_json:
#             data += str(c)
#         # print 'many_item', data, self.event_handled
#         self.event_handled += 1
#
#
# class some_items(QWidget):
#     '''
#     Widget that contains multiple widgets connected to the backend data.
#     The widget itself is also connected, it should be able to have many
#     more 'many_items' in the QVBoxLayout
#     '''
#     def __init__(self, parent, dispatcher):
#         QWidget.__init__(self, parent)
#         self.ui = QVBoxLayout(self)
#         self.items = []
#         self.event_handled = 0
#
#         dispatcher.model_changed.connect(self.handler)
#         for i in range(0, 10):
#             item = many_items(self, dispatcher)
#             self.ui.addWidget(item)
#             self.items.append(item)
#
#     def handler(self, model_json):
#         # process data from the backend thread
#         data = ''
#         for c in model_json:
#             data += str(c)
#         # print 'some_item', data, self.event_handled
#         self.event_handled += 1
#
#
# class main_item(QWidget):
#     '''
#     Main item that is used as central widget and contains many some_items in a
#     QVBoxLayout.
#     The widget itself is also connected.
#     '''
#     def __init__(self, parent, dispatcher):
#         QWidget.__init__(self, parent)
#         self.resize(30, 60)
#         self.ui = QVBoxLayout(self)
#         self.items = []
#         self.event_handled = 0
#
#         dispatcher.model_changed.connect(self.handler)
#         # Reduce the range to simplify the testcase and decrease the number of
#         # connected objects.
#         # somexmany: dispatched events required
#         # 0-10x10: ~ 1k
#         # 100x100: > 5k
#         # 10x100: > 20k
#         # 100x10: ~ 1k
#         # 1x1: > 1M
#         # 10x1: < 1k
#         # 1000x1: > 5k
#         # if >5k: killall python, restart!
#
#         for i in range(0, 10):
#             item = some_items(self, dispatcher)
#             self.ui.addWidget(item)
#             self.items.append(item)
#
#     def handler(self, model_json):
#         # process data from the backend thread
#         data = ''
#         for c in model_json:
#             data += str(c)
#         # print 'main_item', data, self.event_handled
#         self.event_handled += 1
#
# #
# # the following code is required to make the window and simulate a backend
# #
#
#
# class mainwindow(QMainWindow):
#     def __init__(self, backend, logger=None):
#         QMainWindow.__init__(self)
#         self.backend = backend
#         self.setCentralWidget(main_item(self, self.backend))
#         self.resize(300, 600)
#         self.show()
#         self.backend.shutdown.connect(self.shutdown)
#         self.backend.request_data.emit()
#
#     def shutdown(self):
#         print 'mainwindow.shutdown'
#         QApplication.setQuitOnLastWindowClosed(True)
#         self.close()
#
#
# class backend_thread(QThread):
#     '''
#     Backend Thread that is responsible to create the backend dispatcher and
#     make it available to the main-thread. The Backend Thread continuously
#     executes QCoreApplication.processEvents to ensure that emit'ed signals are
#     received in this thread. The dispatcher QObject is created when the thread
#     has started.
#     '''
#
#     def __init__(self, dispatcher_class):
#         QThread.__init__(self, None)
#         self.backend_dispatcher_class = dispatcher_class
#         self.backend_dispatcher = None
#
#     def get_dispatcher(self):
#         '''
#         Returns the dispatcher for the main-thread.
#         Should be called after start()
#         '''
#         while self.backend_dispatcher is None:
#             # Thread not yet running
#             # wait until the dispatcher is available
#             time.sleep(LOOP_TIMER_NOOP)
#         return self.backend_dispatcher
#
#     def run(self):
#         '''
#         Backend Thread main. Schedules qt event loop and enters the tornado
#         event loop.
#         '''
#         self.backend_dispatcher = self.backend_dispatcher_class()
#         self.backend_dispatcher.shutdown.connect(self.quit)
#         self.exec_()
#
#
# class backend_dispatcher(QObject):
#     '''
#     Backend Dispatcher to be used by the main thread. All functions of this
#     class are private and must not be called from the main thread. only
#     signals may be emitted that qt promises to be thread safe. Most signals
#     receive a done_signal and a failed_signal in order to handle the async
#     requests.
#     '''
#
#     model_changed = Signal(basestring)
#     request_data = Signal()
#     available = Signal()
#     shutdown = Signal()
#
#     def __init__(self):
#         QObject.__init__(self)
#         # receive signal from main thread
#         self.request_data.connect(self._request_data)
#         self.dispatched_events = 0
#
#     def _request_data(self):
#         # send response to main thread
#         # the data is chosen to see the actual corruption
#         # the corruption is not consistently happening
#         self.model_changed.emit(
#             '1234567812345678'
#             '1234pay8load5678'
#             '1234567812345678'
#             '1234567812345678'
#             '')
#         self._schedule_request_data()
#
#     def _schedule_request_data(self):
#         '''
#         Schedule request_data without producing a endless stack.
#         '''
#         self.dispatched_events += 1
#         if self.dispatched_events % 100 == 0:
#             print self.dispatched_events, int(sys.argv[1])
#         if int(sys.argv[1]) - self.dispatched_events < 0:
#             print 'requested amount of requests reached'
#             self.shutdown.emit()
#             # do not schedule more requests
#             # sys.exit(0)
#         else:
#             timer = QTimer(self)
#             timer.start(10)
#             timer.setSingleShot(True)
#             timer.timeout.connect(self._request_data)
#
#
# def run_gui():
#     '''
#     Run the GUI for the application.
#     '''
#     qApp = QApplication(sys.argv)
#
#     backend = backend_thread(backend_dispatcher)
#     backend.start()
#     dispatcher = backend.get_dispatcher()
#
#     item_window = mainwindow(dispatcher)
#     item_window.show()
#
#     exit_code = qApp.exec_()
#     sys.exit(exit_code)
#
#
# if __name__ == '__main__':
#     run_gui()
