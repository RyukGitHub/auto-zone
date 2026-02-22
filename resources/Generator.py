import random

class Generator:
    """Library for dynamically generating data for automation tests."""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def generate_account_number(self):
        """Generates an 8-digit random prefix and appends 7861580."""
        prefix = f"{random.randint(0, 99999999):08d}"
        return f"{prefix}7861580"

    def generate_routing_number(self):
        """
        Generates a valid 9-digit US routing number using the modulus 10 
        checksum algorithm.
        """
        # Valid routing numbers typically start with 01-12 for commercial banks
        prefix = f"{random.randint(1, 12):02d}"
        middle = f"{random.randint(0, 999999):06d}"
        eight_digits = prefix + middle
        
        # Applying routing transit number checksum multipliers: 3, 7, 1
        weights = [3, 7, 1, 3, 7, 1, 3, 7]
        checksum_base = sum(int(digit) * weight for digit, weight in zip(eight_digits, weights))
        checksum = (10 - (checksum_base % 10)) % 10
        
        return f"{eight_digits}{checksum}"
