from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5 import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import re, keyword, types, builtins


class PyCustomLexer(QsciLexerCustom):

    def __init__(self, parent: QObject | None):
        if not isinstance(parent, QsciScintilla):
            raise Exception(f"Expected QsciScintilla, got {type(parent)}")
        super().__init__(parent)
        self.color1 = "#abb2bf"
        self.color2 = "#282c34"
        self.setDefaultColor(QColor(self.color1))
        self.setDefaultPaper(QColor(self.color2))
        self.setDefaultFont(QFont("Consolas", 14))

        self.keyword_list = keyword.kwlist
        self.builtin_function_names = [name for name, obj in vars(builtins).items()
                                       if isinstance(obj, types.BuiltinFunctionType)]

        self.default = 0
        self.keyword = 1
        self.types = 2
        self.string = 3
        self.keyargs = 4
        self.brackets = 5
        self.comments = 6
        self.constants = 7
        self.functions = 8
        self.classes = 9
        self.function_def = 10

        # styles
        self.setColor(QColor(self.color1), self.default)
        self.setColor(QColor("#c678dd"), self.keyword)
        self.setColor(QColor("#56b6c2"), self.types)
        self.setColor(QColor("#98c379"), self.string)
        self.setColor(QColor("#c678dd"), self.keyargs)
        self.setColor(QColor("#c678dd"), self.brackets)
        self.setColor(QColor("#777777"), self.comments)
        self.setColor(QColor("#d19a5e"), self.constants)
        self.setColor(QColor("#61afd1"), self.functions)
        self.setColor(QColor("#c68f55"), self.classes)
        self.setColor(QColor("#61afd1"), self.function_def)

        # paper color
        self.setPaper(QColor(self.color2), self.default)
        self.setPaper(QColor(self.color2), self.keyword)
        self.setPaper(QColor(self.color2), self.types)
        self.setPaper(QColor(self.color2), self.string)
        self.setPaper(QColor(self.color2), self.keyargs)
        self.setPaper(QColor(self.color2), self.brackets)
        self.setPaper(QColor(self.color2), self.comments)
        self.setPaper(QColor(self.color2), self.constants)
        self.setPaper(QColor(self.color2), self.functions)
        self.setPaper(QColor(self.color2), self.classes)
        self.setPaper(QColor(self.color2), self.function_def)

        # font
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.default)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.keyword)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.types)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.string)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.keyargs)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.brackets)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.comments)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.constants)
        # self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.functions)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.classes)
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.function_def)

    def language(self) -> str:
        return "PYCustomLexer"

    def description(self, style: int) -> str:
        match style:
            case self.default:      return "default" 
            case self.keyword:      return "keyword" 
            case self.types:        return "types" 
            case self.string:       return "string" 
            case self.keyargs:      return "keyargs" 
            case self.brackets:     return "brackets" 
            case self.comments:     return "comments" 
            case self.constants:    return "constants" 
            case self.functions:    return "functions" 
            case self.classes:      return "classes" 
            case self.function_def: return "function_def" 

    def get_tokens(self, text) -> list[tuple[str, int]]:
        "Tokenize the text. Returns list of (token_name, byte_count of token_name)"

        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")
        return [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

    def styleText(self, start: int, end: int) -> None:
        self.startStyling(start)
        editor: QsciScintilla = self.parent()

        text = editor.text()[start:end]
        print(text)
        token_list = self.get_tokens(text)
        print(token_list) # "hi again" shows as [", hi, space, again, "]. Is that right?
        
        string_flag = False
        # comment_flag = False ??

        # wtf is this ??
        if start > 0: 
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == self.string:
                string_flag = False

        def next_tok(skip: int = 0) -> tuple[str, int] | None:
            "consume next token"
            if not token_list:
                return None
            if skip != 0 and skip is not None:
                for _ in range(skip - 1):
                    if token_list:
                        token_list.pop(0) # remove and return first item
            return token_list.pop(0) # remove and return first item

        def peek_tok(n: int = 0) -> tuple[str, int]:
            "get next token or default"
            try:
                return token_list[n]
            except IndexError:
                return ('', 0) # evt. rettes fra [''] til (' ', 0) til ('', 0)
            
        def skip_spaces_peek(min_skip: int = None) -> tuple[tuple[str, int], int]:
            "get token after skipping min_skip plus spaces"
            skip = 0
            tok: tuple[str, int] = (' ', 0) # rettet fra (' ') til [' '] til (' ', 0)
            if min_skip is not None:
                skip = min_skip
            while tok[0].isspace():
                tok = peek_tok(skip)
                skip += 1
            return tok, skip
        
        while True:
            curr_token = next_tok()
            if curr_token is None:
                break
            tok_str, tok_len = curr_token

            if string_flag:
                self.setStyling(tok_len, self.string)
                if tok_str == '"' or tok_str == "'":
                    string_flag = False
                continue

            operators = ['+', '-', '*', '/', '%', '!', '&&', '||', '==', '!=', '>',
                         '>=', '<=', '<']
            if tok_str == "class":
                class_name_tok, class_name_len = skip_spaces_peek()
                brac_or_colon, _ = skip_spaces_peek(class_name_len)
                # isidentifier means is valid identifier
                if class_name_tok[0].isidentifier() and brac_or_colon[0] in [':', '(']:
                    self.setStyling(tok_len, self.keyword)
                    _ = next_tok(class_name_len)
                    self.setStyling(class_name_tok[1] + 1, self.classes)
                    continue
                else:
                    self.setStyling(tok_len, self.keyword)
                    continue
            elif tok_str == "def":
                func_name_tok, func_name_len = skip_spaces_peek()
                if func_name_tok[0].isidentifier():
                    self.setStyling(tok_len, self.keyword)
                    _ = next_tok(func_name_len)
                    self.setStyling(func_name_tok[1] + 1, self.function_def)
                    continue
                else:
                    self.setStyling(tok_len, self.keyword)
                    continue
            

            elif tok_str in self.keyword_list:
                self.setStyling(tok_len, self.keyword)
            elif tok_str.isnumeric() or tok_str == 'self':
                self.setStyling(tok_len, self.constants)
            elif tok_str in ['(', ')', '[', ']', '{', '}']:
                self.setStyling(tok_len, self.brackets)
            elif tok_str == '"' or tok_str == "'":
                self.setStyling(tok_len, self.string)
                string_flag = True 
            elif tok_str in self.builtin_function_names or tok_str in operators:
                self.setStyling(tok_len, self.types)
            else:
                self.setStyling(tok_len, self.default)
            
            # missing:
            #     keyargs 
            #     comments 
            #     functions 
            #     function_def 
            # vars

