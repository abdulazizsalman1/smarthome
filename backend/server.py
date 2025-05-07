import asyncio
import websockets
import sys
import os
import json

# Ensure the backend modules are in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.models import devices
from backend.protocol import marshal, unmarshal
from backend.users import get_user

connected_clients = {}

async def handle_client(websocket):
    username = None
    try:
        print(f"✅ New client connected: {websocket.remote_address}")

        while True:
            data = await websocket.recv()
            request = unmarshal(data)
            response = await process_request(request, websocket)

            # On login, send the full devices list right away
            if request.get("action") == "login" and response["status"] == "success":
                username = request.get("username")
                connected_clients[username] = websocket
                devices_list = {device.device_id: device.get_info() for device in devices.values()}
                await websocket.send(marshal({'status': 'success', 'data': devices_list}))
            else:
                # For any other request, send back the response (which now includes full devices list if applicable)
                await websocket.send(marshal(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected: {username}")
        if username in connected_clients:
            del connected_clients[username]

async def process_request(request, websocket):
    action = request.get('action')

    if action == 'login':
        username = request.get('username')
        password = request.get('password')
        if get_user(username) == password:
            return {'status': 'success', 'message': 'Login successful'}
        else:
            return {'status': 'fail', 'message': 'Invalid credentials'}

    elif action == 'list_devices':
        devices_list = {device.device_id: device.get_info() for device in devices.values()}
        return {'status': 'success', 'data': devices_list}

    elif action == 'control_device':
        device_id = request.get('deviceID')
        command = request.get('command')
        device = devices.get(device_id)
        if device:
            result = device.control(command)
            devices_list = {d.device_id: d.get_info() for d in devices.values()}
            return {
                'status': 'success',
                'message': result['message'],
                'data': devices_list
            }
        else:
            return {'status': 'fail', 'message': 'Device not found'}

    elif action == 'set_brightness':
        device_id = request.get('deviceID')
        brightness = request.get('brightness')
        device = devices.get(device_id)
        if device:
            result = device.set_brightness(brightness)
            devices_list = {d.device_id: d.get_info() for d in devices.values()}
            return {
                'status': 'success',
                'message': result['message'],
                'data': devices_list
            }
        else:
            return {'status': 'fail', 'message': 'Device not found'}

    elif action == 'set_color':
        device_id = request.get('deviceID')
        color = request.get('color')
        device = devices.get(device_id)
        if device:
            result = device.set_color(color)
            devices_list = {d.device_id: d.get_info() for d in devices.values()}
            return {
                'status': 'success',
                'message': result['message'],
                'data': devices_list
            }
        else:
            return {'status': 'fail', 'message': 'Device not found'}

    elif action == 'logout':
        return {'status': 'success', 'message': 'Logged out successfully'}

    return {'status': 'fail', 'message': 'Unsupported action'}

async def main():
    async with websockets.serve(handle_client, "localhost", 12345, ping_interval=None):
        print("✅ WebSocket server started at ws://localhost:12345")
        await asyncio.Future()  # Keep the server running

if __name__ == '__main__':
    asyncio.run(main())
