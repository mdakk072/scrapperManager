from ipc import IPC

def run_requester():
    ipc = IPC()
    address = "tcp://127.0.0.1:5555"
    ipc.init_requester("client", address)
    print(f"Requester initialized to connect to {address}")

    try:
        while True:
            message = input("Enter request message: ")
            if message.lower() == "exit":
                break
            response = ipc.send_request("client", message)
            if response:
                print(f"Received response: {response}")
            else:
                print("No response received.")
    except KeyboardInterrupt:
        print("Stopping requester...")
    finally:
        ipc.close()

if __name__ == "__main__":
    run_requester()
