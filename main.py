from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os

try:
	from moviepy.editor import VideoFileClip
except:
	from imageio.plugins import ffmpeg
	ffmpeg.download()
finally:
	from moviepy.editor import VideoFileClip


class DropField(QtWidgets.QTextEdit):
	def __init__(self, parent=None):
		super(DropField, self).__init__(parent)
		self.setAcceptDrops(True)
		self.setCursorWidth(0)

		self.validFileExtList = [".mp4", ".avi"]

		self.thr = VideoConvertionThread()
		self.thr.started.connect(self.onStarted)
		self.thr.finished.connect(self.onFinished)

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

	def onStarted(self):
		self.clear()
		self.setAcceptDrops(False)
		self.setReadOnly(True)
		self.setDisabled(True)

	def onFinished(self):
		self.setAcceptDrops(True)
		self.setReadOnly(False)
		self.setDisabled(False)


class Window(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.setWindowIcon(QtGui.QIcon('imgs/LarianLogo.png'))

		self.vbox = QtWidgets.QVBoxLayout()

		self.dropField = DropField()
		self.dropField.setAlignment(QtCore.Qt.AlignLeft)
		self.dropField.setFixedSize(480, 480)

		self.progressBar = QtWidgets.QProgressBar(self)
		self.progressBar.setFixedWidth(515)

		self.dropField.thr.started.connect(self.onVideoConvertStarted)
		self.dropField.thr.finished.connect(self.onVideoConvertFinished)

		sys.stdout = OutLog(self.dropField, sys.stdout)
		sys.stderr = OutLog(self.dropField, sys.stderr, QtGui.QColor(255, 0, 0))

		self.vbox.addWidget(self.dropField)
		self.vbox.addWidget(self.progressBar)
		self.vbox.addStretch()

		self.setLayout(self.vbox)

	def onVideoConvertStarted(self):
		self.progressBar.setRange(0, 0)

	def onVideoConvertFinished(self):
		self.progressBar.setRange(0, 1)
		self.showOnFinishMsgBox()

	def showOnFinishMsgBox(self):

		pass


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

		os.startfile(outputFolder)

	def setVideoUrls(self, urlsList):
		self.videoUrls = urlsList


class OutLog:
	def __init__(self, edit, out=None, color=None):

		self.edit = edit
		self.out = None
		self.color = color

	def write(self, m):
		if self.color:
			tc = self.edit.textColor()
			self.edit.setTextColor(self.color)

		self.edit.moveCursor(QtGui.QTextCursor.End)

		if "[MoviePy]" in m:
			m = m.replace("[MoviePy] ", "")

		if ">>>>" in m:
			m = m.replace(">>>> ", "")

		self.edit.insertPlainText(m)
		self.edit.insertPlainText("\n")

		if self.color:
			self.edit.setTextColor(tc)

		if self.out:
			self.out.write(m)

	def flush(self):
		pass


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("plastique")

	window = Window()
	window.setWindowTitle("Video converter app")
	window.setFixedSize(500, 530)
	window.show()

	sys.exit(app.exec_())