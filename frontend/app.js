const ws = new WebSocket('ws://127.0.0.1:12345');
let username = null;

ws.onopen = () => {
    console.log("Connected to WebSocket server.");
};

ws.onmessage = (message) => {
    const data = JSON.parse(message.data);
    console.log("Received:", data);

    if (data.status === "success") {
        if (data.data) {
            console.log("Devices data:", data.data);
            showDevices(data.data);
        } else {
            console.log("No device data received.");
        }
        if (data.message) {
            alert(data.message);
        }
    } else {
        alert(data.message || "An error occurred.");
    }
};

document.getElementById('loginButton').onclick = function() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    if (user && pass) {
        username = user;

        const loginData = {
            action: "login",
            username: user,
            password: pass
        };
        ws.send(JSON.stringify(loginData));

        document.getElementById('loginForm').style.display = 'none';
    } else {
        alert("Please enter both username and password.");
    }
};

function showDevices(devices) {
    const devicesList = document.getElementById("devicesList");
    devicesList.innerHTML = ''; // Clear previous content

    // Iterate through devices to display them
    for (let deviceID in devices) {
        const device = devices[deviceID];

        if (!device || !device.device_id || !device.name) {
            console.error('Invalid device data:', device);
            continue;
        }

        const status = device.status !== undefined ? device.status : 'undefined';
        const brightness = device.brightness !== undefined ? device.brightness : 'undefined';
        const color = device.color !== undefined ? device.color : 'undefined';

        const deviceElement = document.createElement("div");
        deviceElement.id = `device-${device.device_id}`;
        deviceElement.classList.add("device-item");

        deviceElement.innerHTML = `
            <p><strong>${device.name} (${device.room})</strong></p>
            <p class="status">Status: ${status}, Brightness: ${brightness}%, Color: ${color}</p>
            <button onclick="controlDevice('${device.device_id}', 'turn_on')">Turn On</button>
            <button onclick="controlDevice('${device.device_id}', 'turn_off')">Turn Off</button>
            <button onclick="setBrightness('${device.device_id}')">Set Brightness</button>
            <button onclick="setColor('${device.device_id}')">Set Color</button>
        `;

        devicesList.appendChild(deviceElement);
    }

    document.getElementById('logoutButton').style.display = 'block';
    document.getElementById('loginButton').style.display = 'block';
}

function controlDevice(deviceID, command) {
    const controlData = {
        action: "control_device",
        deviceID: deviceID,
        command: command
    };

    console.log("Sending control data:", controlData);
    ws.send(JSON.stringify(controlData));
}

function setBrightness(deviceID) {
    const brightness = prompt("Enter brightness value (0-100):");
    if (brightness !== null && brightness !== '') {
        const brightnessData = {
            action: "set_brightness",
            deviceID: deviceID,
            brightness: brightness
        };

        ws.send(JSON.stringify(brightnessData));
    } else {
        alert("Please enter a valid brightness value.");
    }
}

function setColor(deviceID) {
    const color = prompt("Enter color (e.g., red, green, blue):");
    if (color) {
        const colorData = {
            action: "set_color",
            deviceID: deviceID,
            color: color
        };

        ws.send(JSON.stringify(colorData));
    } else {
        alert("Please enter a valid color.");
    }
}

document.getElementById('logoutButton').onclick = function() {
    const logoutData = {
        action: "logout"
    };
    ws.send(JSON.stringify(logoutData));

    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('logoutButton').style.display = 'none';
    document.getElementById('loginButton').style.display = 'block';
    alert("Logged out successfully");
};
