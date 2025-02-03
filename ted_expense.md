# Finance Management System API Documentation

## Table of Contents
1. **User Roles & Permissions**
2. **Authentication**
3. **User Management**
4. **Transaction Operations**
5. **Expense Categories**
6. **Loan Management**
7. **Filters & Search**
8. **Error Handling**

---

## 1. User Roles & Permissions
### Roles:
- **Admin**: Full system access
- **TED**: Department user (Transaction capabilities)
- **S2L**: Department user (Transaction capabilities)

### Permission Matrix:
| Endpoint               | Admin | TED | S2L |
|------------------------|-------|-----|-----|
| User Creation          | ✔     | ✖   | ✖   |
| Transaction Creation   | ✔     | ✔   | ✔   |
| Loan Approval          | ✔     | ✖   | ✖   |
| Category Management    | ✔     | ✔*  | ✔*  |
| All Money Allocation   | ✔     | ✖   | ✖   |

_* Can only manage their own categories_

---

## 2. Authentication
### Obtain Token
**Endpoint**  
`POST /api/auth/token/`

**Request**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1
}
```

**Usage**  
Include token in header for authenticated requests:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## 3. User Management
### Create User (Admin Only)
**Endpoint**  
`POST /api/auth/create_user/`

**Request**
```json
{
  "username": "ted_user",
  "password": "tedpass123",
  "user_type": "ted"
}
```

### Change Password
**Endpoint**  
`POST /api/auth/user/<id>/change_pass/`

**Request**
```json
{
  "password": "newpassword123"
}
```

---

## 4. Transaction Operations
### Default Admin View
Admins automatically see **all transactions** from all departments. Default daily view shows transactions from last 24 hours.

**Base Endpoint**  
`GET /api/transaction/`

### Filter Capabilities
```http
GET /api/transaction/?user_type=ted&start_date=2023-07-01&end_date=2023-07-31
```

**Parameters**:
- `transaction_type`: expense/user_allocated_money/admin_allocated_money
- `category__name`: Category name (partial match)
- `min_ammount`: Minimum transaction amount
- `max_ammount`: Maximum transaction amount
- `source`: Payment source (cash/bank/etc)

### Create Transaction
**Endpoint**  
`POST /api/transaction/`

**Request**
```json
{
  "ammount": "500.00",
  "transaction_type": "expense",
  "category": 1,
  "source": "cash"
}
```

### Money Allocation
**Admin to User**  
`POST /api/user_allocated_money/`
```json
{
  "user": 2,
  "ammount": "1000.00",
  "source": "bank"
}
```

**To Admin Account**  
`POST /api/admin_allocated_money/`
```json
{
  "ammount": "5000.00",
  "source": "cash"
}
```

---

## 5. Expense Categories
### Category Management
**Create Category**  
`POST /api/expence_category/`
```json
{
  "name": "Office Supplies",
  "description": "Pens, paper, etc"
}
```

**Access Rules**:
- Admins see all categories
- Department users see only their own categories

---

## 6. Loan Management
### Loan Request Flow
1. **Department User Creates Request**
   ```http
   POST /api/loan_requests/
   ```
   ```json
   {
     "to_department": "s2l",
     "amount": "15000.00"
   }
   ```

2. **Admin Actions**:
   - Approve: `POST /api/loan_requests/<id>/approve_loan/`
   - Decline: `POST /api/loan_requests/<id>/decline_loan/`

### Loan Balance Rules
- Approved loans increase lender's `loan_balance`
- Decrease borrower's `loan_balance`
- Automatic balance adjustment between departments

---

## 7. Advanced Filters
### Transaction Search
```http
GET /api/transaction/?search=office
```
Searches in:
- Transaction type
- Category name
- Username
- Department type
- Source

### Ordering
```http
GET /api/transaction/?ordering=-ammount  # Descending by amount
GET /api/transaction/?ordering=created_at  # Oldest first
```

---

## 8. Error Handling
### Common Errors
**403 Forbidden**  
- Unauthorized loan approval attempt
- Department user accessing admin endpoints

**400 Bad Request**  
```json
{
  "error": "Insufficient balance"
}
```

**404 Not Found**  
```json
{
  "error": "User not found"
}
```

### Validation Errors
```json
{
  "non_field_errors": [
    "Cannot request loan from same department"
  ]
}
```

---

## Frontend Implementation Guide

### Default Admin Dashboard
1. Load initial transactions:
   ```http
   GET /api/transaction/?start_date={today}
   ```
2. Display filters:
   - Department selector (ted/s2l)
   - Date range picker
   - Category dropdown
   - Amount range slider

### Real-time Updates
- Refresh transaction list after:
  - Money allocations
  - Loan approvals
  - New transactions

### Balance Display
Show calculated balances:
```javascript
// User object structure
{
  "balance": "15000.00",
  "loan_balance": "5000.00"
}
```

### Loan Management UI
1. Status indicators (pending/approved/declined)
2. Approval history tracking:
   ```json
   {
     "approved_at": "2023-07-15",
     "approved_by": "admin"
   }
   ```

This documentation provides comprehensive guidance for implementing all system features. Always include the authentication token in headers for protected endpoints and handle 403 errors with appropriate user reauthentication flows.