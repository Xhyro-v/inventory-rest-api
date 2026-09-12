# Business Rule

## Customer Resolution

Customer is a domain entity and is not an authenticated user.

When Staff/Admin creates an order, customer information must be provided as part of the order request.

The backend uses the customer's phone number as the business identifier.

Flow:
1. Receive customer name and phone number.
2. Search existing customer by phone number.
3. If a customer exists, reuse the existing customer record.
4. If no customer exists, create a new customer.
5. Use the resulting customer ID as the order's customer reference.
6. Continue order creation.

## Order Cancellation

An order can only be cancelled from allowed states.

When a valid cancellation is requested:
1. Validate authenticated actor and permission.
2. Validate current order state.
3. Change order status to CANCELLED.
4. Restore inventory for all affected order items.
5. Create an OrderHistory event.
6. Create corresponding StockHistory records.
7. Commit the operation atomically.

* PENDING → CANCELLED
* CONFIRMED → CANCELLED
* COMPLETED → not allowed
* CANCELLED → not allowed

If any inventory or history operation fails, the entire transaction must be rolled back.

---

## POST /orders

### Customer Resolution During Order Creation

When POST /orders is called:

1. Receive customer information.
2. Find customer by phone.
3. If found, reuse the existing customer.
4. If not found, create a new customer.
5. Use the resulting customer ID when creating the order.
6. Customer resolution and order creation must remain consistent within the transaction.

### Order Item Relation During Order Creation

when POST orders/ is called: 

1. Take product information like price, stock, status
2. If the status is active and the stock is available, continue the order
3. If the status inactive and the stock is unavailable product can't be taken 
4. When the order is pending with status `PENDING` stock will ready to get adjustment(+/-) with the quantity of the product in the orders
5. When the status is `CONFIRMED` after stock ready with adjustment request, `CONFIRMED` will immediately deducted from available stock.
Flow:  

``` CREATE
PENDING
  ↓
stock made request

CONFIRMED
  ↓
Stock -QTY

COMPLETED
  ↓
no stock adjustment 
```