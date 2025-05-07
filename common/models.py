# models.py
class Device:
    def __init__(self, device_id, name, room, status='off'):
        self.device_id = device_id
        self.name = name
        self.room = room
        self.status = status

    def get_info(self):
        return f"{self.name} - {self.status}"

    def control(self, command):
        if command == 'turn_on':
            self.status = 'on'
        elif command == 'turn_off':
            self.status = 'off'
        else:
            return {'status': 'fail', 'message': 'Invalid command'}
        return {'status': 'success', 'message': f'{self.name} in {self.room} turned {self.status}'}

class Light(Device):
    def __init__(self, device_id, name, room, status='off', brightness=100, color='white'):
        super().__init__(device_id, name, room, status)
        self.brightness = brightness
        self.color = color

    def control(self, command):
        result = super().control(command)
        if 'fail' in result['status']:
            return result
        if command.startswith('set_brightness'):
            self.brightness = int(command.split('_')[-1])
            return {'status': 'success', 'message': f'{self.name} brightness set to {self.brightness}'}
        elif command.startswith('set_color'):
            self.color = command.split('_')[-1]
            return {'status': 'success', 'message': f'{self.name} color set to {self.color}'}
        return result

# Example devices
devices = {
    "1": Light("1", "Living Room Main Light", "Living Room"),
    "2": Light("2", "Living Room Side Light", "Living Room"),
    "3": Light("3", "Kitchen Light", "Kitchen"),
    "4": Light("4", "Bedroom Main Light", "Bedroom"),
    "5": Light("5", "Bedroom Side Light", "Bedroom")
}
