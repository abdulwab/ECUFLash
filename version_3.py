import can
import time

def setup_can_interface():
    try:
        bus = can.interface.Bus(interface='ixxat', channel=0, bitrate=500000)
        print("CAN interface initialized successfully.")
        return bus
    except Exception as e:
        print(f"Failed to initialize CAN interface: {e}")
        return None

def read_tune_file(tune_file_path):
    try:
        with open(tune_file_path, 'rb') as f:
            print("File content (hex):")
            for i in range(10):  # Print the first 10 chunks
                chunk = f.read(8)
                if not chunk:
                    break
                print(chunk.hex())
    except FileNotFoundError:
        print(f"Error: Tune file '{tune_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_tune_data(bus, tune_file_path):
    try:
        with open(tune_file_path, 'rb') as f:
            while True:
                chunk = f.read(8)  # Read 8 bytes at a time
                if not chunk:
                    break

                if chunk == b'\xff\xff\xff\xff\xff\xff\xff\xff':
                    print("Skipping empty data chunk.")
                    continue
                
                msg = can.Message(arbitration_id=0x7E0, data=chunk, is_extended_id=False)
                bus.send(msg)
                
                # print(f"Sent chunk: {chunk.hex()}")

                response = bus.recv(timeout=1)  # Wait for a response for up to 1 second
                print(f"Its response : {response}")

                time.sleep(0.05)  # Add a delay of 50ms between each message (adjust as needed)

    except FileNotFoundError:
        print(f"Error: Tune file '{tune_file_path}' not found.")
    except can.CanError as e:
        print(f"CAN error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_flash_command(bus):
    try:
        msg = can.Message(arbitration_id=0x7E0, data=[0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0, 0x12], is_extended_id=False)
        bus.send(msg)
        print("Flash command sent successfully.")

        response = bus.recv(timeout=1)  # Wait for a response for up to 1 second
        if response:
            print(f"Received response to flash command: {response.data.hex()}")
        else:
            print("No response received to flash command.")
    except can.CanError as e:
        print(f"Error sending CAN message: {e}")

def unlock_ecu(bus):
    try:
        msg = can.Message(arbitration_id=0x7E0, data=[0x02, 0x27, 0x01], is_extended_id=False)
        bus.send(msg)
        print("Unlock command sent.")

        response = bus.recv(timeout=1)  # Wait for a response for up to 1 second
        if response:
            print(f"Received response to unlock command: {response.data.hex()}")
        else:
            print("No response received to unlock command.")
    except can.CanError as e:
        print(f"Error sending CAN message: {e}")

def flash_ecu(tune_file_path):
    bus = setup_can_interface()
    if not bus:
        return

    unlock_ecu(bus)
    send_flash_command(bus)
    
    # Flash the ECU with the tune file
    send_tune_data(bus, tune_file_path)

    print("Flashing process completed.")
    reset_msg = can.Message(arbitration_id=0x7E0, data=[0x11, 0x01], is_extended_id=False)
    bus.send(reset_msg)
    print("Sent ECU reset command.")

    # Shutdown the CAN bus properly
    bus.shutdown()

if __name__ == "__main__":
    tune_file_path = './bin/Can-Am_Traxter_Defender_2016_HD10_72_hp_Bosch_ME17.8.5_Bench_NR.bin'  # Replace with actual file path
    
    # Test reading the file content
    read_tune_file(tune_file_path)
    
    # Flash the ECU
    flash_ecu(tune_file_path)