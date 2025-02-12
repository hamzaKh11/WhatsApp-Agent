from flask import Flask, request, jsonify
import os
from mistralai import Mistral

print("Flask app is starting...")
app = Flask(__name__)
print("Flask app initialized.")

# Replace with your actual Mistral.ai API key
api_key = "wQjDI3vp1mCx2ZKPJxCcfaOkDvGjojUT"
model = "mistral-large-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)


@app.route('/twilio-whatsapp-webhook', methods=['POST'])
def twilio_webhook():
    print("--------------------------- /twilio-whatsapp-webhook --------------------------")
    print("Request received!")
    print("Headers:", request.headers)
    print("Form Data:", request.form)

    incoming_message = request.form.get('Body')
    sender_phone = request.form.get('From')

    if incoming_message is None or sender_phone is None:
        print("Error: Missing Body or From fields.")
        return "Bad Request", 400

    print("Incoming Message:", incoming_message)
    print("Sender Phone:", sender_phone)

    # Check if the message contains product details
    if "Je suis intéressé par ce produit" in incoming_message:
        # Parse the product details from the incoming message
        product_details = parse_product_details(incoming_message)
        product_name = product_details.get(
            "productName", "Nom du produit non disponible")
        product_price = product_details.get(
            "productPrice", "Prix non disponible")
        product_description = product_details.get(
            "productDescription", "Description non disponible")
        product_link = product_details.get(
            "productLink", "Lien non disponible")

        # Add product details to the conversation history
        conversation_history = [
            {"role": "system", "content": "Act like a SalesAgent in French who answers customers' questions about products, convinces customers to buy, and collects the information needed to confirm an order."},
            {"role": "assistant", "content": f"Vous êtes intéressé par le produit suivant : {product_name}. Voici les détails : {product_description}. Prix : {product_price}. Lien : {product_link}."},
            {"role": "user", "content": incoming_message},
        ]
    else:
        # Default conversation history
        conversation_history = [
            {"role": "system", "content": "Act like a SalesAgent in French who answers customers' questions about products, convinces customers to buy, and collects the information needed to confirm an order."},
            {"role": "user", "content": incoming_message},
        ]

    try:
        # Send the message to Mistral.ai for processing
        chat_response = client.chat.complete(
            model=model,
            messages=conversation_history
        )
        ai_response = chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Mistral.ai: {e}")
        ai_response = "Désolé, il y a eu une erreur. Veuillez réessayer."

    # Return the response to Twilio
    return f'<Response><Message>{ai_response}</Message></Response>'


def parse_product_details(message):
    """Parse product details from the incoming message."""
    print("---------------------------(parse_product_details)--------------------------")
    details = {}
    lines = message.split("\n")
    for line in lines:
        if "Nom :" in line:
            details["productName"] = line.split(":")[1].strip()
        elif "Prix :" in line:
            details["productPrice"] = line.split(":")[1].strip()
        elif "Description :" in line:
            details["productDescription"] = line.split(":")[1].strip()
        elif "Lien :" in line:
            details["productLink"] = line.split(":")[1].strip()
    return details


if __name__ == '__main__':
    app.run(debug=True, port=5000)
