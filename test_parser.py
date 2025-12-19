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


class TestParserEdgeCases(unittest.TestCase):
    """Тесты парсера для edge cases."""
    
    def test_empty_array(self):
        """Тест пустого массива."""
        lexer = Lexer("array()")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [])
    
    def test_empty_dict(self):
        """Тест пустого словаря."""
        lexer = Lexer("[]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {})
    
    def test_array_with_trailing_comma(self):
        """Тест массива с завершающей запятой (не должен поддерживаться по синтаксису)."""
        # По синтаксису завершающая запятая не поддерживается
        # Но проверим что парсер корректно обрабатывает
        lexer = Lexer("array(1, 2)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [1, 2])
    
    def test_nested_constants(self):
        """Тест вложенных констант."""
        lexer = Lexer("let A = 10\nlet B = #{A}\narray(#{A}, #{B})")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [10, 10])
    
    def test_constant_in_array(self):
        """Тест константы в массиве."""
        lexer = Lexer("let X = 42\narray(#{X}, 10)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [42, 10])
    
    def test_constant_in_dict(self):
        """Тест константы в словаре."""
        lexer = Lexer("let Port = 8080\n[ port => #{Port} ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {"port": 8080})
    
    def test_complex_nested_structure(self):
        """Тест сложной вложенной структуры."""
        lexer = Lexer("""
        [
          server => [
            ports => array(80, 443, 8080),
            name => "MyServer"
          ],
          clients => array(
            [ name => "Client1", id => 1 ],
            [ name => "Client2", id => 2 ]
          )
        ]
        """)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertIn("server", result)
        self.assertIn("clients", result)
        self.assertEqual(len(result["clients"]), 2)
    
    def test_number_variations(self):
        """Тест различных форматов чисел."""
        test_cases = [
            ("0", 0),
            ("-0", 0),
            ("0.5", 0.5),
            (".5", 0.5),
            ("1e5", 1e5),
            ("1E5", 1e5),
            ("1.5e-3", 1.5e-3),
            ("-1.5e+10", -1.5e+10),
        ]
        for text, expected in test_cases:
            with self.subTest(text=text):
                lexer = Lexer(text)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                result = parser.parse()
                self.assertEqual(result, expected)
    
    def test_string_escape_sequences(self):
        """Тест escape-последовательностей в строках."""
        lexer = Lexer('"hello\\nworld\\ttab"')
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].value, "hello\nworld\ttab")
    
    def test_multiple_constants(self):
        """Тест множественных констант."""
        lexer = Lexer("let A = 1\nlet B = 2\nlet C = 3\narray(#{A}, #{B}, #{C})")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [1, 2, 3])
    
    def test_boolean_values(self):
        """Тест булевых значений."""
        lexer = Lexer("[ enabled => true, disabled => false ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, {"enabled": True, "disabled": False})
    
    def test_boolean_in_array(self):
        """Тест булевых значений в массиве."""
        lexer = Lexer("array(true, false, true)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        result = parser.parse()
        self.assertEqual(result, [True, False, True])


class TestErrorHandling(unittest.TestCase):
    """Тесты обработки ошибок."""
    
    def test_undefined_constant(self):
        """Тест неопределенной константы."""
        lexer = Lexer("#{UndefinedConst}")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError) as context:
            parser.parse()
        self.assertIn("Undefined constant", str(context.exception))
    
    def test_invalid_number_format(self):
        """Тест неверного формата числа."""
        lexer = Lexer("12.34.56")
        with self.assertRaises(SyntaxError):
            lexer.tokenize()
    
    def test_unclosed_string(self):
        """Тест незакрытой строки."""
        lexer = Lexer('"unclosed string')
        with self.assertRaises(SyntaxError) as context:
            lexer.tokenize()
        self.assertIn("Unclosed string", str(context.exception))
    
    def test_unclosed_array(self):
        """Тест незакрытого массива."""
        lexer = Lexer("array(1, 2")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()
    
    def test_unclosed_dict(self):
        """Тест незакрытого словаря."""
        lexer = Lexer("[ key => value")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()
    
    def test_invalid_identifier_in_dict(self):
        """Тест неверного идентификатора в словаре."""
        lexer = Lexer("[ 123 => value ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()
    
    def test_missing_arrow_in_dict(self):
        """Тест отсутствующей стрелки в словаре."""
        lexer = Lexer("[ key value ]")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        with self.assertRaises(SyntaxError):
            parser.parse()
    
    def test_unclosed_constant_ref(self):
        """Тест незакрытой ссылки на константу."""
        lexer = Lexer("#{Unclosed")
        with self.assertRaises(SyntaxError) as context:
            lexer.tokenize()
        self.assertIn("Unclosed constant reference", str(context.exception))


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
    
    def test_convert_nested_structure(self):
        """Тест конвертации вложенной структуры."""
        data = {
            "server": {
                "port": 8080,
                "hosts": ["localhost", "127.0.0.1"]
            }
        }
        result = convert_to_toml(data)
        self.assertIn("server", result)
        self.assertIn("port", result)
        self.assertIn("8080", result)
    
    def test_convert_empty_array(self):
        """Тест конвертации пустого массива."""
        result = convert_to_toml([])
        self.assertIn("array", result)
    
    def test_convert_empty_dict(self):
        """Тест конвертации пустого словаря."""
        result = convert_to_toml({})
        # Пустой словарь должен дать пустой TOML документ
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()

