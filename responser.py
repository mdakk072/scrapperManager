from ipc import IPC
import time

def run_responder():
    ipc = IPC()
    address = "tcp://127.0.0.1:5555"
    ipc.init_replier(address)
    print(f"Replier initialized at {address}")

    try:
        while True:
            request = ipc.receive_request(timeout=1000)
            if request:
                print(f"Received request: {request}")
                response = f"Response to: {request} ra sma3tek >!"
                ipc.send_response(response)
                print(f"Sent response: {response}")
            else:
                print("No request received. Waiting...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping responder...")
    finally:
        ipc.close()

if __name__ == "__main__":
    run_responder()
