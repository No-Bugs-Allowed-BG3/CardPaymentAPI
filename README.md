
# 💳 Card Payment API

A simple FastAPI-based backend for handling card payment operations including balance checking, withdrawing money, and receiving payments from external dealers.
This API is __NOT__ intended for production, it's purpose is to facilitate the development and/or testing of our main project - Virtual Wallet ( MoneyHub )
---

## 🚀 Features

- Check balance of a card with CVV, expiry, and currency
- Withdraw money from a card if balance is sufficient
- Add money to a card from an external dealer

---

## 📦 Tech Stack

- **FastAPI** for API endpoints
- **SQLite** for lightweight database
- **Pydantic** for request validation
- **Uvicorn** as the ASGI server

---

## 📁 Project Structure

```
card_payment_api/
├── main.py                # Main application file
├── db/
│   └── cardpayments.db    # SQLite database
```

---

## 📡 API Endpoints

### 🔍 Check Card Balance

**POST** `/balance/checks/`

#### Request Body
```json
{
  "number": "1234567812345678",
  "cvv_code": "007",
  "expiry": "01/28",
  "requested_amount": 100,
  "currency": "EUR"
}
```

#### Response
```json
{
  "number": "1234567812345678",
  "requested_amount": 100,
  "approved": true,
  "currency": "EUR"
}
```

---

### 💸 Withdraw Money From Card

**POST** `/cards/withdrawals/`

#### Request Body
```json
{
  "number": "1234567812345678",
  "cvv_code": "007",
  "expiry": "01/28",
  "requested_amount": 100,
  "currency": "EUR"
}
```

#### Response
```json
{
  "number": "1234567812345678",
  "requested_amount": 100,
  "approved": true,
  "currency": "EUR"
}
```

---

### 💰 Pay Money to Card (External Dealer)

**POST** `/payments/`

#### Request Body
```json
{
  "sender": "8765432187654321",
  "number": "1234567812345678",
  "incoming_amount": 200,
  "currency": "EUR"
}
```

#### Response
```json
true
```

---

## ⚙️ Running the Project

### 1. Install Dependencies
```bash
pip install fastapi uvicorn
```

### 2. Start the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8002
```

### 3. Test the API
You can use tools like [Postman](https://www.postman.com/) or `curl`.

---

## 🗄️ Database Schema

Ensure your SQLite `cardpayments.db` includes a table like:

```sql
CREATE TABLE "cards" (
	"id"	INTEGER,
	"card_number"	TEXT NOT NULL,
	"cvv"	TEXT NOT NULL,
	"expiry"	TEXT NOT NULL,
	"balance"	TEXT NOT NULL,
	"currency"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)
```

---

## 🛡️ Validation Rules

| Field           | Validation                        |
|----------------|------------------------------------|
| `number`        | 16-digit numeric string            |
| `cvv_code`      | 3-digit numeric string             |
| `expiry`        | Format `MM/YY`                     |
| `currency`      | 3 uppercase letters (e.g., USD)    |
| `requested_amount` / `incoming_amount` | Must be > 0 |

---

## 📬 Contact

For issues or suggestions, feel free to open an issue or contact the maintainer.

---

## 📝 License

Feel free to use or modify parts of this code.
