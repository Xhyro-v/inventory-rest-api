## Database Entities/Models 
* **User** 
  * Identifier
  * Email 
  * Role
  * Password (Hashed)

* Customer
  * customer_id
  * name
  * phone
  * created_at
  * updated_at

* **Product**
  * identifier(product_id)
  * SKU
  * name
  * description
  * price
  * current stock
  * active/inactive status
  * created timestamp
  * updated timestamp

* **Order Item**
  * order_item_id
  * product_id
  * quantity
  * unit_price
  * subtotal

* **Order**
  * order_id
  * Customer (Domain entities)
  * Order Item   
  * Total amount 
  * status
    * `PENDING`
    * `CONFIRMED`
    * `CANCELLED`  
    * `COMPLETED`  
  * created timestamp
  * updated timestamp

* **Order History**
  * id
  * order_id
  * event_type
  * actor_id
  * old_status
  * new_status
  * reason/note
  * created_at

* **StockHistory**
  * Identifier
  * Product_id
  * Quantity_change
  * Stock_before
  * Stock_after
  * Reason
  * Order_id(nullable)
  * Actor_id
  * Created_at


## Entity Relationships
- User 1:N Order
- User 1:N OrderHistory
- User 1:N StockHistory
- Customer 1:N Order
- Order 1:N OrderItem
- Product 1:N OrderItem
- Order 1:N OrderHistory
- Product 1:N StockHistory
- Order 0:N StockHistory