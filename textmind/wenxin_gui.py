# -*- coding: utf-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import sys,time,os,chardet
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from wenxin_ui import Ui_MainWindow

from wenxin import *

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class MainForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        time.sleep(1)
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.pushButton_about,QtCore.SIGNAL("clicked()"), self.about)
        QtCore.QObject.connect(self.ui.pushButton_clear,QtCore.SIGNAL("clicked()"), self.clear_text)
        QtCore.QObject.connect(self.ui.pushButton_analysis,QtCore.SIGNAL("clicked()"), self.analysis)
        QtCore.QObject.connect(self.ui.pushButton_import,QtCore.SIGNAL("clicked()"), self.file_import)
        QtCore.QObject.connect(self.ui.pushButton_save,QtCore.SIGNAL("clicked()"), self.file_save)
        QtCore.QObject.connect(self.ui.pushButton_append,QtCore.SIGNAL("clicked()"), self.file_append)


    def about(self):
        QMessageBox.about(self,"About TextMind",self.tr("“文心”中文心理分析系统是由中科院心理所计算网络心理实验室"
            "（http://ccpl.psych.ac.cn）研发的，针对中文文本进行语言分析的软件系统。\n"
            "通过“文心”，您可以便捷地分析文本中使用的不同类别语言的程度、偏好等特点。\n\n\n"
            "如果您在使用中遇到问题，请您通过邮件向我们反馈：textmind@live.com"))

    def clear_text(self):
        self.ui.textEdit.clear()

    def file_import(self):
        fd = QtGui.QFileDialog(self)
        fname = fd.getOpenFileName(parent=self, caption=self.tr("请选择要导入的文本文件"),
                                   filter=QString("Text File(*.txt);;Any File(*.*)"))
        fname = unicode(fname)
        if os.path.isfile(fname):
            fp = codecs.open(fname,'r')
            content  = fp.read()
            encoding_det = chardet.detect(content).get('encoding')
            content = content.decode(encoding_det)

            self.ui.textEdit.setPlainText(content)

    def analysis(self):
        txt = self.ui.textEdit.toPlainText()
        txt = unicode(QtCore.QString(txt)).encode('utf-8')
        txt = txt.strip(' \t\r\n')
        if len(txt)<1:
           QMessageBox.about(self,"提示信息",self.tr("请您正确输入要分析的文本！"))
           return

        textmind = TextMind()
        result = textmind.process_paragraph(txt)
        self.analysis_result = result
        r = result.stat()

        table_view = self.ui.table
        table_view.clearContents()
        table_view.setRowCount(len(r))
        num = 0
        for k,v in r.iteritems():
           item_id = QTableWidgetItem('%03d' % (num+1))
           item_key = QTableWidgetItem(k)
           item_value = QTableWidgetItem('%s' % v)
           table_view.setItem(num, 0, item_id)
           table_view.setItem(num, 1, item_key)
           table_view.setItem(num, 2, item_value)
           num += 1

        self.ui.pushButton_save.setEnabled(True)
        self.ui.pushButton_append.setEnabled(True)


    def file_save(self):
        r = self.analysis_result
        if r is None or len(r._results) == 0:
            return

        fd = QtGui.QFileDialog(self)
        fpath =fd.getSaveFileName(parent=self, caption=self.tr("将分析结果导出至文件"),
                                  filter=self.tr("逗号分隔文件[可用Excel直接打开](*.csv)"))
        fpath = unicode(fpath)
        if os.path.exists(fpath):
            with codecs.open(fpath, 'w', encoding='utf-8') as fp:
                fp.write(u'\uFEFF\n')
                self.analysis_result.dump(fp=fp,separator=',',contains_header=True)
                fp.write(u'\n')

    def file_append(self):
        r = self.analysis_result
        if r is None or len(r._results) == 0:
            return

        fd = QtGui.QFileDialog(self)
        fpath =fd.getSaveFileName(parent=self, caption=self.tr("将分析结果附加至文件[不删除原有文件]"),
                                  filter=self.tr("逗号分隔文件[可用Excel直接打开](*.csv)"))
        fpath = unicode(fpath)
        if os.path.exists(fpath):
            with codecs.open(fpath, 'a', encoding='utf-8') as fp:
                self.analysis_result.dump(fp=fp,separator=',')
                fp.write(u'\n')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    splash=QSplashScreen(QPixmap("./image/splash.png"))
    font = QtGui.QFont()
    font.setPointSize(12)
    splash.setFont(font)
    splash.show()
    splash.showMessage(("Loading....."))
    app.processEvents()
    main_form = MainForm()
    main_form.show()
    splash.finish(main_form)
    sys.exit(app.exec_())