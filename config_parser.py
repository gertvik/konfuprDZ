"""
Парсер для учебного конфигурационного языка.
"""
import re
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class TokenType(Enum):
    """Типы токенов."""
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    ARRAY = "ARRAY"
    DICT_START = "DICT_START"
    DICT_END = "DICT_END"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ARROW = "ARROW"
    COMMA = "COMMA"
    LET = "LET"
    EQUALS = "EQUALS"
    CONSTANT_REF = "CONSTANT_REF"
    EOF = "EOF"


class Token:
    """Токен."""
    def __init__(self, type: TokenType, value: Any, position: int):
        self.type = type
        self.value = value
        self.position = position
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.position})"


class Lexer:
    """Лексер для токенизации входного текста."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        """Выбросить ошибку лексического анализа."""
        # Показываем контекст вокруг ошибки
        start = max(0, self.pos - 20)
        end = min(len(self.text), self.pos + 20)
        context = self.text[start:end]
        marker_pos = self.pos - start
        marker = " " * marker_pos + "^"
        raise SyntaxError(f"Lexical error at position {self.pos}: {message}\n  {context}\n  {marker}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Посмотреть символ вперед."""
        if self.pos + offset >= len(self.text):
            return None
        return self.text[self.pos + offset]
    
    def advance(self) -> Optional[str]:
        """Переместиться на следующий символ."""
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        self.pos += 1
        return char
    
    def skip_whitespace(self):
        """Пропустить пробельные символы."""
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1
    
    def read_number(self) -> str:
        """Прочитать число."""
        start_pos = self.pos
        has_digits = False
        
        # Знак минус
        if self.peek() == '-':
            self.advance()
        
        # Проверяем начинается ли с точки
        starts_with_dot = self.peek() == '.'
        
        # Целая часть
        if self.peek() and self.peek().isdigit():
            has_digits = True
            while self.peek() and self.peek().isdigit():
                self.advance()
        
        # Дробная часть
        if self.peek() == '.':
            self.advance()
            if self.peek() and self.peek().isdigit():
                has_digits = True
                while self.peek() and self.peek().isdigit():
                    self.advance()
            elif starts_with_dot and not has_digits:
                # Число начинается с точки, но после точки нет цифр
                self.error("Invalid number format: expected digits after decimal point")
        
        # Проверяем что было хотя бы одно число
        if not has_digits:
            self.error("Invalid number format: expected at least one digit")
        
        # Экспонента
        if self.peek() and self.peek().lower() == 'e':
            self.advance()
            if self.peek() in ('-', '+'):
                self.advance()
            if not (self.peek() and self.peek().isdigit()):
                self.error("Invalid exponent in number: expected digits after 'e'")
            while self.peek() and self.peek().isdigit():
                self.advance()
        
        return self.text[start_pos:self.pos]
    
    def read_string(self) -> str:
        """Прочитать строку в кавычках."""
        if self.peek() != '"':
            self.error("Expected string quote")
        
        self.advance()  # Пропустить открывающую кавычку
        start_pos = self.pos
        result = []
        
        while self.pos < len(self.text):
            char = self.advance()
            if char == '"':
                return ''.join(result)
            elif char == '\\':
                # Обработка escape-последовательностей
                next_char = self.advance()
                if next_char == 'n':
                    result.append('\n')
                elif next_char == 't':
                    result.append('\t')
                elif next_char == '\\':
                    result.append('\\')
                elif next_char == '"':
                    result.append('"')
                else:
                    result.append('\\')
                    result.append(next_char)
            else:
                result.append(char)
        
        self.error("Unclosed string")
    
    def read_identifier(self) -> str:
        """Прочитать идентификатор."""
        start_pos = self.pos
        
        # Первый символ: _ или A-Z (по спецификации)
        # Но для практичности разрешаем и a-z для имен в словарях
        char = self.peek()
        if char and (char == '_' or ('A' <= char <= 'Z') or ('a' <= char <= 'z')):
            self.advance()
        else:
            self.error(f"Invalid identifier start: {char}")
        
        # Остальные символы: _a-zA-Z0-9
        while self.pos < len(self.text):
            char = self.peek()
            if char and (char == '_' or ('a' <= char <= 'z') or 
                        ('A' <= char <= 'Z') or ('0' <= char <= '9')):
                self.advance()
            else:
                break
        
        return self.text[start_pos:self.pos]
    
    def tokenize(self) -> List[Token]:
        """Токенизировать входной текст."""
        self.tokens = []
        self.pos = 0
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if self.pos >= len(self.text):
                break
            
            char = self.peek()
            
            # Число
            if char == '-' or char.isdigit() or char == '.':
                num_str = self.read_number()
                try:
                    if 'e' in num_str.lower() or 'E' in num_str:
                        value = float(num_str)
                    elif '.' in num_str:
                        value = float(num_str)
                    else:
                        value = int(num_str)
                    self.tokens.append(Token(TokenType.NUMBER, value, self.pos - len(num_str)))
                except ValueError:
                    self.error(f"Invalid number: {num_str}")
            
            # Строка
            elif char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, self.pos - len(value) - 2))
            
            # Константная ссылка
            elif char == '#' and self.peek(1) == '{':
                self.advance()  # #
                self.advance()  # {
                start_pos = self.pos
                while self.pos < len(self.text) and self.peek() != '}':
                    self.advance()
                if self.pos >= len(self.text):
                    self.error("Unclosed constant reference")
                name = self.text[start_pos:self.pos]
                self.advance()  # }
                self.tokens.append(Token(TokenType.CONSTANT_REF, name, start_pos - 2))
            
            # Ключевые слова и операторы
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.DICT_START, '[', self.pos - 1))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.DICT_END, ']', self.pos - 1))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', self.pos - 1))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', self.pos - 1))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', self.pos - 1))
            elif char == '=':
                self.advance()
                if self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '=>', self.pos - 2))
                else:
                    self.tokens.append(Token(TokenType.EQUALS, '=', self.pos - 1))
            elif char == '>':
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, '=>', self.pos - 1))
            
            # Ключевые слова и идентификаторы
            elif char == '_' or ('A' <= char <= 'Z') or ('a' <= char <= 'z'):
                # Проверяем ключевые слова
                if char == 'a' and self.pos + 5 <= len(self.text) and self.text[self.pos:self.pos+5] == "array":
                    # Проверяем, что это отдельное слово
                    if self.pos + 5 >= len(self.text) or not (self.text[self.pos+5].isalnum() or self.text[self.pos+5] == '_'):
                        self.pos += 5
                        self.tokens.append(Token(TokenType.ARRAY, "array", self.pos - 5))
                    else:
                        ident = self.read_identifier()
                        self.tokens.append(Token(TokenType.IDENTIFIER, ident, self.pos - len(ident)))
                elif char == 'l' and self.pos + 3 <= len(self.text) and self.text[self.pos:self.pos+3] == "let":
                    # Проверяем, что это отдельное слово
                    if self.pos + 3 >= len(self.text) or not (self.text[self.pos+3].isalnum() or self.text[self.pos+3] == '_'):
                        self.pos += 3
                        self.tokens.append(Token(TokenType.LET, "let", self.pos - 3))
                    else:
                        ident = self.read_identifier()
                        self.tokens.append(Token(TokenType.IDENTIFIER, ident, self.pos - len(ident)))
                else:
                    # Обычный идентификатор
                    ident = self.read_identifier()
                    self.tokens.append(Token(TokenType.IDENTIFIER, ident, self.pos - len(ident)))
            
            else:
                self.error(f"Unexpected character: {char}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.pos))
        return self.tokens


class Parser:
    """Парсер для разбора токенов в AST."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.constants: Dict[str, Any] = {}
    
    def error(self, message: str):
        """Выбросить ошибку синтаксического анализа."""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            # Показываем предыдущие токены для контекста
            context_tokens = []
            start = max(0, self.pos - 3)
            for i in range(start, min(self.pos + 1, len(self.tokens))):
                if i < len(self.tokens):
                    t = self.tokens[i]
                    if t.type != TokenType.EOF:
                        context_tokens.append(f"{t.type.name}({t.value})")
            context = " ".join(context_tokens)
            raise SyntaxError(f"Syntax error at position {token.position}: {message}\n  Context: {context}")
        else:
            raise SyntaxError(f"Syntax error: {message}")
    
    def peek(self) -> Token:
        """Посмотреть текущий токен."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def advance(self) -> Token:
        """Перейти к следующему токену."""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.tokens[-1]  # EOF
    
    def expect(self, token_type: TokenType) -> Token:
        """Ожидать токен определенного типа."""
        token = self.peek()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()
    
    def parse_value(self) -> Any:
        """Парсинг значения."""
        token = self.peek()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        
        elif token.type == TokenType.STRING:
            self.advance()
            return token.value
        
        elif token.type == TokenType.ARRAY:
            return self.parse_array()
        
        elif token.type == TokenType.DICT_START:
            return self.parse_dict()
        
        elif token.type == TokenType.CONSTANT_REF:
            self.advance()
            name = token.value
            if name not in self.constants:
                self.error(f"Undefined constant: {name}")
            return self.constants[name]
        
        elif token.type == TokenType.IDENTIFIER:
            # Поддержка булевых значений true/false
            if token.value == "true":
                self.advance()
                return True
            elif token.value == "false":
                self.advance()
                return False
            else:
                self.error(f"Unexpected identifier in value: {token.value}")
        
        else:
            self.error(f"Unexpected token in value: {token.type.name}")
    
    def parse_array(self) -> List[Any]:
        """Парсинг массива."""
        self.expect(TokenType.ARRAY)
        self.expect(TokenType.LPAREN)
        
        values = []
        
        # Пустой массив
        if self.peek().type == TokenType.RPAREN:
            self.advance()
            return values
        
        # Парсим значения
        while True:
            value = self.parse_value()
            values.append(value)
            
            if self.peek().type == TokenType.COMMA:
                self.advance()
            elif self.peek().type == TokenType.RPAREN:
                self.advance()
                break
            else:
                self.error("Expected comma or closing parenthesis")
        
        return values
    
    def skip_whitespace_in_text(self):
        """Пропустить пробелы (для парсера)."""
        pass  # Пробелы уже пропущены лексером
    
    def parse_dict(self) -> Dict[str, Any]:
        """Парсинг словаря."""
        self.expect(TokenType.DICT_START)
        
        result = {}
        
        while True:
            self.skip_whitespace_in_text()
            
            if self.peek().type == TokenType.DICT_END:
                self.advance()
                break
            
            # Имя
            name_token = self.expect(TokenType.IDENTIFIER)
            name = name_token.value
            
            # =>
            self.expect(TokenType.ARROW)
            
            # Значение
            value = self.parse_value()
            result[name] = value
            
            # Запятая или конец
            if self.peek().type == TokenType.COMMA:
                self.advance()
            elif self.peek().type == TokenType.DICT_END:
                continue
            else:
                self.error("Expected comma or closing bracket")
        
        return result
    
    def parse_let(self):
        """Парсинг объявления константы."""
        self.expect(TokenType.LET)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        self.expect(TokenType.EQUALS)
        value = self.parse_value()
        self.constants[name] = value
    
    def parse(self) -> Any:
        """Парсинг всего входного текста."""
        result = None
        
        while self.pos < len(self.tokens):
            token = self.peek()
            
            if token.type == TokenType.EOF:
                break
            
            elif token.type == TokenType.LET:
                self.parse_let()
            
            else:
                # Основное значение (корневой элемент)
                if result is None:
                    result = self.parse_value()
                else:
                    self.error("Multiple root values")
        
        return result if result is not None else {}


