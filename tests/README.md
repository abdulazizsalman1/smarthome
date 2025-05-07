# Smart Home System Tests

This directory contains the test suite for the Smart Home System. The tests cover authentication, homes, rooms, and devices functionality.

## Test Structure

- `test_auth.py`: Tests for user registration and authentication
- `test_homes.py`: Tests for home management
- `test_devices.py`: Tests for device management and control

## Running Tests

1. Install the required dependencies:
```bash
pip install pytest pytest-asyncio
```

2. Run all tests:
```bash
pytest
```

3. Run specific test file:
```bash
pytest tests/test_auth.py
```

4. Run with detailed output:
```bash
pytest -v
```

## Test Coverage

The tests cover the following functionality:

### Authentication
- User registration
- Duplicate username handling
- Login with correct credentials
- Login with incorrect credentials
- Token validation

### Homes
- Creating a new home
- Getting list of homes
- Unauthorized access prevention
- Home ownership validation

### Devices
- Creating new devices
- Getting device list
- Updating device status
- Device type-specific controls
- Unauthorized access prevention

## Test Database

Tests use a separate SQLite database (`test.db`) to avoid affecting the production database. The test database is automatically created and cleaned up before and after each test.

## Continuous Integration

The test suite is designed to be run as part of a CI/CD pipeline. All tests must pass before code can be merged into the main branch. 