from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
from PyQt5.QtWidgets import QWidget
import sys, os
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.side_bar_clr = "#282c34"

        self.init_ui()

        self.current_file = None

    def init_ui(self):
        self.setWindowTitle("PyQt Editor")
        self.resize(1300, 900)

        self.setStyleSheet(open("./dependencies/style.qss").read())
        self.window_font = QFont("Fire Code") # alternative Consolas font
        self.window_font.setPointSize(12) # video chose 16, but thats too large
        self.setFont(self.window_font)

        self.set_up_menu()
        self.set_up_body()

        self.show()

    def get_editor(self) -> QsciScintilla: 
        # it makes the editor, isn't that a misnomer?
        
        editor = QsciScintilla()
        editor.setUtf8(True)
        editor.setFont(self.window_font)
        editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        editor.setIndentationGuides(True)
        editor.setTabWidth(4)
        editor.setIndentationsUseTabs(False)
        editor.setAutoIndent(True)
        
        # autocomplete todo
        # caret
        # EOL
        editor.setEolMode(QsciScintilla.EolWindows)
        editor.setEolVisibility(False)
        
        # add lexer
        editor.setLexer(None)

        return editor

    def set_new_tab(self, path: Path, is_new_file=False):
        if not path.is_file():
            return
        if not is_new_file and self.is_binary(path):
            self.statusBar().showMessage("Cannot open binary file")
            return
        
        if not is_new_file:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == path.name:
                    self.tab_widget.setCurrentIndex(i)
                    self.current_file = path
                    return
        
        # create new tab
        editor = self.get_editor()
        self.tab_widget.addTab(editor, path.name)

        if not is_new_file:
            editor.setText(path.read_text())
        self.setWindowTitle(path.name)
        self.current_file = path
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)



    def is_binary(self, path: Path) -> bool:
        with open(path, 'rb') as f:
            # null byte is common in binary, but rare in text
            return b'\0' in f.read(1024) 

    # ------------ menu ------------ #

    def set_up_menu(self):
        menu_bar = self.menuBar()

        # ------- file menu ------ #
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+K+O")
        open_folder.triggered.connect(self.open_folder)

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_file_as = file_menu.addAction("Save as")
        save_file_as.setShortcut("Ctrl+Shift+S")
        save_file_as.triggered.connect(self.save_file_as)

        # ------- edit menu ------ #
        edit_menu = menu_bar.addMenu("Edit")

        copy_action = file_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)


    def new_file():...
    def open_file():...
    def open_folder():...
    def save_file():...
    def save_file_as():...
    def copy():...


    # ------------ body ------------ #
    def set_up_body(self):
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Plain)
        self.side_bar.setStyleSheet(f"""
            background-color: {self.side_bar_clr}""")
        side_bar_layout = QHBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        folder_label = QLabel()
        folder_label.setPixmap(QPixmap("./dependencies/icons/folder-icon-blue.svg").scaled(QSize(25, 25)))
        folder_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        folder_label.setFont(self.window_font)
        folder_label.mousePressEvent = self.show_hide_tab
        side_bar_layout.addWidget(folder_label)
        self.side_bar.setLayout(side_bar_layout)

        body.addWidget(self.side_bar)

        self.hsplit = QSplitter(Qt.Horizontal)

        self.tree_frame = QFrame()
        self.tree_frame.setLineWidth(1)
        self.tree_frame.setMaximumWidth(400)
        self.tree_frame.setMinimumWidth(200)
        self.tree_frame.setBaseSize(100, 0)
        self.tree_frame.setContentsMargins(0, 0, 0, 0)
        
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)
        
        self.tree_frame.setStyleSheet("""
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
            """)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("FiraCode", 13))
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.tree_view.customContextMenuRequested.connect(self.tree_view_context_menu)
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # removing header an unwanted file details from explorer
        self.tree_view.setHeaderHidden(True) 
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        tree_frame_layout.addWidget(self.tree_view)
        self.tree_frame.setLayout(tree_frame_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)

        self.hsplit.addWidget(self.tree_frame)
        self.hsplit.addWidget(self.tab_widget)
        body.addWidget(self.hsplit)
        body_frame.setLayout(body)
        self.setCentralWidget(body_frame)



    def tree_view_context_menu(self, pos):...
    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)


    def show_hide_tab(self, _):...



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())



