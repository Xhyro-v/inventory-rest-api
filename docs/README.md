# Project Documentation: Inventory and Order management API

- **Status**: Planning / In Development
- **Version**: v1.0.0
- **Created Date**: September 6, 2026
- **Project Owner**: Naufal Azhar

---

## 1. Executive Summary
The project aims to solve manual input order,product stock for retail business

## 2. Goals & Objectives
- **Primary Goal**: Decrease manual input work

---

## 3. Project Scope

### In-Scope
- Authentication  
- Role(Admin/Staff)
- CRUD Order (Status,History) 
- CRUD Accessibility by role (
            {Admin: 
                    +Product & stock management 
                    +Full acces of all Product CRUD
                    +Able to see Staff and Customer
            },
            {Staff:
                    +Create order
                    +Able to see order, product and stock
                    -Can't delete product
            }
) 

### Out-of-Scope (Phase 2)
- Vue
- React
- Tailwind
- dashboard
- fancy UI
- real payment gateway
- microservices
- Docker orchestration 
- Kubernetes
- Redis
- deployment production

---

## 4. Technical Architecture & Tech Stack

| Component | Technology / Tool |
| :--- | :--- |
| **Backend API** | Python (FastAPI) |
| **Database** | PostgreSQL (Primary) |
| **ORM** | SQLalchemy 2.0 (Primary) |
| **Migration** | Alembic (Primary) |

---
