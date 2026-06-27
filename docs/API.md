# API Route Catalog

## Base URL
`http://localhost:8000/api`

## Endpoints

### 1. Authentication
*   **POST** `/auth/login`
    - **Body**: `{ "username": "admin", "password": "password" }`
    - **Response**: JWT access token, token type.
*   **POST** `/auth/register` (Admin-only)
    - **Headers**: Authorization Bearer `<token>`

### 2. Vehicles
*   **GET** `/vehicles`
    - **Query parameters**: `limit`, `skip`, `plate`
    - **Response**: List of vehicles.
*   **POST** `/vehicles`
    - **Body**: Vehicle registration schema.

### 3. Violations & Challans
*   **POST** `/violations`
    - **Body**: Multipart form data with evidence image + metadata JSON.
*   **POST** `/violations/{id}/verify`
    - **Body**: JSON flags confirming status.
*   **POST** `/generate-challan`
    - **Body**: `{ "violation_id": "<uuid>" }`
    - **Response**: Created Challan document link.
*   **POST** `/update-payment`
    - **Body**: Razorpay payment response payload.
