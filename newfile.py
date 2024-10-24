import json
from datetime import datetime

class DairyBillManager:
    def __init__(self, filename='bills.json'):  # Removed extra space
        self.filename = filename
        self.prices = {
            'milk': 50,      # Set price per liter
            'yogurt': 30,    # Set price per kg
            'paneer': 200,   # Set price per kg
            'cheese': 250    # Set price per kg
        }
        self.load_bills() 

    def load_bills(self):
        try:
            with open(self.filename, 'r') as file:
                self.bills = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.bills = []

    def save_bills(self):
        with open(self.filename, 'w') as file:
            json.dump(self.bills, file, indent=4)

    def add_bill(self, product, quantity):
        if product in self.prices:
            if quantity <= 0:  # Validate quantity
                print("Quantity must be greater than zero.")
                return
            amount = self.prices[product] * quantity
            bill = {
                'product': product,
                'quantity': quantity,
                'amount': amount,
                'date': datetime.now().isoformat()
            }
            self.bills.append(bill)
            self.save_bills()
            print(f"Added bill for {quantity} kg/liter of {product} costing {amount}.")
        else:
            print("Invalid product.")

    def view_bills(self):
        if not self.bills:
            print("No bills available.")
            return

        for index, bill in enumerate(self.bills):
            try:
                print(f"{index}. Date: {bill['date']}, Product: {bill['product']}, Quantity: {bill['quantity']}, Amount: {bill['amount']}")
            except KeyError as e:
                print(f"Bill entry {index} is missing key: {e}. Entry: {bill}")

    def total_expense(self):
        total = sum(bill['amount'] for bill in self.bills)
        print(f"Total Monthly Expense: {total}")

    def delete_bill(self, index):
        if 0 <= index < len(self.bills):
            self.bills.pop(index)
            self.save_bills()
            print("Bill deleted.")
        else:
            print("Invalid index.")

def main():
    manager = DairyBillManager()

    while True:
        print("1. Add Bill")
        print("2. View Bills")
        print("3. Total Expense")
        print("4. Delete Bill")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            print("Available products: milk, yogurt, paneer, cheese")
            product = input("Enter product name: ").strip().lower()
            quantity = float(input("Enter quantity: "))
            manager.add_bill(product, quantity)
        elif choice == '2':
            manager.view_bills()
        elif choice == '3':
            manager.total_expense()
        elif choice == '4':
            try:
                index = int(input("Enter bill index to delete: "))
                manager.delete_bill(index)
            except ValueError:
                print("Please enter a valid integer.")
        elif choice == '5':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
