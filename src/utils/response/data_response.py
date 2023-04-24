class ResponseModel(object):
    def __init__(self,message:str,code:int,success:bool,data:dict):
        self.message = message
        self.success = success
        self.code = code
        self.data = data

    def response(self):
        return {"data":self.data,
                "message":self.message,
                "code":self.code,
                "success":self.success
                }