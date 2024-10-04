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
hex_address = '0x64e51387c629f7852195fde79cc7c5119c7ee4bbc0da3a7f3e9ee926d6fd955f'
ss58_address = convert_hex_to_ss58(hex_address)
print(ss58_address) 



