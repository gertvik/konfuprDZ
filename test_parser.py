"""
Тесты для парсера конфигурационного языка.
"""
import unittest
from config_parser import Lexer, Parser
from toml_converter import convert_to_toml


class TestLexer(unittest.TestCase):
    """Тесты лексера."""
    
    def test_number_integer(self):
        """Тест целого числа."""
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "NUMBER")
        self.assertEqual(tokens[0].value, 42)
    
    def test_number_float(self):
        """Тест числа с плавающей точкой."""
        lexer = Lexer("3.14")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "NUMBER")
        self.assertEqual(tokens[0].value, 3.14)
    
    def test_number_negative(self):
        """Тест отрицательного числа."""
        lexer = Lexer("-10")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "NUMBER")
        self.assertEqual(tokens[0].value, -10)
    
    def test_number_scientific(self):
        """Тест числа в научной нотации."""
        lexer = Lexer("1.5e10")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "NUMBER")
        self.assertEqual(tokens[0].value, 1.5e10)
    
    def test_string(self):
        """Тест строки."""
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "STRING")
        self.assertEqual(tokens[0].value, "hello world")
    
    def test_identifier(self):
        """Тест идентификатора."""
        lexer = Lexer("MyVar_123")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "IDENTIFIER")
        self.assertEqual(tokens[0].value, "MyVar_123")
    
    def test_array_keyword(self):
        """Тест ключевого слова array."""
        lexer = Lexer("array")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "ARRAY")
    
    def test_let_keyword(self):
        """Тест ключевого слова let."""
        lexer = Lexer("let")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "LET")
    
    def test_constant_ref(self):
        """Тест ссылки на константу."""
        lexer = Lexer("#{MyConst}")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type.value, "CONSTANT_REF")
        self.assertEqual(tokens[0].value, "MyConst")


class TestParser(unittest.TestCase):
    """Тесты парсера."""
    
    def test_parse_number(self):
        """Тест парсинга числа."""
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, 42)
    
    def test_parse_string(self):
        """Тест парсинга строки."""
        lexer = Lexer('"hello"')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, "hello")
    
    def test_parse_array_simple(self):
        """Тест парсинга простого массива."""
        lexer = Lexer("array(1, 2, 3)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [1, 2, 3])
    
    def test_parse_array_mixed(self):
        """Тест парсинга массива с разными типами."""
        lexer = Lexer('array(1, "two", 3.0)')
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [1, "two", 3.0])
    
    def test_parse_dict_simple(self):
        """Тест парсинга простого словаря."""
        lexer = Lexer("[ key => value ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {"key": "value"})
    
    def test_parse_dict_multiple(self):
        """Тест парсинга словаря с несколькими ключами."""
        lexer = Lexer("[ name => \"John\", age => 30 ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {"name": "John", "age": 30})
    
    def test_parse_let(self):
        """Тест парсинга объявления константы."""
        lexer = Lexer("let MyConst = 42")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        self.assertEqual(parser.constants["MyConst"], 42)
    
    def test_parse_constant_ref(self):
        """Тест парсинга ссылки на константу."""
        lexer = Lexer("let X = 10\n#{X}")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, 10)
    
    def test_parse_nested_dict(self):
        """Тест парсинга вложенного словаря."""
        lexer = Lexer("[ outer => [ inner => value ] ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {"outer": {"inner": "value"}})
    
    def test_parse_nested_array(self):
        """Тест парсинга вложенного массива."""
        lexer = Lexer("array(array(1, 2), array(3, 4))")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [[1, 2], [3, 4]])


class TestConverter(unittest.TestCase):
    """Тесты конвертера в TOML."""
    
    def test_convert_number(self):
        """Тест конвертации числа."""
        result = convert_to_toml(42)
        self.assertIn("42", result)
    
    def test_convert_string(self):
        """Тест конвертации строки."""
        result = convert_to_toml("hello")
        self.assertIn("hello", result)
    
    def test_convert_dict(self):
        """Тест конвертации словаря."""
        result = convert_to_toml({"key": "value"})
        self.assertIn("key", result)
        self.assertIn("value", result)
    
    def test_convert_array(self):
        """Тест конвертации массива."""
        result = convert_to_toml([1, 2, 3])
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)


if __name__ == "__main__":
    unittest.main()

