import requests
import json
import time


# =========================
# CONFIGURATION
# =========================

BOT_TOKEN = "8895633565:AAE9FwDP1PqEf7rMmQnlLYdi8YS-ZxendzU"

EXTERNAL_API_URL = "https://core.telegram.org/bots/api"


# Telegram API base URL
TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# =========================
# SEND MESSAGE
# =========================

def send_message(chat_id, text, reply_markup=None):
    url = TELEGRAM_API + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        return response.json()

    except Exception as error:
        print("Send message error:", error)
        return None


# =========================
# REPLY KEYBOARD
# =========================

def get_keyboard():
    return {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# =========================
# PHONE LOOKUP
# =========================

def phone_lookup(phone_number):
    if EXTERNAL_API_URL == "":
        return {
            "error": "External API URL is not configured."
        }

    try:
        # Send the number to your authorized external API.
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=15
        )

        response.raise_for_status()

        # Convert API response into JSON
        result = response.json()

        return result

    except requests.exceptions.RequestException as error:
        return {
            "error": "External API request failed.",
            "details": str(error)
        }

    except ValueError:
        return {
            "error": "External API did not return valid JSON."
        }


# =========================
# HANDLE UPDATES
# =========================

def handle_update(update):

    if "message" not in update:
        return

    message = update["message"]

    if "chat" not in message:
        return

    chat_id = message["chat"]["id"]

    text = message.get("text", "")

    # =========================
    # /start COMMAND
    # =========================

    if text == "/start":

        welcome_message = (
            "👋 Welcome!\n\n"
            "This is an educational Telegram bot.\n\n"
            "Choose an option below:"
        )

        send_message(
            chat_id,
            welcome_message,
            get_keyboard()
        )

        return

    # =========================
    # PHONE LOOKUP BUTTON
    # =========================

    if text == "📱 Phone Lookup":

        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:"
        )

        return

    # =========================
    # PHONE NUMBER VALIDATION
    # =========================

    if text.isdigit():

        if len(text) != 10:

            send_message(
                chat_id,
                "❌ Invalid number.\n\n"
                "Please send exactly 10 digits."
            )

            return

        # =========================
        # API REQUEST
        # =========================

        result = phone_lookup(text)

        # Convert result to formatted JSON
        formatted_json = json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )

        # Telegram HTML <pre> formatting
        response_text = (
            "<pre>"
            + formatted_json
            + "</pre>"
        )

        send_message(
            chat_id,
            response_text
        )

        return

    # =========================
    # INVALID INPUT
    # =========================

    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please use the button and send a valid "
        "10 digit mobile number."
    )


# =========================
# LONG POLLING
# =========================

def main():

    if BOT_TOKEN == "":
        print("ERROR: BOT_TOKEN is empty.")
        print("Add your Telegram Bot Token first.")
        return

    offset = None

    print("Bot started...")
    print("Waiting for messages...")

    while True:

        try:

            params = {
                "timeout": 30
            }

            if offset is not None:
                params["offset"] = offset

            response = requests.get(
                TELEGRAM_API + "/getUpdates",
                params=params,
                timeout=40
            )

            data = response.json()

            if not data.get("ok"):
                print("Telegram API error:")
                print(data)

                time.sleep(3)
                continue

            updates = data.get("result", [])

            for update in updates:

                # Move offset forward so the same
                # update is not processed again.
                offset = update["update_id"] + 1

                handle_update(update)

        except requests.exceptions.RequestException as error:

            print("Network error:", error)
            time.sleep(5)

        except ValueError:

            print("Telegram returned invalid JSON.")
            time.sleep(3)

        except Exception as error:

            print("Unexpected error:", error)
            time.sleep(3)


# =========================
# PROGRAM START
# =========================

if __name__ == "__main__":
    main()
