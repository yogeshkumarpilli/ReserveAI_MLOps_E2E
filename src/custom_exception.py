import traceback
import sys

class CustomException(Exception):
    def __init__(self, message, error_detail=None):
        self.message = message
        self.error_detail = error_detail
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.message}: {self.error_detail}" if self.error_detail else self.message
    
    def __repr__(self):
        return CustomException.__name__.str()
    

if __name__ == "__main__":
    try:
        a = 1/0
    except Exception as e:
        raise CustomException(e, sys)
    