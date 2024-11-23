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

### 2. **Subscribe to Class**

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

### 3. **Unsubscribe from Class**

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

### 4. **Get Subscribed Classes**

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

### 5. **Unsubscribe All (with Query Parameters)**

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