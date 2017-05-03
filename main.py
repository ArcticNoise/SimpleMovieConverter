from PyQt5 import QtCore, QtWidgets
import sys, os

try:
	from moviepy.editor import *
except:
	from imageio.plugins import ffmpeg
	ffmpeg.download()
finally:
	from moviepy.editor import *


class DropLabel(QtWidgets.QTextEdit):
	def __init__(self, parent=None):
		super(DropLabel, self).__init__(parent)
		self.setAcceptDrops(True)

		self.validFileExtList = [".mp4", ".avi"]

		self.thr = VideoConvertionThread()
		self.thr.started.connect(self.on_started)
		self.thr.finished.connect(self.on_finished)

	def dragEnterEvent(self, e, *args, **kwargs):
		for el in e.mimeData().urls():
			if os.path.splitext(el.path())[1] in self.validFileExtList:
				e.accept()
			else:
				e.ignore()

	def leaveEvent(self, *args, **kwargs):
		pass

	def dropEvent(self, e, *args, **kwargs):
		self.thr.setVideoUrls(e.mimeData().urls())
		self.thr.start()

	def on_started(self):
		self.setAcceptDrops(False)
		self.setReadOnly(True)

	def on_finished(self):
		self.setAcceptDrops(True)
		self.setReadOnly(False)


class Window(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.vbox = QtWidgets.QVBoxLayout()

		self.label = DropLabel()
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.label.setFixedSize(480, 480)
		self.vbox.addWidget(self.label)
		self.vbox.addStretch()

		self.setLayout(self.vbox)


class VideoConvertionThread(QtCore.QThread):
	def __init__(self, parent=None):
		super(VideoConvertionThread, self).__init__(parent)

		self.videoUrls = []

	def run(self):
		outputFolder = os.path.join(os.getcwd(), "output")

		if not os.path.exists(outputFolder):
			os.makedirs(self.outputFolder)

		for el in self.videoUrls:
			fileName = el.path().split("/")[-1]
			clip = VideoFileClip(el.path()[1:]).without_audio().set_fps(24)
			clip.write_videofile(os.path.join(outputFolder, fileName), ffmpeg_params=["-crf", "33"], progress_bar=False)

		self.videoUrls.clear()

	def setVideoUrls(self, urlsList):
		self.videoUrls = urlsList

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("plastique")

	window = Window()
	window.setWindowTitle("Video converter app")
	window.setFixedSize(500, 500)
	window.show()

	sys.exit(app.exec_())