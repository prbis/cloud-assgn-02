import requests

#API_GATEWAY_URL = 'http://localhost:5000'
API_GATEWAY_URL = 'https://apigateway-806117749861.us-central1.run.app'

# Function to create a user
def create_user(account_id, email, delivery_address):
    payload = {
        'account_id': account_id,
        'email': email,
        'delivery_address': delivery_address
    }
    response = requests.post(f"{API_GATEWAY_URL}/users", json=payload)
    if response.status_code == 201:
        print("User created successfully:", response.json())
        return response.json()
    else:
        print("Failed to create user:", response.status_code, response.text)
        return None

# Function to update a user
def update_user(user_id, email=None, delivery_address=None):
    payload = {}
    if email:
        payload['email'] = email
    if delivery_address:
        payload['delivery_address'] = delivery_address

    response = requests.put(f"{API_GATEWAY_URL}/users/{user_id}", json=payload)
    if response.status_code == 200:
        print("User updated successfully:", response.json())
        return response.json()
    else:
        print("Failed to update user:", response.status_code, response.text)
        return None

# Function to create an order
def create_order(items, email, delivery_address):
    payload = {
        'items': items,
        'email': email,
        'delivery_address': delivery_address
    }
    response = requests.post(f"{API_GATEWAY_URL}/orders", json=payload)
    if response.status_code == 201:
        print("Order created successfully:", response.json())
        return response.json()
    else:
        print("Failed to create order:", response.status_code, response.text)
        return None

# Function to update an order
def update_order(order_id, status=None):
    payload = {}
    if status:
        payload['status'] = status

    response = requests.put(f"{API_GATEWAY_URL}/orders/{order_id}", json=payload)
    if response.status_code == 200:
        print("Order updated successfully:", response.json())
        return response.json()
    else:
        print("Failed to update order:", response.status_code, response.text)
        return None

# Test the end-to-end functionality
def test_system():
    # Step 1: Create a user
    user = create_user(
        account_id="rafat11111",
        email="rafat@example.com",
        delivery_address="Montreal,Canada"
    )
    if not user:
        print("Exiting: Failed to create user.")
        return

    # Step 2: Update the user's email and delivery address
    user_id = user.get('_id')
    updated_user = update_user(user_id, email="updated_rafat@example.com", delivery_address="Toronto,Canada")
    if not updated_user:
        print("Exiting: Failed to update user.")
        return

    # Step 3: Create an order for the user
    order = create_order(
        items=["item1", "item2"],
        email=user.get("email"),
        delivery_address=user.get("delivery_address")
    )
    if not order:
        print("Exiting: Failed to create order.")
        return

    # Step 4: Update the order status
    order_id = order.get('_id')
    updated_order = update_order(order_id, status="delivered")
    if not updated_order:
        print("Exiting: Failed to update order.")
        return

    # Final Test Results
    print("\n--- Test Results ---")
    print("User:", updated_user)
    print("Order:", updated_order)

# Entry point for the script
if __name__ == '__main__':
    test_system()
