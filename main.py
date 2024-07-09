from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import sys, os
from pathlib import Path
from editor import Editor

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

    def get_side_bar_icon(self, path, name) -> QLabel:
        label = QLabel()
        label.setPixmap(QPixmap(path).scaled(QSize(25, 25)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        # label.mousePressEvent = self.show_hide_tab
        label.mousePressEvent = lambda e: self.show_hide_tab(e, name)
        return label

    def make_editor(self) -> Editor:
        return Editor(self.window_font)

    def set_new_tab(self, path: Path, is_new_file=False):
        editor = self.make_editor()
        if is_new_file:
            self.tab_widget.addTab(editor, "untitled")
            self.setWindowTitle("intitled")
            self.statusBar().showMessage("Opened untitled")
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
            self.current_file = None
            return
        
        if not path.is_file():
            return
        if self.is_binary(path):
            self.statusBar().showMessage("Cannot open binary file")
            return

        # check if file is already open        
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == path.name:
                self.tab_widget.setCurrentIndex(i)
                self.current_file = path
                return
        
        # create new tab
        self.tab_widget.addTab(editor, path.name)
        editor.setText(path.read_text())
        self.setWindowTitle(path.name)
        self.current_file = path
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)


    def get_editor(self) -> QsciScintilla | None:
        editor = self.tab_widget.currentWidget()
        if editor is not None and not isinstance(editor, QsciScintilla):
            raise Exception(f"expected QsciScintilla or None, found {type(editor)}")
        return editor


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

        file_menu.addSeparator()

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save as")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        # ------- edit menu ------ #
        edit_menu = menu_bar.addMenu("Edit")

        copy_action = file_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)


    def new_file(self):
        self.set_new_tab(None, is_new_file=True)


    def open_file(self):
        ops = QFileDialog.Options()
        ops |= QFileDialog.DontUseNativeDialog
        # add support for opening mulple files later
        new_file, _ = QFileDialog.getOpenFileName(self, 
            "Pick A File", "", "All Files (*);;Python Files (*.py)",
            options=ops)
        if new_file == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)
        

    def open_folder(self):
        ops = QFileDialog.Options()
        ops |= QFileDialog.DontUseNativeDialog
        new_folder = QFileDialog.getExistingDirectory(self, 
            "Pick A Folder", "", options=ops)
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(f"Opened {new_folder}", 2000)

        


    def save_file(self):
        if self.current_file is None:
            self.statusBar().showMessage("No File Selected", 2000)
            return 
        if self.current_file is None and self.tab_widget.count() > 0:
            self.save_as()

        editor = self.get_editor()
        if editor is None:
            self.statusBar().showMessage("No File Selected", 2000)
            return
        self.current_file.write_text(editor.text()) # doesnt recognize text
        self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)

    def save_as(self):
        # requires user to remember specifying the extension
        editor = self.get_editor()
        if editor is None:
            self.statusBar().showMessage("No File Selected", 2000)
            return
        file_path = QFileDialog.getSaveFileName(self, "Save As", os.getcwd())[0]
        if file_path == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        path = Path(file_path)
        path.write_text(editor.text())
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def copy(self):
        editor = self.get_editor()
        if editor is None:
            self.statusBar().showMessage("No File Selected", 2000)
            return
        editor.copy()



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

        folder_label = self.get_side_bar_icon(
            "./dependencies/icons/folder-icon-blue.svg", "folder-icon")
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
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.hsplit.addWidget(self.tree_frame)
        self.hsplit.addWidget(self.tab_widget)
        body.addWidget(self.hsplit)
        body_frame.setLayout(body)
        self.setCentralWidget(body_frame)



    def tree_view_context_menu(self, pos):
        ...

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)


    def show_hide_tab(self, event: QEvent, type_):
        self.tree_frame.setVisible(not self.tree_frame.isVisible())

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())



