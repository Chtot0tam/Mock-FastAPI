# Mock-FastAPI

A simple IoT Devices environment built with FastAPI, made for training API testing and security analysis. Runs on localhost and contains intentional vulnerabilities mapped to the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).

---

## Setup

1. Download [Python](https://www.python.org/downloads/)
2. Download [VS Code](https://code.visualstudio.com/download)
3. Install dependencies — open the VS Code terminal and run:
   ```bash
   pip install fastapi uvicorn
   ```
4. Clone this repository and open it as a project in VS Code
5. Start the server:
   ```bash
   py -m uvicorn main:app --reload
   ```
6. Open Swagger docs in your browser:
   ```
   http://127.0.0.1:8000/docs
   ```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/login` | Log in and receive a token |
| `POST` | `/register` | Register a new user |
| `GET` | `/api/devices` | List all devices |
| `GET` | `/api/devices/{device_id}` | Get a single device by ID |
| `GET` | `/api/devices/type/{device_type}` | List devices by type |
| `POST` | `/api/devices` | Create a new device (admin only) |
| `PUT` | `/api/devices/{device_id}` | Update a device (admin only) |
| `DELETE` | `/api/devices/{device_id}` | Delete a device (admin only) |

### Example device response

```json
{
  "id": 1,
  "device_id": "socket-01",
  "owner": "user1",
  "type": "Socket",
  "room": "Living Room",
  "online": true,
  "power_w": 42.5,
  "voltage": 230
}
```

---

## Tests

### How to run

1. Download [Postman](https://www.postman.com/downloads/)
2. Import the collection: left bar → `...` → Import → `postman/IoT_Security_Tests.json`
3. Run the collection

### CRUD

| # | Test | Expected |
|---|---|---|
| 1 | Get all devices — response is array and not empty | 200 |
| 2 | Get a specific device and verify its properties | 200 |
| 3 | Get a non-existent device | 404 |
| 4 | Get devices by type and verify results | 200 |
| 5 | Get devices with an invalid type | 404 |
| 6 | Create a Socket device | 201 |
| 7 | Create a WaterLeakSensor | 201 |
| 8 | Create a Socket with missing required fields | 422 |
| 9 | Create a device with invalid data type | 422 |
| 10 | Update an existing device | 200 |
| 11 | Update a non-existing device | 404 |
| 12 | Delete an existing device | 200 |
| 13 | Delete a non-existing device | 404 |

### Auth

| # | Test | Expected |
|---|---|---|
| 1 | Successful login | 200 |
| 2 | Invalid password | 401 |
| 3 | Non-existing user | 401 |

### Registration

| # | Test | Expected |
|---|---|---|
| 1 | Successful registration | 201 |
| 2 | Duplicate username | 409 |
| 3 | Missing credentials | 422 |

---

## Security Analysis — OWASP API Top 10 Mapping

### `POST /login`

| | |
|---|---|
| **Auth required** | No |
| **Role required** | — |

**API2 — Broken Authentication**  
Passwords are hashed but there is no rate limiting, meaning unlimited brute-force attempts are possible against any username. No account lockout mechanism exists.

**API8 — Security Misconfiguration**  
No password strength validation on registration means weak passwords are accepted, making brute-force easier.

---

### `POST /register`

| | |
|---|---|
| **Auth required** | No |
| **Role required** | — |

**API2 — Broken Authentication**  
New users are always assigned the `user` role. There is no way to promote a user to admin through the API — this has to be done manually in code, which is a misconfiguration waiting to happen in a real deployment.

**API8 — Security Misconfiguration**  
No password strength validation. A user can register with a single-character password. No protection against automated account creation.

---

### `GET /api/devices`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Any authenticated user |

**API1 — Broken Object Level Authorization**  
The endpoint returns all devices from all owners in a single response. `user1` can see `user2`'s water leak sensor including its location (Basement) and battery level. There is no filtering by `owner` field.

**API3 — Broken Object Property Level Authorization**  
The response exposes sensitive internal fields — `warning: WATER_LEAK_DETECTED`, `battery: 15`, `leak_detected: true` — for devices the requesting user does not own.

---

### `GET /api/devices/{device_id}`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Any authenticated user |

**API1 — Broken Object Level Authorization**  
A user can request any device by numeric ID regardless of ownership. `user1` can fetch device `id: 4` owned by `user2` and see that there is a water leak in their Basement.

---

### `GET /api/devices/type/{device_type}`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Any authenticated user |

**API1 — Broken Object Level Authorization**  
Filtering by type returns all matching devices across all owners. Querying `WaterLeakSensor` reveals both `user1` and `user2`'s sensors including their rooms, battery levels, and leak status.

**API8 — Security Misconfiguration**  
The `device_type` path parameter is passed directly into a string comparison with no input validation or allowlist check.

---

### `POST /api/devices`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Admin only |

**API5 — Broken Function Level Authorization**  
Correctly restricted to admins. A regular user token receives `403 Forbidden`. The risk here is that the `owner` field in the request body is free text — an admin can create a device assigned to any username, including ones that don't exist.

---

### `PUT /api/devices/{device_id}`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Admin only |

**API5 — Broken Function Level Authorization**  
Correctly restricted to admins. However, the full device object must be sent on every update — there is no partial update (PATCH) support. This means a client must know all current field values to update just one, which risks accidentally overwriting data.

**API1 — Broken Object Level Authorization**  
No ownership check beyond the admin role. An admin can modify any user's device, including setting `leak_detected: false` on `user2`'s sensor to suppress a real alert.

---

### `DELETE /api/devices/{device_id}`

| | |
|---|---|
| **Auth required** | Yes |
| **Role required** | Admin only |

**API5 — Broken Function Level Authorization**  
Correctly restricted to admins. A regular user token receives `403 Forbidden`.

**API1 — Broken Object Level Authorization**  
No ownership check beyond the admin role. An admin can delete any user's device — including `user2`'s basement water leak sensor — without any ownership confirmation.

---

## OWASP Coverage Summary

| OWASP Category | Endpoints affected |
|---|---|
| API1 — Broken Object Level Authorization | GET /devices, GET /devices/{id}, GET /devices/type/{type}, PUT, DELETE |
| API2 — Broken Authentication | POST /login, POST /register |
| API3 — Broken Object Property Level Authorization | GET /devices |
| API5 — Broken Function Level Authorization | POST /devices, PUT /devices/{id}, DELETE /devices/{id} |
| API8 — Security Misconfiguration | POST /login, POST /register, GET /devices/type/{type} |