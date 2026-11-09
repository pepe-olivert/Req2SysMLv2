from .LoggingParser import LoggingParser
from .SysMLv2.SysMLv2Lexer import SysMLv2Lexer  
from .SysMLv2.SysMLv2Parser import SysMLv2Parser

class SysMLv2LoggingParser(LoggingParser):
    """Parser for validatign SysMLv2 specifically"""
    
    def get_lexer_parser_classes(self):
        return SysMLv2Lexer, SysMLv2Parser
