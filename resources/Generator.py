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
        If a routing number is provided, queries the API for its details.
        If None, generates mathematically valid routing numbers and tests them 
        against the API up to 10 times until a valid one is found.
        If 10 attempts fail, falls back to a default valid routing number.
        
        Returns a dictionary: {'routing': str, 'bank': str, 'city': str, 'zip': str}
        """
        import requests
        
        url = "https://bank.codes/us-routing-number-checker/"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        def fetch_details(rtno):
            try:
                payload = {'routing': rtno}
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                html = response.text
                
                # Check if it was invalid
                if "does not exist in our database" in html:
                    return None
                    
                # Parsing Bank
                bank = "Unknown"
                if "<th>Bank</th>" in html or "<th scope='row'>Bank</th>" in html:
                    try:
                        parts = html.split(">Bank</th>")
                        if len(parts) > 1:
                            td_part = parts[1].split("<td>")[1]
                            bank = td_part.split("</td>")[0].strip()
                    except IndexError:
                        pass
                
                # Parsing City
                city = "Unknown"
                if "<th>City</th>" in html or "<th scope='row'>City</th>" in html:
                    try:
                        parts = html.split(">City</th>")
                        if len(parts) > 1:
                            td_part = parts[1].split("<td>")[1]
                            city = td_part.split("</td>")[0].strip()
                    except IndexError:
                        pass
                        
                # Parsing ZIP
                zip_code = "Unknown"
                if "<th>ZIP</th>" in html or "<th scope='row'>ZIP</th>" in html:
                    try:
                        parts = html.split(">ZIP</th>")
                        if len(parts) > 1:
                            td_part = parts[1].split("<td>")[1]
                            zip_code = td_part.split("</td>")[0].strip()
                    except IndexError:
                        pass
                        
                return {
                    'routing': rtno,
                    'bank': bank,
                    'city': city,
                    'zip': zip_code
                }
            except requests.exceptions.RequestException:
                return None

        # 1. If user provided a routing number, fetch and return its details.
        if provided_routing:
            details = fetch_details(provided_routing)
            if details:
                return details
            return {'routing': provided_routing, 'bank': 'Unknown', 'city': 'Unknown', 'zip': 'Unknown'}

        # 2. If no routing provided, try generating up to 10 times.
        for attempt in range(10):
            # Generate mathematically valid RTNO
            prefix = f"{random.randint(1, 12):02d}"
            middle = f"{random.randint(0, 999999):06d}"
            eight_digits = prefix + middle
            weights = [3, 7, 1, 3, 7, 1, 3, 7]
            checksum_base = sum(int(digit) * weight for digit, weight in zip(eight_digits, weights))
            checksum = (10 - (checksum_base % 10)) % 10
            test_rtno = f"{eight_digits}{checksum}"
            
            details = fetch_details(test_rtno)
            if details:
                return details

        # 3. Fallback if all 10 generation attempts fail.
        fallback_rtno = "063201875"
        details = fetch_details(fallback_rtno)
        if details:
            return details
            
        return {
            'routing': fallback_rtno,
            'bank': 'Unknown',
            'city': 'Unknown',
            'zip': 'Unknown'
        }
