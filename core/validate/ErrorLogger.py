from antlr4.error.ErrorListener import ErrorListener

class ErrorLoggerClass(ErrorListener):
    """This class keeps track of every error found in the SysML v2 code"""
    def __init__(self):
        self.__errors = []  # List to collect errors
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Store each error as a formatted string
        error_message = f"Syntax error at line {line}, column {column}: {msg}"
        self.__errors.append(error_message)
    
    def get_errors_string(self):
        # Join all errors into a single string, separating them by newlines
        return "\n".join(self.__errors)
