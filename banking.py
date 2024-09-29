import mysql.connector
from mysql.connector import Error

# Establish the MySQL connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',          # Update with your MySQL host
            user='root',               # Update with your MySQL username
            password='root',  # Update with your MySQL password
            database='banking_system'  # Ensure the database is created
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to create a new account
def create_account(connection, account_number, account_holder):
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO accounts (account_number, account_holder) VALUES (%s, %s)", 
                       (account_number, account_holder))
        connection.commit()
        print(f"Account {account_number} created successfully!")
    except Error as e:
        print(f"Failed to create account: {e}")
    finally:
        cursor.close()

# Function to deposit money
def deposit(connection, account_number, amount):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", 
                       (amount, account_number))
        cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)",
                       (account_number, 'Deposit', amount))
        connection.commit()
        print(f"Deposited ${amount} to account {account_number}")
    except Error as e:
        print(f"Failed to deposit: {e}")
    finally:
        cursor.close()

# Function to withdraw money
def withdraw(connection, account_number, amount):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (account_number,))
        balance = cursor.fetchone()[0]

        if balance >= amount:
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                           (amount, account_number))
            cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)",
                           (account_number, 'Withdraw', amount))
            connection.commit()
            print(f"Withdrew ${amount} from account {account_number}")
        else:
            print("Insufficient funds!")
    except Error as e:
        print(f"Failed to withdraw: {e}")
    finally:
        cursor.close()

# Function to transfer money between accounts
def transfer(connection, from_account, to_account, amount):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_number = %s", (from_account,))
        from_balance = cursor.fetchone()[0]

        if from_balance >= amount:
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_number = %s", 
                           (amount, from_account))
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_number = %s", 
                           (amount, to_account))
            cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)",
                           (from_account, 'Transfer Out', amount))
            cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, %s, %s)",
                           (to_account, 'Transfer In', amount))
            connection.commit()
            print(f"Transferred ${amount} from account {from_account} to account {to_account}")
        else:
            print("Insufficient funds!")
    except Error as e:
        print(f"Failed to transfer: {e}")
    finally:
        cursor.close()

# Function to generate an account report
def account_report(connection, account_number):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM accounts WHERE account_number = %s", (account_number,))
        account = cursor.fetchone()
        if account:
            print(f"Account Number: {account[0]}\nAccount Holder: {account[1]}\nBalance: ${account[2]}\n")
            cursor.execute("SELECT * FROM transactions WHERE account_number = %s ORDER BY timestamp", 
                           (account_number,))
            transactions = cursor.fetchall()
            print("Transactions:")
            for transaction in transactions:
                print(f"{transaction[3]}: {transaction[2]} ${transaction[4]}")
        else:
            print("Account not found!")
    except Error as e:
        print(f"Failed to fetch account report: {e}")
    finally:
        cursor.close()

# Main menu for banking operations
def main_menu():
    connection = create_connection()
    if connection:
        while True:
            print("1. Create Account\n2. Deposit\n3. Withdraw\n4. Transfer\n5. Report\n6. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                acc_num = input("Enter account number: ")
                acc_holder = input("Enter account holder name: ")
                create_account(connection, acc_num, acc_holder)
            elif choice == '2':
                acc_num = input("Enter account number: ")
                amount = float(input("Enter deposit amount: "))
                deposit(connection, acc_num, amount)
            elif choice == '3':
                acc_num = input("Enter account number: ")
                amount = float(input("Enter withdrawal amount: "))
                withdraw(connection, acc_num, amount)
            elif choice == '4':
                from_acc = input("Enter sender account number: ")
                to_acc = input("Enter recipient account number: ")
                amount = float(input("Enter transfer amount: "))
                transfer(connection, from_acc, to_acc, amount)
            elif choice == '5':
                acc_num = input("Enter account number: ")
                account_report(connection, acc_num)
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Try again!")
        
        # Close the MySQL connection
        connection.close()

# Run the program

main_menu()