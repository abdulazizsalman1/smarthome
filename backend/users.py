# Sample user credentials
users = {
    "admin": "password123"
}

def get_user(username):
    return users.get(username)
