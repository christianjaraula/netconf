from ncclient import manager
from ncclient.operations import RPCError
from datetime import datetime
import requests

# Device information
device_ip = "192.168.235.128"
device_port = 830
device_username = "cisco"
device_password = "cisco123!"

# WebEx Teams API details
webex_teams_access_token = 'ZmU3ZTUyODYtMjJhOS00ODJlLWExNGItM2I1Y2Q2NjM3OTdkODk5YTFlNTAtMDAy_P0A1_36820416-bfff-433a-84bf-39585b2b3f67'
webex_teams_room_id = 'b8075c50-3ca3-11ee-865d-d31b775d174c'

# NETCONF filter template for retrieving the running-config
get_config_template = """
<filter>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <interface>
      <GigabitEthernet>
        <name>1</name> <!-- Change the interface name accordingly -->
      </GigabitEthernet>
    </interface>
  </native>
</filter>
"""

# NETCONF edit-config template for making changes to the configuration
edit_config_template = """
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <interface>
      <GigabitEthernet>
        <name>1</name> <!-- Change the interface name accordingly -->
        <description>Updated Interface Description and set the negotiation to false</description> <!-- Change the description accordingly -->
        <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
          <auto>false</auto> <!-- Change the negotiation mode (true/false) accordingly -->
        </negotiation>
      </GigabitEthernet>
    </interface>
  </native>
</config>
"""

def connect_to_device():
    try:
        device = manager.connect(
            host=device_ip,
            port=device_port,
            username=device_username,
            password=device_password,
            device_params={'name': 'iosxe'}
        )
        return device
    except Exception as e:
        print(f"Failed to connect to the device: {e}")
        return None

def get_running_config(device):
    try:
        running_config = device.get_config(source='running', filter=get_config_template).data_xml
        return running_config
    except RPCError as rpc_error:
        print(f"Failed to retrieve running config: {rpc_error}")
        return None

def edit_config(device):
    try:
        device.edit_config(target='running', config=edit_config_template)
        print("Configuration changes applied successfully.")
    except RPCError as rpc_error:
        print(f"Failed to apply configuration changes: {rpc_error}")

def send_webex_teams_notification(message):
    try:
        url = f'https://api.ciscospark.com/v1/messages'
        headers = {
            'Authorization': f'Bearer {webex_teams_access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'roomId': webex_teams_room_id,
            'text': message
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("WebEx Teams notification sent successfully.")
    except Exception as e:
        print(f"Failed to send WebEx Teams notification: {e}")

def send_notification():
    # Implement the logic to send a notification message to the WebEx SE Teams group
    # You can customize the message content as needed
    message = f"Configuration update completed at {datetime.now()}. Changes have been made to the interface."
    print("Sending Notification:", message)
    
    # Use requests library or another suitable library to send the notification
    send_webex_teams_notification(message)

def main():
    # Connect to the device
    device = connect_to_device()
    if not device:
        return

    # Step 1: Verify the current running-config
    print("Current Running Configuration:")
    print(get_running_config(device))

    # Step 2: Make three changes to the configuration
    edit_config(device)

    # Step 3: Verify the changes
    print("Updated Running Configuration:")
    print(get_running_config(device))

    # Step 4: Verify the new running-config (same as Step 3 in this example)

    # Step 5: Send a notification message
    send_notification()

    # Close the NETCONF session
    device.close_session()

if __name__ == "__main__":
    main()
