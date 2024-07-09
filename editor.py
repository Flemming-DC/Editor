from PyQt5.QtWidgets import *
from PyQt5 import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
from PyQt5.QtWidgets import QWidget
import keyword
import pkgutil # list of installed packages
from dependencies.icons import resources_rc

class Editor(QsciScintilla):

    def __init__(self, font: QFont, parent: QWidget | None = None):
        super().__init__(parent)
        self.window_font = font

        self.setUtf8(True)
        self.setFont(self.window_font)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        
        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1) # auto complete shows after 1 character
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # caret
        self.setCaretForegroundColor(QColor("#dedcdc")) 
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        # self.setCaretLineBackgroundColor(QColor("#2c313c")) # color for the current line

        # EOL
        self.setEolMode(QsciScintilla.EolWindows)
        self.setEolVisibility(False)
        
        # add lexer for syntax highlighting
        self.pylexer = QsciLexerPython() 
        self.pylexer.setDefaultFont(self.window_font)

        # API (you can add autocompletion using this) my reply: ???
        self.api = QsciAPIs(self.pylexer)
        for key in keyword.kwlist + dir(__builtins__): # adding builtin functions and keywords
            self.api.add(key)
        for _, name, _ in pkgutil.iter_modules(): # adding all module names from current interpreter
            self.api.add(name)

        # for test purposes
        # you can add custom function with parameters as an example
        # self.api.add("addition(a: int, b: int)")
        self.api.prepare()

        self.setLexer(self.pylexer)

        # line numbers
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(QColor("#ff888888"))
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsFont(self.window_font)

        # keypress
        # self.keyPressEvent = self.handle_editor_press


    def keyPressEvent(self, event: QKeyEvent):
        "ctrl + space will show autocomplete"
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Space:
            self.autoCompleteFromAll()
        else:
            super().keyPressEvent(event)


    # def handle_editor_press(self, event: QKeyEvent):
    #     "ctrl + space will show autocomplete"
    #     editor = self.get_editor()
    #     if not editor:
    #         return # is this right ??
    #     if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Space:
    #         editor.autoCompleteFromAll()
    #     else:
    #         QsciScintilla.keyPressEvent(editor, event)



