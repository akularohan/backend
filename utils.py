import random
import string

def generate_room_code() -> str:
    """Generate a random 5-character alphanumeric room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
