# Functional Requirements
---
## User

| # | As a... | I can...     | Object     |
| - | ------- | ------------ | ---------- |
| 1 | User    | **register** | Profile    |
| 2 | User    | **create**   | Order      |
| 3 | User    | **create**   | Specialist |
| 4 | User    | **complete** | Order      |

## Specialist

| # | As a...    | I can...   | Object  |
| - | ---------- | ---------- | ------- |
| 1 | Specialist | **create** | Catalog |
| 2 | Specialist | **take**   | Order   |

## Admin

| # | As a... | I can...   | Object     |
| - | ------- |------------| ---------- |
| 1 | Admin   | **verify** | Specialist |
| 1 | Admin   | **ban**    | Specialist |

## Any User

| # | As a... | I can... | Object             |
| - | ------- | -------- | ------------------ |
| 1 | Any     | **see**  | Active Orders      |
| 2 | Any     | **see**  | Specialist Catalog |
| 3 | Any     | **see**  | Active Specialists |

---


# ERD
```mermaid
erDiagram
    users {
        uuid id PK
        enum role
        varchar name
        varchar surname
        date birth_date
        varchar phone
        varchar email
        varchar hashed_password
        timestamptz created_at
    }

    specialist {
        uuid id PK
        uuid user_id FK
        varchar h3_index
        boolean is_active
        boolean is_verified
        timestamptz created_at
    }

    address {
        uuid id PK
        uuid user_id FK
        varchar country
        varchar city
        varchar street
        varchar h3_index
        timestamptz created_at
    }

    order {
        uuid id PK
        uuid user_id FK
        uuid specialist_id FK
        varchar job_type
        varchar description
        float price
        boolean is_active
        enum status
        timestamptz created_at
        timestamptz completed_at
    }

    catalog {
        uuid id PK
        uuid specialist_id FK
        varchar job_type
        float price
        timestamptz created_at
    }

    comments {
        uuid id PK
        uuid user_id FK
        uuid specialist_id FK
        varchar comment
        timestamptz created_at
    }

    rate {
        uuid id PK
        uuid user_id FK
        uuid specialist_id FK
        int rate
        timestamptz created_at
    }

    messages {
        uuid id PK
        uuid order_id FK
        uuid sender_id FK
        varchar message
        timestamptz created_at
    }

    accreditation {
        uuid id PK
        uuid specialist_id FK
        varchar file_url
        timestamptz created_at
    }

    audit_log {
        uuid id PK
        uuid user_id FK
        enum action
        varchar detail
        varchar ip_address
        timestamptz created_at
    }

    h3_zone_stats {
        uuid id PK
        varchar h3_index
        int total_orders
        int completed_orders
        float avg_price
        int active_specialists
        timestamptz created_at
        timestamptz updated_at
    }

    users ||--o| specialist : "has"
    users ||--o| address : "has"
    users ||--o{ order : "creates"
    users ||--o{ comments : "writes"
    users ||--o{ rate : "gives"
    users ||--o{ messages : "sends"
    users ||--o{ audit_log : "logs"

    specialist ||--o{ order : "takes"
    specialist ||--o{ catalog : "creates"
    specialist ||--o{ comments : "receives"
    specialist ||--o{ rate : "receives"
    specialist ||--o{ accreditation : "has"

    order ||--o{ messages : "has"
```
