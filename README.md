# Retail Automation

An end-to-end retail inventory automation system built using Python, MySQL, and QueueBuster APIs.
The project automates inventory collection from multiple retail stores, synchronizes master data into a relational database, maintains historical inventory snapshots, exports Power BI-ready datasets, and provides a production-ready ETL workflow with logging and transaction management.

---

## Features

- QueueBuster Inventory API integration
- Multi-store inventory collection
- Automatic synchronization of:
  - Stores
  - Categories
  - Sub Categories
  - Brands
  - Products
- Inventory snapshot history
- Run tracking and ETL monitoring
- MySQL-backed data warehouse
- CSV export for Power BI
- Structured logging
- Transaction management with rollback support
- Modular ETL workflow
- Exception handling and failure recovery

---

## Tech Stack

- Python
- Pandas
- MySQL
- QueueBuster REST APIs
- Power BI
- Git & GitHub

---

## Project Structure

```
Retail_Automation/
├── Inventory_API/
│   ├── qb_inventory_api.py
│   ├── inventory_workflow.py
│   └── run_inventory.py
├── shared/
│   ├── database/
│   │   ├── connection.py
│   │   ├── schema.sql
│   │   ├── seed.py
│   │   └── repositories/
│   │       ├── alert_repository.py
│   │       ├── brand_repository.py
│   │       ├── category_repository.py
│   │       ├── inventory_repository.py
│   │       ├── product_repository.py
│   │       ├── run_repository.py
│   │       ├── store_repository.py
│   │       └── sub_category_repository.py
│   ├── utils/
│   ├── api_client.py
│   ├── auth.py
│   ├── config.py
│   ├── constants.py
│   ├── exporter.py
│   ├── inventory_parser.py
│   ├── logger.py
│   └── store_loader.py
├── logs/
├── output/
├── main.py
└── requirements.txt
```

---

## Current Workflow

```
QueueBuster API
      │
      ▼
Partner Authentication
      │
      ▼
Fetch Inventory
      │
      ▼
Parse API Response
      │
      ▼
Synchronize Master Tables
      │
      ▼
Store Inventory Snapshot
      │
      ▼
Export CSV
      │
      ▼
Power BI
```

---

## Database Design

Current database includes:

- inventory_run
- inventory_snapshot
- store
- category
- sub_category
- brand
- product
- inventory_status

---

## Reliability Features

- Transaction-based ETL
- Automatic rollback on failure
- Run status tracking
- Structured logging
- Exception handling
- Modular workflow architecture
- Master data synchronization

---

## Current Status

### Completed
- Inventory ETL
- Master Data Synchronization
- Inventory Snapshot History
- Power BI Dataset Export
- Transaction Management
- Logging & Run Monitoring

### Planned
- Inventory Alert Engine
- Sales ETL
- Purchase ETL
- Telegram Notifications
- Automated Scheduling
- Power BI Executive Dashboard

---

## License

MIT License
