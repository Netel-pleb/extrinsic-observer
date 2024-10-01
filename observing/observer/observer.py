# import pytz
# from datetime import datetime
# from substrateinterface.base import SubstrateInterface
# import bittensor as bt


# def setup_substrate_interface():
#     """
#     Initializes and returns a SubstrateInterface object configured to connect to a specified WebSocket URL.
#     This interface will be used to interact with the blockchain.
#     """
#     return SubstrateInterface(
#         url="wss://archive.chain.opentensor.ai:443/",
#         ss58_format=42,
#         use_remote_preset=True,
#     )

# def get_block_data(substrate, block_number):
#     """
#     Retrieves block data and associated events from the blockchain for a given block number.
    
#     Parameters:
#     substrate (SubstrateInterface): The interface used to interact with the blockchain.
#     block_number (int): The block number to retrieve data for.

#     Returns:
#     tuple: Contains the block data, events, and block hash.
#     """
#     block_hash = substrate.get_block_hash(block_id=block_number)
#     print(block_hash)
#     block = substrate.get_block(block_hash=block_hash)
#     events = substrate.get_events(block_hash=block_hash)
#     return block, events

# def extract_block_timestamp(extrinsics):
#     """
#     Extracts the timestamp from a list of extrinsics by identifying the 'set' function call within the 'Timestamp' module.

#     Parameters:
#     extrinsics (list): A list of extrinsic objects from which to extract the timestamp.

#     Returns:
#     datetime: The extracted timestamp in UTC, or None if not found.
#     """
#     for extrinsic in extrinsics:
#         extrinsic_value = getattr(extrinsic, 'value', None)
#         if extrinsic_value and 'call' in extrinsic_value:
#             call = extrinsic_value['call']
#             if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
#                 return datetime.fromtimestamp(call['call_args'][0]['value'] / 1000, tz=pytz.UTC)
#     return None

# def check_schedule_swap_coldkey(extrinsics):

#     for idx, extrinsic in enumerate(extrinsics):
#         extrinsic_value = getattr(extrinsic, 'value', None)
#         if not extrinsic_value:
#             continue
#         if extrinsic_value and 'call' in extrinsic_value:
#             call = extrinsic_value['call']
#             if call['call_function'] == 'schedule_swap_coldkey' and call['call_module'] == 'SubtensorModule':
#                 return idx
#     return -1

# def process_swap_extrinsics(extrinsic_events):
#     """
#     Processes each extrinsic in the block, extracting relevant details and storing them in the database.
#     Also associates each extrinsic with its corresponding events and success status.

#     Parameters:
#     extrinsics (list): A list of extrinsic objects.
#     events (list): A list of event objects associated with the block.
#     block_instance (Block): The Block instance to which these extrinsics belong.
#     block_number (int): The block number.
#     """
#     for event in extrinsic_events:
#         event_value = getattr(event, 'value', None)
#         if event_value['event_id'] == 'ColdkeySwapScheduled':
#             old_coldkey = event_value['attributes']['old_coldkey']
#             new_coldkey = event_value['attributes']['new_coldkey']
#             execution_block = event_value['attributes']['execution_block']
#     return old_coldkey, new_coldkey, execution_block

# def check_success(events, idx):

#     extrinsic_events = []
#     extrinsic_success = False
#     for event in events:
#         event_value = getattr(event, 'value', None)
#         if event_value and event_value.get('extrinsic_idx') == idx:
#             extrinsic_events.append(event)
#             if event_value['event_id'] == 'ExtrinsicSuccess':
#                 extrinsic_success = True
#     return extrinsic_events, extrinsic_success

# def report_swap_coldkey(current_block_number, extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp):
#     fields = []
#     if extrinsic_success == True:
#         current_block_field = {
#             "name": "🧱 **CURRENT BLOCK** 🧱",
#             "value": "",
#             "inline": False
#         }
#         current_block_field["value"] += f"{current_block_number}\n\n"
#         fields.append(current_block_field)
        
        
#         old_coldkey_field = {
#                 "name": "\n\n🔑 **OLD COLDKEY** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         old_coldkey_field["value"] += f"{old_coldkey}\n\n"
#         fields.append(old_coldkey_field)
        
#         new_coldkey_field = {
#                 "name": "\n\n🔑 **NEW COLDKEY** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         new_coldkey_field["value"] += f"{new_coldkey}\n\n"
#         fields.append(new_coldkey_field)
        
#         execution_block_field = {
#                 "name": "\n\n🧱 **EXECUTION BLOCK** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         execution_block_field["value"] += f"{execution_block}\n\n"
#         fields.append(execution_block_field)

#         time_stamp_field = {
#                 "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         time_stamp_field["value"] += f"{time_stamp}\n\n"
#         fields.append(time_stamp_field)
#     else:      
#         current_block_field = {
#             "name": "🧱 **CURRENT BLOCK** 🧱",
#             "value": "",
#             "inline": False
#         }
#         current_block_field["value"] += f"{current_block_number}\n\n"
#         fields.append(current_block_field)

#         old_coldkey_field = {
#                 "name": "\n\n🔑 **ACCOUNT** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         old_coldkey_field["value"] += f"{old_coldkey}\n\n"
#         fields.append(old_coldkey_field)
        
#         failed_extrinsic_field = {
#             "name": "🔴 **Extrinsic Failed** 🔴",
#             "value": "The extrinsic failed to execute.",
#             "inline": False
#         }
#         fields.append(failed_extrinsic_field)

#         time_stamp_field = {
#                 "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         time_stamp_field["value"] += f"{time_stamp}\n\n"
#         fields.append(time_stamp_field)
        
#     embed = {
#         "title": "🌟 __ NEW SCHEDULE_SWAP_COLDKEY DETECTED __ 🌟",
#         "description": "",
#         "color": 642600,  # Hex color code in decimal
#         "fields": fields,
#     }
#     return embed

# def check_dissolve_subnet(extrinsics):

#     for idx, extrinsic in enumerate(extrinsics):
#         extrinsic_value = getattr(extrinsic, 'value', None)
#         if not extrinsic_value:
#             continue
#         if extrinsic_value and 'call' in extrinsic_value:
#             call = extrinsic_value['call']
#             if call['call_function'] == 'schedule_dissolve_network' and call['call_module'] == 'SubtensorModule':
#                 return idx
#     return -1

# def process_dissolve_extrinsics(extrinsic_events):
#     """
#     Processes each extrinsic in the block, extracting relevant details and storing them in the database.
#     Also associates each extrinsic with its corresponding events and success status.

#     Parameters:
#     extrinsics (list): A list of extrinsic objects.
#     events (list): A list of event objects associated with the block.
#     block_instance (Block): The Block instance to which these extrinsics belong.
#     block_number (int): The block number.
#     """
#     netuid, execution_block = None, None
#     for event in extrinsic_events:
#         event_value = getattr(event, 'value', None)
#         if event_value['event_id'] == 'DissolveNetworkScheduled':
#             netuid = event_value['attributes']['netuid']
#             owner_coldkey = event_value['attributes']['account']
#             execution_block = event_value['attributes']['execution_block']
#     return netuid, owner_coldkey, execution_block

# def report_dissolve_subnet(current_block_number, extrinsic_success, netuid, owner_coldkey, execution_block, time_stamp):
#     fields = []
#     if extrinsic_success == True:
#         current_block_field = {
#             "name": "🧱 **CURRENT BLOCK** 🧱",
#             "value": "",
#             "inline": False
#         }
#         current_block_field["value"] += f"{current_block_number}\n\n"
#         fields.append(current_block_field)
        
#         owner_coldkey_field = {
#                 "name": "\n\n🔑 **OWNER COLDKEY** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         owner_coldkey_field["value"] += f"{owner_coldkey}\n\n"
#         fields.append(owner_coldkey_field)
        
#         netuid_field = {
#             "name": "🧱 **NETUID** 🧱",
#             "value": "",
#             "inline": False
#         }
#         netuid_field["value"] += f"{netuid}\n\n"
#         fields.append(netuid_field)
        
#         execution_block_field = {
#                 "name": "\n\n🧱 **EXECUTION BLOCK** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         execution_block_field["value"] += f"{execution_block}\n\n"
#         fields.append(execution_block_field)
        
#         time_stamp_field = {
#                 "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         time_stamp_field["value"] += f"{time_stamp}\n\n"
#         fields.append(time_stamp_field)
        
#     else:
#         current_block_field = {
#             "name": "🧱 **CURRENT BLOCK** 🧱",
#             "value": "",
#             "inline": False
#         }
#         current_block_field["value"] += f"{current_block_number}\n\n"
#         fields.append(current_block_field)        
        
#         failed_extrinsic_field = {
#             "name": "🔴 **Extrinsic Failed** 🔴",
#             "value": "The extrinsic failed to execute.",
#             "inline": False
#         }  
#         fields.append(failed_extrinsic_field)      
        
#         owner_coldkey_field = {
#                 "name": "\n\n🔑 **OWNER COLDKEY** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         owner_coldkey_field["value"] += f"{owner_coldkey}\n\n"
#         fields.append(owner_coldkey_field)

#         netuid_field = {
#             "name": "🧱 **NETUID** 🧱",
#             "value": "",
#             "inline": False
#         }
#         netuid_field["value"] += f"{netuid}\n\n"
#         fields.append(netuid_field)   

#         time_stamp_field = {
#                 "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
#                 "value": "",
#                 "inline": False
#         }
#         time_stamp_field["value"] += f"{time_stamp}\n\n"
#         fields.append(time_stamp_field)
        
#     embed = {
#         "title": "🌟 __ NEW SCHEDULE_NETWORK_DISSOLVE DETECTED __ 🌟",
#         "description": "",
#         "color": 342600,  # Hex color code in decimal
#         "fields": fields,
#     }
#     return embed

# def find_dissolve_subnet(substrate, block_number):
#     """
#     Main function to execute the block processing logic.
#     Sets up the substrate interface, retrieves block data, and processes the block and its extrinsics.
#     """
#     # block_number = 3593992
#     execution_block, time_stamp, netuid, owner_coldkey = None, None, None, None
#     extrinsic_success = False
#     block, events = get_block_data(substrate, block_number)
#     has_dissolve_subnet_idx= check_dissolve_subnet(block['extrinsics'])
#     if has_dissolve_subnet_idx >= 0:
#         print("block contains has_dissolve_subnet")
#         time_stamp = extract_block_timestamp(block['extrinsics'])
#         extrinsic_events, extrinsic_success = check_success(events, has_dissolve_subnet_idx)
#         if extrinsic_success == True:
#             netuid, owner_coldkey, execution_block = process_dissolve_extrinsics(extrinsic_events)

#     return has_dissolve_subnet_idx, extrinsic_success, netuid, owner_coldkey, execution_block, time_stamp

# def find_swap_coldkey(substrate, block_number):
#     """
#     Main function to execute the block processing logic.
#     Sets up the substrate interface, retrieves block data, and processes the block and its extrinsics.
#     """
#     # block_number = 3593992
#     old_coldkey, new_coldkey, execution_block, time_stamp = None, None, None, None
#     extrinsic_success = False
#     block, events = get_block_data(substrate, block_number)
#     is_schedule_swap_coldkey = check_schedule_swap_coldkey(block['extrinsics'])
#     if is_schedule_swap_coldkey:
#         print("block contains Swap coldkey scheduled")
#         time_stamp = extract_block_timestamp(block['extrinsics'])
#         extrinsic_events, extrinsic_success = check_success(events, is_schedule_swap_coldkey)
#         if extrinsic_success == True:
#             old_coldkey, new_coldkey, execution_block = process_swap_extrinsics(extrinsic_events)
#     return is_schedule_swap_coldkey, extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp      

# def observer_block():
#     substrate = setup_substrate_interface()
#     current_block_number = bt.subtensor().get_current_block()
#     current_block_number = 3941423
#     # current_block_number = 3877258
#     swap_coldkey_report, dissolve_subnet_report = None, None
#     is_schedule_swap_coldkey, extrinsic_success_swap_coldkey, new_coldkey, old_coldkey, execution_block, time_stamp = find_swap_coldkey(substrate, current_block_number)
#     extrinsic_success_swap_coldkey = False
#     if is_schedule_swap_coldkey:
#         swap_coldkey_report = report_swap_coldkey(current_block_number, extrinsic_success_swap_coldkey, new_coldkey, old_coldkey, execution_block, time_stamp)
    
#     has_dissolve_subnet_idx, extrinsic_success_dissolve_netword, netuid, owner_coldkey, execution_block, time_stamp = find_dissolve_subnet(substrate, current_block_number)
#     if has_dissolve_subnet_idx >= 0:
#         # extrinsic_success_dissolve_netword = False
#         dissolve_subnet_report = report_dissolve_subnet(current_block_number, extrinsic_success_dissolve_netword, netuid, owner_coldkey, execution_block, time_stamp)
    
    
#     return swap_coldkey_report, dissolve_subnet_report
    
# if __name__ == "__main__":
#     observer_block()
    
    


import pytz
from datetime import datetime
from substrateinterface.base import SubstrateInterface
import bittensor as bt

def setup_substrate_interface():
    """
    Initializes and returns a SubstrateInterface object configured to connect to a specified WebSocket URL.
    This interface will be used to interact with the blockchain.
    """
    return SubstrateInterface(
        url="wss://archive.chain.opentensor.ai:443/",
        ss58_format=42,
        use_remote_preset=True,
    )

def get_block_data(substrate, block_number):
    """
    Retrieves block data and associated events from the blockchain for a given block number.
    """
    block_hash = substrate.get_block_hash(block_id=block_number)
    block = substrate.get_block(block_hash=block_hash)
    events = substrate.get_events(block_hash=block_hash)
    return block, events

def extract_block_timestamp(extrinsics):
    """
    Extracts the timestamp from a list of extrinsics by identifying the 'set' function call within the 'Timestamp' module.
    """
    for extrinsic in extrinsics:
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
                return datetime.fromtimestamp(call['call_args'][0]['value'] / 1000, tz=pytz.UTC)
    return None

def check_extrinsic(extrinsics, function_name, module_name):
    """
    Checks for a specific extrinsic call in the list of extrinsics.
    Returns the index if found, otherwise -1.
    """
    for idx, extrinsic in enumerate(extrinsics):
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == function_name and call['call_module'] == module_name:
                return idx
    return -1

def process_swap_extrinsics(extrinsic_events):
    """
    Processes extrinsic events related to coldkey swap and extracts relevant details.
    """
    for event in extrinsic_events:
        event_value = getattr(event, 'value', None)
        if event_value['event_id'] == 'ColdkeySwapScheduled':
            old_coldkey = event_value['attributes']['old_coldkey']
            new_coldkey = event_value['attributes']['new_coldkey']
            execution_block = event_value['attributes']['execution_block']
            return old_coldkey, new_coldkey, execution_block
    return None, None, None

def process_dissolve_extrinsics(extrinsic_events):
    """
    Processes extrinsic events related to network dissolve and extracts relevant details.
    """
    for event in extrinsic_events:
        event_value = getattr(event, 'value', None)
        if event_value['event_id'] == 'DissolveNetworkScheduled':
            netuid = event_value['attributes']['netuid']
            owner_coldkey = event_value['attributes']['account']
            execution_block = event_value['attributes']['execution_block']
            return netuid, owner_coldkey, execution_block
    return None, None, None

def check_success(events, idx):
    """
    Checks if an extrinsic was successful and collects its events.
    """
    extrinsic_events = []
    extrinsic_success = False
    for event in events:
        event_value = getattr(event, 'value', None)
        if event_value and event_value.get('extrinsic_idx') == idx:
            extrinsic_events.append(event)
            if event_value['event_id'] == 'ExtrinsicSuccess':
                extrinsic_success = True
    return extrinsic_events, extrinsic_success

def generate_report(title, success, details, time_stamp):
    """
    Generates a report based on the extrinsic success and details provided.
    """
    fields = [{
        "name": "🧱 **CURRENT BLOCK** 🧱",
        "value": f"{details['current_block_number']}\n\n",
        "inline": False
    }]

    if success:
        for key, value in details.items():
            if key != 'current_block_number':
                fields.append({
                    "name": f"\n\n🔑 **{key.upper()}** \n\n\n",
                    "value": f"{value}\n\n",
                    "inline": False
                })
    else:
        fields.append({
            "name": "🔴 **Extrinsic Failed** 🔴",
            "value": "The extrinsic failed to execute.",
            "inline": False
        })

    fields.append({
        "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
        "value": f"{time_stamp}\n\n",
        "inline": False
    })

    return {
        "title": title,
        "description": "",
        "color": 642600 if "COLDKEY" in title else 342600,  # Different colors for different reports
        "fields": fields,
    }

def find_dissolve_subnet( block, events):
    """
    Finds and processes a scheduled network dissolve in the given block number.
    """
    idx = check_extrinsic(block['extrinsics'], 'schedule_dissolve_network', 'SubtensorModule')
    if idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, idx)
        netuid, owner_coldkey, execution_block = process_dissolve_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        return idx, extrinsic_success, netuid, owner_coldkey, execution_block, time_stamp
    return -1, False, None, None, None, None

def find_swap_coldkey(block, events):
    """
    Finds and processes a scheduled coldkey swap in the given block number.
    """
    
    idx = check_extrinsic(block['extrinsics'], 'schedule_swap_coldkey', 'SubtensorModule')
    if idx >= 0:
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, idx)
        old_coldkey, new_coldkey, execution_block = process_swap_extrinsics(extrinsic_events) if extrinsic_success else (None, None, None)
        return idx, extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp
    return -1, False, None, None, None, None

def observer_block():
    """
    Observes the current block for scheduled coldkey swaps and network dissolves, generating reports for each.
    """
    substrate = setup_substrate_interface()
    current_block_number = bt.subtensor().get_current_block()
    current_block_number = 3941423  # Example block number
    block, events = get_block_data(substrate, current_block_number)
    swap_coldkey_report, dissolve_subnet_report = None, None

    # Check for swap coldkey
    idx, success, new_coldkey, old_coldkey, execution_block, time_stamp = find_swap_coldkey(block, events)
    if idx >= 0:
        details = {
            "current_block_number": current_block_number,
            "old_coldkey": old_coldkey,
            "new_coldkey": new_coldkey,
            "execution_block": execution_block
        }
        swap_coldkey_report = generate_report("🌟 __ NEW SCHEDULE_SWAP_COLDKEY DETECTED __ 🌟", success, details, time_stamp)

    # Check for dissolve subnet
    idx, success, netuid, owner_coldkey, execution_block, time_stamp = find_dissolve_subnet(block, events)
    if idx >= 0:
        details = {
            "current_block_number": current_block_number,
            "netuid": netuid,
            "owner_coldkey": owner_coldkey,
            "execution_block": execution_block
        }
        dissolve_subnet_report = generate_report("🌟 __ NEW SCHEDULE_NETWORK_DISSOLVE DETECTED __ 🌟", success, details, time_stamp)

    return swap_coldkey_report, dissolve_subnet_report
