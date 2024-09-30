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
    
    Parameters:
    substrate (SubstrateInterface): The interface used to interact with the blockchain.
    block_number (int): The block number to retrieve data for.

    Returns:
    tuple: Contains the block data, events, and block hash.
    """
    block_hash = substrate.get_block_hash(block_id=block_number)
    block = substrate.get_block(block_hash=block_hash)
    events = substrate.get_events(block_hash=block_hash)
    return block, events

def extract_block_timestamp(extrinsics):
    """
    Extracts the timestamp from a list of extrinsics by identifying the 'set' function call within the 'Timestamp' module.

    Parameters:
    extrinsics (list): A list of extrinsic objects from which to extract the timestamp.

    Returns:
    datetime: The extracted timestamp in UTC, or None if not found.
    """
    for extrinsic in extrinsics:
        extrinsic_value = getattr(extrinsic, 'value', None)
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
                return datetime.fromtimestamp(call['call_args'][0]['value'] / 1000, tz=pytz.UTC)
    return None

def check_schedule_swap_coldkey(extrinsics):

    for idx, extrinsic in enumerate(extrinsics):
        extrinsic_value = getattr(extrinsic, 'value', None)
        if not extrinsic_value:
            continue
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'schedule_swap_coldkey' and call['call_module'] == 'SubtensorModule':
                return idx
    return None

def process_extrinsics(extrinsic_events):
    """
    Processes each extrinsic in the block, extracting relevant details and storing them in the database.
    Also associates each extrinsic with its corresponding events and success status.

    Parameters:
    extrinsics (list): A list of extrinsic objects.
    events (list): A list of event objects associated with the block.
    block_instance (Block): The Block instance to which these extrinsics belong.
    block_number (int): The block number.
    """
    for event in extrinsic_events:
        event_value = getattr(event, 'value', None)
        if event_value['event_id'] == 'ColdkeySwapScheduled':
            old_coldkey = event_value['attributes']['old_coldkey']
            new_coldkey = event_value['attributes']['new_coldkey']
            execution_block = event_value['attributes']['execution_block']
    return old_coldkey, new_coldkey, execution_block

def check_success(events, idx):

    extrinsic_events = []
    extrinsic_success = False
    for event in events:
        event_value = getattr(event, 'value', None)
        if event_value and event_value.get('extrinsic_idx') == idx:
            extrinsic_events.append(event)
            if event_value['event_id'] == 'ExtrinsicSuccess':
                extrinsic_success = True
    return extrinsic_events, extrinsic_success

def report_swap_coldkey(extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp):
    fields = []
    if extrinsic_success:
        old_coldkey_field = {
                "name": "\n\n🌿 **OLD HOTKEY** 🌿\n\n\n",
                "value": "",
                "inline": False
        }
        old_coldkey_field["value"] += f"{old_coldkey}\n\n"
        fields.append(old_coldkey_field)
        
        new_coldkey_field = {
                "name": "\n\n🌿 **NEW HOTKEY** 🌿\n\n\n",
                "value": "",
                "inline": False
        }
        new_coldkey_field["value"] += f"{new_coldkey}\n\n"
        fields.append(new_coldkey_field)
        
        execution_block_field = {
                "name": "\n\n🌿 **EXECUTION BLOCK** 🌿\n\n\n",
                "value": "",
                "inline": False
        }
        execution_block_field["value"] += f"{execution_block}\n\n"
        fields.append(execution_block_field)
        
        time_stamp_field = {
                "name": "\n\n🌿 **TIME STAMP** 🌿\n\n\n",
                "value": "",
                "inline": False
        }
        time_stamp_field["value"] += f"{time_stamp}\n\n"
    else:
        fields.append({
            "name": "🔴 **Extrinsic Failed** 🔴",
            "value": "The extrinsic failed to execute.",
            "inline": False
        })
        
    embed = {
        "title": "🌟 __ NEW SCHEDULE_SWAP_COLDKEY DETECTED __ 🌟",
        "description": "",
        "color": 642600,  # Hex color code in decimal
        "fields": fields,
    }

def find_swap_coldkey(block_number):
    """
    Main function to execute the block processing logic.
    Sets up the substrate interface, retrieves block data, and processes the block and its extrinsics.
    """
    # block_number = 3593992
    old_coldkey, new_coldkey, execution_block = None, None, None
    substrate = setup_substrate_interface()
    block, events = get_block_data(substrate, block_number)
    is_schedule_swap_coldkey = check_schedule_swap_coldkey(block['extrinsics'], events)
    if is_schedule_swap_coldkey:
        print("block contains Swap coldkey scheduled")
        time_stamp = extract_block_timestamp(block['extrinsics'])
        extrinsic_events, extrinsic_success = check_success(events, is_schedule_swap_coldkey)
        if extrinsic_success:
            old_coldkey, new_coldkey, execution_block = process_extrinsics(extrinsic_events)
        return extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp        

def observer_block():
    
    extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp = find_swap_coldkey(3941423)
    swap_coldkey_report = report_swap_coldkey(extrinsic_success, new_coldkey, old_coldkey, execution_block, time_stamp)
    # network_dissolve_report = report_network_dissolve()
    return swap_coldkey_report
    
if __name__ == "__main__":
    observer_block()