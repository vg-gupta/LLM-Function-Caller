import logging

logging.basicConfig(filename="logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def log_function_call(user_query, function_name):
    logging.info(f"User Query: {user_query} → Function: {function_name}")
