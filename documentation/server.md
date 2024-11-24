# Server API Documentation

## Base URL
`https://api.getthedamclass.sarvesh.me`

---

### 1. **Sign Up**

**Endpoint:** `/signup`  
**Method:** `POST`

**Description:** Register a new user with their email and pin.

**Request Body:**  
```json
{
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response:**
- **200 OK:**  
  ```json
  {
    "message": "User signed up successfully"
  }
  ```
- **400 Bad Request:**  
  ```json
  {
    "message": "Invalid email or pin"
  }
  ```

---
### 2. **Delete User**

**Endpoint:** `/deleteuser`
**Method:** `POST`

**Description:** Delete a user and all their subscriptions from the database.

**Request Body:**  
```json
{
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response:**
- **200 OK:**  
  ```json
  {
    "message": "User deleted successfully"
  }
  ```
- **400 Bad Request:**  
  ```json
  {
    "message": "Couldn't delete user. Try again!"
  }
  ```

---

### 3. **Subscribe to Class**

**Endpoint:** `/sub`  
**Method:** `POST`

**Description:** Subscribe to a class using its CRN.

**Request Body:**  
```json
{
  "crn": "12345",
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response:**
- **200 OK:**  
  ```json
  {
    "message": "Subscribed to class 12345 successfully"
  }
  ```
- **400 Bad Request:**  
  ```json
  {
    "message": "Invalid email, pin, or crn"
  }
  ```

---

### 4. **Unsubscribe from Class**

**Endpoint:** `/unsub`  
**Method:** `POST`

**Description:** Unsubscribe from a class using its CRN.

**Request Body:**  
```json
{
  "crn": "12345",
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response:**
- **200 OK:**  
  ```json
  {
    "message": "Unsubscribed from class 12345 successfully"
  }
  ```
- **400 Bad Request:**  
  ```json
  {
    "message": "Invalid email, pin, or crn"
  }
  ```

---

### 5. **Get Subscribed Classes**

**Endpoint:** `/getsubs`  
**Method:** `POST`

**Description:** Retrieve a list of classes the user is subscribed to.

**Request Body:**  
```json
{
  "email": "user@example.com",
  "pin": "1234"
}
```

**Response:**
- **200 OK:**  
  ```json
  {
    "subs": {
      "crn": "cname"
    }
  }
  ```
- **400 Bad Request:**  
  ```json
  {
    "message": "Invalid email or pin"
  }
  ```

---

### 6. **Unsubscribe All (with Query Parameters)**

**Endpoint:** `/unsubscribe`  
**Method:** `GET`

**Description:** Unsubscribe all classes with a specific query value.

**Query Parameter:**  
- `value` - (Required) The value used to perform unsubscription.

**Example Request:**  
`GET /unsubscribe?value=some_value`

**Response:**
- **200 OK:**  
  ```json
  {
    "message": "Unsubscribed successfully"
  }
  ```

---