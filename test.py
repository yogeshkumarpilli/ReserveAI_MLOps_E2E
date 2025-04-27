from src.logger import get_logger
from src.custom_exception import CustomException
import sys

logger = get_logger(__name__)

def divide_numbers(a, b):
    try:
        result = a / b
        logger.info(f"Division successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in division: {e}")
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        logger.info("Starting main function")
        divide_numbers(10, 0)
    except CustomException as e:
        logger.error(str(e))


