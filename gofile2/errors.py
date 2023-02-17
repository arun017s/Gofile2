# Original Author: Codec04
# Re-built by Itz-fork
# Project: Gofile2

class InvalidToken(Exception):
    def __init__(self) -> None:
        Exception.__init__(
            self, "Token is required for this action but it's None")

class JobFailed(Exception):
    def __init__(self, e) -> None:
        Exception.__init__(
            self, f"Error Happend: {e} \n\nReport this at ----> https://github.com/Itz-fork/Gofile2/issues")

class ResponseError(Exception):
    pass

class InvalidPath(Exception):
    pass

class InvalidOption(Exception):
    def __init__(self, opt) -> None:
        Exception.__init__(self, f"{opt} doesn't appear to be a valid option")
