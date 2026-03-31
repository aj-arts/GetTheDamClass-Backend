# Database Functions Documentation

---

## `connect_to_db(attempts=5, delay=5)`
- **Description:** Attempts to connect to the MySQL database with retry logic.
- **Parameters:** 
  - `attempts` (int): Number of connection attempts.
  - `delay` (int): Delay in seconds between retries.
- **Returns:** A database connection object.

---

## `valid(email, pin)`
- **Description:** Validates if the provided PIN matches the hashed PIN for the given email.
- **Parameters:** 
  - `email` (str): The user's email.
  - `pin` (str): The user's PIN.
- **Returns:** `True` if valid, `False` otherwise.

---

## `addUser(email, pin)`
- **Description:** Adds a new user with a hashed PIN to the database.
- **Parameters:** 
  - `email` (str): The user's email.
  - `pin` (str): The user's PIN.
- **Returns:** `True` after successful addition.

---

## `linkCRN(CRN, email)`
- **Description:** Links a CRN (course number) to the user identified by email.
- **Parameters:** 
  - `CRN` (int): The CRN number.
  - `email` (str): The user's email.
- **Returns:** `True` if successful, `False` if user not found.

---

## `unlinkCRN(CRN, email)`
- **Description:** Unlinks a CRN from the user identified by email.
- **Parameters:** 
  - `CRN` (int): The CRN number.
  - `email` (str): The user's email.
- **Returns:** `True` if successful, `False` if not linked.

---

## `getCRNsByUser(email)`
- **Description:** Retrieves all CRNs linked to the given user.
- **Parameters:** 
  - `email` (str): The user's email.
- **Returns:** A list of CRNs.

---

## `delSubscription(subsubToken)`
- **Description:** Deletes a subscription by its unique unsubscribe token.
- **Parameters:** 
  - `subsubToken` (str): The unsubscribe token.
- **Returns:** `True` if successful, `False` if not found.

---

## `getUniqueCRNs()`
- **Description:** Retrieves all distinct CRN numbers and their course names.
- **Returns:** A list of dictionaries with `CRN` and `COURSE_NAME`.

---

## `getUsersByCRN(CRN)`
- **Description:** Retrieves all users linked to a given CRN.
- **Parameters:** 
  - `CRN` (int): The CRN number.
- **Returns:** A list of user emails.

---

## `getUnsubValue(email, CRN)`
- **Description:** Retrieves the unsubscribe token for a user’s specific CRN subscription.
- **Parameters:** 
  - `email` (str): The user's email.
  - `CRN` (int): The CRN number.
- **Returns:** The unsubscribe token or `False`.

---

## `purgeUnusedCRNs()`
- **Description:** Deletes CRNs not linked to any active subscriptions.
- **Returns:** `True` after completion.

---

## `purgeUnusedUsers()`
- **Description:** Deletes users not linked to any subscriptions.
- **Returns:** `True` after completion.

---

## `deleteUser(email)`
- **Description:** Deletes a user and their data based on email.
- **Parameters:** 
  - `email` (str): The user's email.
- **Returns:** `True` if successful, `False` if user not found.

---

## `wasVacant(crn)`
- **Description:** Checks the vacancy status of a CRN.
- **Parameters:** 
  - `crn` (int): The CRN number.
- **Returns:** `True` if vacant, `False` otherwise.

---

## `setWasVacant(crn, vacant)`
- **Description:** Updates the vacancy status of a CRN.
- **Parameters:** 
  - `crn` (int): The CRN number.
  - `vacant` (bool): Vacancy status.
- **Returns:** `True` if successful, `False` otherwise.

---

## `setCourseName(crn, name)`
- **Description:** Updates or inserts the course name for a CRN.
- **Parameters:** 
  - `crn` (int): The CRN number.
  - `name` (str): The course name.
- **Returns:** `True` if successful, `False` otherwise.

---

## `getCourseName(crn)`
- **Description:** Retrieves the course name for a CRN.
- **Parameters:** 
  - `crn` (int): The CRN number.
- **Returns:** The course name or `False`. 
