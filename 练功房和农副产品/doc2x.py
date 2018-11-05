import win32com
from win32com.client import Dispatch, constants
filenamein=r'D:\pyS\iTN8600-SQ4_A_SYSTEM_7.6.32_20180224.doc'
filenameout=r'D:\pyS\iTN8600-SQ4_A_SYSTEM_7.6.32_20180224.docx'
w = win32com.client.Dispatch('Word.Application')
w.Visible = 0
w.DisplayAlerts = 0
wc = win32com.client.constants
doc = w.Documents.Open(filenamein)
w.ActiveDocument.SaveAs(filenameout,16)
w.Documents.Close()
w.Quit()