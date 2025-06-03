#!/usr/bin/env python3
"""
Test the customer parsing function with real data examples
"""

import re

def parse_customer_data(customer_string):
    """Parse customer data from the specific format: 'Name t: phone m: mobile e: email'"""
    if not customer_string or customer_string.strip() == '-':
        return None
    
    customer_info = {
        'name': '',
        'phone': '',
        'email': ''
    }
    
    try:
        # Split by common patterns
        parts = customer_string.strip()
        
        # Extract name (everything before 't:' or first contact info)
        if ' t:' in parts:
            name_part = parts.split(' t:')[0].strip()
        elif ' m:' in parts:
            name_part = parts.split(' m:')[0].strip()
        elif ' e:' in parts:
            name_part = parts.split(' e:')[0].strip()
        else:
            name_part = parts
        
        customer_info['name'] = name_part
        
        # Extract phone numbers (look for patterns like 'm: 07...' or 't: 8203...')
        
        # Mobile phone pattern (m: followed by number)
        mobile_match = re.search(r'm:\s*([0-9\s]+)', parts)
        if mobile_match:
            customer_info['phone'] = mobile_match.group(1).strip()
        
        # If no mobile, try landline (t: followed by number)
        if not customer_info['phone']:
            landline_match = re.search(r't:\s*([0-9\s]+)', parts)
            if landline_match:
                customer_info['phone'] = landline_match.group(1).strip()
        
        # Extract email (e: followed by email)
        email_match = re.search(r'e:\s*([^\s]+@[^\s]+)', parts)
        if email_match:
            customer_info['email'] = email_match.group(1).strip()
        
        # Clean up phone number (remove extra spaces)
        if customer_info['phone']:
            customer_info['phone'] = re.sub(r'\s+', '', customer_info['phone'])
        
        return customer_info
        
    except Exception as e:
        print(f"Error parsing customer data '{customer_string}': {e}")
        return {'name': customer_string.strip(), 'phone': '', 'email': ''}

# Test with your real data examples
test_cases = [
    "Ms Jo Newton + Lauren Newton t: m: 07939887633 e:",
    "Christy Hadjipateras t: m: 07793093414 e:",
    "Mrs Sheridan t: 8203 0611 m: 07973224728 nikki e: nikkihiller@hotmail.co.uk",
    "Mr Andrew Gartner t: m: 07966140335 e:",
    "Mr Scot Murphy t: m: 07950214811 e:",
    "-",
    ""
]

print("Testing customer data parsing:")
print("=" * 60)

for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest {i}: '{test_case}'")
    result = parse_customer_data(test_case)
    if result:
        print(f"  Name: '{result['name']}'")
        print(f"  Phone: '{result['phone']}'")
        print(f"  Email: '{result['email']}'")
    else:
        print("  Result: None (empty/dash)")
