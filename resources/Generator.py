import random
class Generator:
    """Library for dynamically generating data for automation tests."""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def generate_account_number(self):
        """Generates an 8-digit random prefix and appends 7861580."""
        prefix = f"{random.randint(0, 99999999):08d}"
        return f"{prefix}7861580"

    def get_routing_number_details(self, provided_routing=None):
        """
        If a routing number is provided, returns it.
        If None, falls back to a default valid routing number.
        
        Returns a string.
        """
        
        if not provided_routing:
            return "063201875"
            
        return provided_routing
