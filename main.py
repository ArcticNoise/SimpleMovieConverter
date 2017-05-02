from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os

try:
	from moviepy.editor import *
except:
	from imageio.plugins import ffmpeg
	ffmpeg.download()
finally:
	from moviepy.editor import *


class DropLabel(QtWidgets.QLabel):
	def __init__(self, parent=None):
		super(DropLabel, self).__init__(parent)
		self.setAcceptDrops(True)
		self.outputFolder = os.path.join(os.getcwd(), "output")
		if not os.path.exists(self.outputFolder):
			os.makedirs(self.outputFolder)

	def dragEnterEvent(self, e, *args, **kwargs):
		for el in e.mimeData().urls():
			if os.path.splitext(el.path())[1] in [".mp4", ".avi"]:
				e.accept()
			else:
				e.ignore()

	def leaveEvent(self, *args, **kwargs):
		pass

	def dropEvent(self, e, *args, **kwargs):
		for el in e.mimeData().urls():
			fileName = el.path().split("/")[-1]
			clip = VideoFileClip(el.path()[1:]).without_audio().set_fps(24)
			clip.write_videofile(os.path.join(self.outputFolder, fileName), ffmpeg_params=["-crf", "33"], progress_bar=False)


class Window(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.vbox = QtWidgets.QVBoxLayout()

		self.label = DropLabel()
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.label.setFixedSize(500, 500)
		self.label.setText("Hello")
		self.vbox.addWidget(self.label)
		self.vbox.addStretch()

		self.setLayout(self.vbox)


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("plastique")

	window = Window()
	window.setWindowTitle("Video converter app")
	window.setFixedSize(500, 500)
	window.show()

	sys.exit(app.exec_())