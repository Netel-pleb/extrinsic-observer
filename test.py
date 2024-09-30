from substrateinterface.utils.ss58 import ss58_encode

def convert_hex_to_ss58(hex_address):
    # Remove the '0x' prefix if present
    if hex_address.startswith('0x'):
        hex_address = hex_address[2:]
    
    # Convert hex to bytes
    address_bytes = bytes.fromhex(hex_address)
    
    # Encode to SS58 address
    ss58_address = ss58_encode(address_bytes)
    
    return ss58_address

# Example usage
hex_address = '0x8061a268220ed66047ab2f5695efa03c5b30ef4a873d97df9969fa690a5feb11'
ss58_address = convert_hex_to_ss58(hex_address)
print(ss58_address)  # Expected Output: 5Ey2zNCjGLvYJygfqUjKQd3ovS46dEjmtbzRbfezmRUzXx45