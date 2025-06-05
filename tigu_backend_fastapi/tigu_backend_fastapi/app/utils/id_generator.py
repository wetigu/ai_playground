"""
Simple ID generator for BIGINT fields
"""
import time
import random

def generate_id():
    """
    Generate a unique BIGINT ID using timestamp and random component
    Format: timestamp (seconds) + random 6-digit number
    """
    timestamp = int(time.time())
    random_part = random.randint(100000, 999999)
    return int(f"{timestamp}{random_part}")

def generate_company_code():
    """
    Generate a unique company code
    """
    timestamp = int(time.time())
    random_part = random.randint(1000, 9999)
    return f"COMP{timestamp}{random_part}" 