import socket
from rich.console import Console
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.protocol import marshal, unmarshal

console = Console()

def main():
    host = 'localhost'
    port = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        console.print("[green]Connected to the server[/]")

        # Authentication
        username = console.input("[bold magenta]Username: [/]")
        password = console.input("[bold magenta]Password: [/]")
        login_request = {'action': 'login', 'username': username, 'password': password}
        s.send(marshal(login_request).encode())
        response = unmarshal(s.recv(1024).decode())
        console.print(f"[yellow]{response['message']}[/]")

        if response['status'] == 'success':
            # Device Interaction
            while True:
                s.send(marshal({'action': 'list_devices'}).encode())
                response = unmarshal(s.recv(1024).decode())
                console.print("[yellow]Devices:[/]")
                for device_id, device in response['data'].items():
                    console.print(f"[blue]{device_id}: {device}[/]")

                device_id = console.input("Enter device ID to control or [bold red]'logout'[/] to exit: ")
                if device_id.lower() == 'logout':
                    break

                command = console.input("Enter command (e.g., 'turn_on', 'turn_off', 'set_brightness_100', 'set_color_red'): ")
                control_request = {'action': 'control_device', 'deviceID': device_id, 'command': command}
                s.send(marshal(control_request).encode())
                control_response = unmarshal(s.recv(1024).decode())
                console.print(f"[magenta]{control_response['message']}[/]")

            # Logout
            logout_request = {'action': 'logout'}
            s.send(marshal(logout_request).encode())
            logout_response = unmarshal(s.recv(1024).decode())
            console.print(f"[red]{logout_response['message']}[/]")

if __name__ == '__main__':
    main()
