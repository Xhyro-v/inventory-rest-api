# API Design Structure and Endpoints

## 1. General Information

| Parameter | Detail |
| :--- | :--- |
| **Base URL** | `[https://api.tokoretail.com](https://api.tokoretail.com)` |
| **Protocol** | `HTTPS` |
| **Data Format** | `JSON` (`Content-Type: application/json`) |
| **Current Version** | `v1.0.0` |

---

## 2. Authentication 

Most of the endpoint need JWT to access it.

```
Authorization : Bearer <your_jwt_token>
```

### Role Access User

- **`Admin`** : Full access (Product management, user, transaction and order (Owner))
- **`Staff`** : Limited access (See transaction log, product stock and create order)
- **note** : This is user or this mean its either admin or staff will be at the same database table (user)


## 3. Standard Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success description message",
  "data": { ... } // Object or Array
}
```

### Error Response
```json
{
  "success": false,
  "message": "Failed/Error description message",
  "errors": [ ... ] // Opsional: Validation error details
}
```

## 4. Endpoint

### Authentication

#### 1. User Registration
* **Endpoint**: `POST /v1/auth/registration`
* **Access**: Private (Owner/Admin)
* **Body Request**: 
  * `email` (string (email)): Email
  * `password` (string): Password for new account
  * `password_confirm` (string): Retype previous password
  * `role` (enum, required): Role access (ADMIN or STAFF).
* **Description**: User registration (Admin|Staff) to get an account.
* **Note** : This endpoint for manual input to make account to adjust the scalability of the project 

---

#### 2. User Login
* **Endpoint**: `POST /v1/auth/login`
* **Access**: Public (Admin & Staff)
* **Body Request**: 
  * `email` (string (email)): Email
  * `password` (string): Password for account
* **Description**: User login (Admin|Staff) to get authenticated

---

### Product Management

#### 1. Get All Products
* **Endpoint**: `GET /v1/products`
* **Access**: Authenticated (`ADMIN`, `STAFF`)
* **Query Parameters**:
  * `page` (int, default: `1`): Page number.
  * `limit` (int, default: `10`): Total data.

#### 2. Get Products by SKU
* **Endpoint**: `GET /v1/products/{SKU}`
* **Access**: Authenticated (`ADMIN`, `STAFF`)
* **Path Variable** : SKU 

#### 3. Create Product
* **Endpoint**: `POST /v1/products`
* **Access**: Authenticated (`ADMIN`)
* **Body Request**:
  * `sku` (string): product unique alphanumeric
  * `name` (string): Product name.
  * `description` (string): Product description.
  * `price` (float): Product price.
  * `stock` (int, default: `1`): Product stock.

#### 4. Update Product
* **Endpoint**: `PATCH /v1/products/{product_id}`
* **Access**: Authenticated (`ADMIN`)
* **Path Variable**: `product_id` (integer)
* **Body Request**:
  * `name` (string, optional): Change product name.
  * `description` (string, optional): Change product description.
  * `price` (float, optional): Change product price.
  * `status` (enum, optional): Change product status (`active` / `inactive`).

#### 5. Delete Product
* **Endpoint**: `DELETE /v1/products/{product_id}`
* **Access**: Authenticated (`ADMIN`)
* **Path Variable**: `product_id` (integer)

---

### Product Stock Adjustments

#### 1. Get Stock Product
* **Endpoint**: `GET /v1/products/{product_id}/stock`
* **Access**: Authenticated (`ADMIN`, `STAFF`)
* **Path Variable**: `product_id` (integer)

#### 2. Adjust Stock
* **Endpoint**: `POST /v1/products/{product_id}/stock-adjustment`
* **Access**: Authenticated (`ADMIN`)
* **Path Variable**: `product_id` (integer)
* **Body Request**:
  * `stock_change` (integer, required): Quantity of the stock adjustment (e.g. +10 or -2)
  * `reason` (enum, required): `RESTOCK`, `DAMAGED`, `LOST`, `MANUAL_CORRECTION`
  
---

### Order Management 

#### 1. Get All Orders
* **Endpoint**: `GET /v1/orders`
* **Access**: Authenticated (`ADMIN`, `STAFF`)
* **Query Parameters**:
  * `page` (int, default: `1`): Page number.
  * `limit` (int, default: `10`): Total data.

#### 2. Get Orders by ID
* **Endpoint**: `GET /v1/orders/{order_id}`
* **Access**: Authenticated (`ADMIN`, `STAFF`)
* **Path Variable**: order_id (integer)

#### 3. Create Order
* **Endpoint**: `POST /v1/orders`
* **Access**: Authenticated (`ADMIN`,`STAFF`)
* **Body Request**:
  * `customer`: {
     * `customer_name` (string): Customer name
     * `customer_phone_number` (integer): Customer phone number
  }
  * `order_items` (list of an order item): list

#### 4. Update Order
* **Endpoint**: `PATCH /v1/orders/{order_id}/status`
* **Access**: Authenticated (`ADMIN`)
* **Path Variable**: order_id (integer)
* **Body Request**:
  * `status`: (enum, required) enums that contain status object

#### 5. Cancel Order
* **Endpoint**: `POST /v1/orders/{order_id}/cancel`
* **Access**: Authenticated (`ADMIN`)
* **Path Variable**: order_id (integer)
* **Description**: Validates the order can be cancelled, updates status to `CANCELLED`, restores inventory for affected items, writes an Order History entry and a Stock History entry (reason: `CANCELLATION`), all committed atomically.


---

### Order History

#### 1. Get All Order History
* **Endpoint**: `GET /v1/stock-history`
* **Access**: Authenticated (`ADMIN`)
* **Query Parameters**:
  * `page` (int, default: `1`): Page number.
  * `limit` (int, default: `10`): Total data.`

---

### Stock History

### 1. Get Stock History
* **Endpoint**: `GET /v1/stock-history`
* **Access**: Authenticated (`ADMIN`)
* **Query Parameters**:
  * `page` (int, default: `1`): Page number.
  * `limit` (int, default: `10`): Total data.`

