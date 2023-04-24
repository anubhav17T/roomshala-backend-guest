class CustomException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class CustomExceptionHandler(Exception):
    def __init__(self, message: str, target: str, success: bool, code: int):
        self.message = message
        self.target = target
        self.success = success
        self.code = code


class DatabaseConnectionError(Exception):
    def __init__(self,message:str):
        self.message = message


