import pytz
from datetime import datetime
from substrateinterface.base import SubstrateInterface
import bittensor as bt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from observing.bot.bot import post_to_discord
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
    print(block_hash)
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

def check_dissolve_subnet(extrinsics):

    for idx, extrinsic in enumerate(extrinsics):
        # print(idx)
        extrinsic_value = getattr(extrinsic, 'value', None)
        if not extrinsic_value:
            continue
        if extrinsic_value and 'call' in extrinsic_value:
            call = extrinsic_value['call']
            if call['call_function'] == 'schedule_dissolve_network' and call['call_module'] == 'SubtensorModule':
            # if call['call_function'] == 'set' and call['call_module'] == 'Timestamp':
                return idx
    return -1

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

def report_dissolve_subnet(current_block_number, time_stamp):
    fields = []
    current_block_field = {
        "name": "🧱 **CURRENT BLOCK** 🧱",
        "value": "",
        "inline": False
    }
    current_block_field["value"] += f"{current_block_number}\n\n"
    fields.append(current_block_field)

    time_stamp_field = {
            "name": "\n\n🕙  **CURRENT BLOCK TIMESTAMP** \n\n\n",
            "value": "",
            "inline": False
    }
    time_stamp_field["value"] += f"{time_stamp}\n\n"
    fields.append(time_stamp_field)
        
    embed = {
        "title": "🌟 __ NEW SCHEDULE_DESSOLVE_NETWORK DETECTED __ 🌟",
        "description": "",
        "color": 642600,  # Hex color code in decimal
        "fields": fields,
    }
    return embed

def dissolve_subnet(substrate, block_number):
    """
    Main function to execute the block processing logic.
    Sets up the substrate interface, retrieves block data, and processes the block and its extrinsics.
    """
    # block_number = 3593992
    execution_block, time_stamp = None, None
    
    block, events = get_block_data(substrate, block_number)
    has_dissolve_subnet_idx= check_dissolve_subnet(block['extrinsics'])
    print (has_dissolve_subnet_idx)
    if has_dissolve_subnet_idx >= 0:
        print("block contains has_dissolve_subnet")
        time_stamp = extract_block_timestamp(block['extrinsics'])
    return has_dissolve_subnet_idx, time_stamp

def observer_block():
    DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1290411821072781372/fLDmDgtz-10ucE5oCBGm4kMj7RFBwXaq2u-7KG9A4p5573kJOlyb97SxXg6DKBP1PtMO"
    substrate = setup_substrate_interface()
    for current_block_number in range(3872180, 3944180):
        print(current_block_number)
        has_dissolve_subnet_idx, time_stamp = dissolve_subnet(substrate, current_block_number)
        # has_dissolve_subnet_idx = True
        if has_dissolve_subnet_idx >= 0:
            dissolve_subnet_report = report_dissolve_subnet(current_block_number, time_stamp)
            post_to_discord(dissolve_subnet_report, DISSOLVE_NETWORK_DISCORD_WEBHOOK_URL)

if __name__ == "__main__":
    observer_block()
    
    
