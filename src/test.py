import sys
from src.exception import CustomException

def divide_the_number() -> float:
    a = 10
    b = 5
    result = a/b
    return result
if __name__ == "__main__":
    try:
        result = divide_the_number()
        print(result)
    except Exception as e:
        raise CustomException(e,sys)