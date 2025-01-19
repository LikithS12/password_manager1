import csv
import hashlib
from cryptography.fernet import Fernet

# Encryption setup
KEY_FILE = "encryption.key"

def generate_key():
    """Generate a unique encryption key and save it to a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    """Load the encryption key from the file."""
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        generate_key()
        return load_key()

key = load_key()
cipher = Fernet(key)

# File paths
ACCOUNTS_FILE = "accounts.txt"
PASSWORDS_FILE = "passwords.csv"

def create_account():
    """Allow the user to create a new account."""
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    with open(ACCOUNTS_FILE, "a") as file:
        file.write(f"{email},{hashed_password}\n")
    print("Account created successfully. Please re-run the program to log in.")

def validate_login():
    """Validate a user's login credentials."""
    accounts = {}

    try:
        with open(ACCOUNTS_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:  # Ensure the line has exactly two elements
                    email, hashed_password = parts
                    accounts[email] = hashed_password
                else:
                    print(f"Skipping invalid line in accounts file: {line.strip()}")
    except FileNotFoundError:
        print("No accounts found. Please create an account first.")
        return False

    for _ in range(3):
        email = input("Enter your email: ").strip()
        if email in accounts:
            for _ in range(3):
                password = input("Enter your password: ").strip()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if accounts[email] == hashed_password:
                    print("Login successful!")
                    return True
                print("Incorrect password. Try again.")
            break
        print("Email not found. Try again.")
    print("Login failed. Please try again later.")
    return False

def add_password():
    """Add a new password to the CSV."""
    website = input("Enter the website/app: ").strip()
    username = input("Enter the username: ").strip()
    password = input("Enter the password: ").strip()
    print(f"\nYou entered:\nWebsite/App: {website}\nUsername: {username}\nPassword: {password}")
    confirm = input("Is this information correct? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Restarting password entry...")
        return add_password()

    encrypted_password = cipher.encrypt(password.encode()).decode()
    with open(PASSWORDS_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([website, username, encrypted_password])
    print("Password saved successfully.")

def view_passwords():
    """View all saved passwords."""
    try:
        with open(PASSWORDS_FILE, "r") as file:
            reader = csv.reader(file)
            print("\nSaved Passwords:")
            for row in reader:
                if len(row) == 3:  # Check if the row has exactly three elements
                    website, username, encrypted_password = row
                    decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
                    print(f"Website/App: {website}, Username: {username}, Password: {decrypted_password}")
                else:
                    print(f"Skipping malformed row: {row}")
    except FileNotFoundError:
        print("No passwords found.")

def main():
    """Main menu for the password manager."""
    print("Password Manager\n")
    print("1. Create an Account\n2. Log In")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        create_account()
    elif choice == "2":
        if validate_login():
            while True:
                print("\n1. Add Password\n2. View Passwords\n3. Log Out")
                option = input("Enter your choice: ").strip()
                if option == "1":
                    add_password()
                elif option == "2":
                    view_passwords()
                elif option == "3":
                    print("Logged out. Goodbye!")
                    break
                else:
                    print("Invalid choice. Try again.")
    else:
        print("Invalid option. Exiting.")

if __name__ == "__main__":
    main()

