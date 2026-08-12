# Retail Automation

An end-to-end retail data automation system built using Python, MySQL, and QueueBuster APIs.

The project is being developed to collect, process, and organize inventory, master data, and sales information from multiple retail stores. It uses modular ETL workflows, a MySQL database, incremental sales processing, transaction management, logging, and Power BI exports.

The current focus is on building a reliable foundation for inventory and sales automation, with an alert system being the next part of the workflow.

---

## Features

### Master Data

Synchronizes core retail master data from QueueBuster APIs:

- Stores
- Categories
- Sub Categories
- Brands
- Products

### Inventory ETL

- Multi-store inventory collection
- Inventory API integration
- Inventory response parsing
- Inventory snapshot history
- Inventory status tracking
- ETL run tracking
- Power BI dataset export

### Sales ETL

- QueueBuster Sales API integration
- Historical sales backfill
- Incremental sales processing
- Sales response parsing
- Sales repository layer
- Transaction-based database operations
- Sales workflow and run tracking

### Database & ETL Management

- MySQL-backed relational database
- Repository-based database architecture
- Transaction management
- Rollback support
- ETL run tracking
- Structured logging
- Exception handling
- Modular workflow design

### Testing

The project includes tests for:

- Database connectivity
- Master API workflow
- ETL run tracking
- Sales checkpoints
- Incremental sales processing
- Sales repository operations
- Sales workflow

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
```text
Retail_Automation/
│
├── Inventory_API/
│   ├── config/
│   ├── logs/
│   ├── output/
│   ├── inventory_workflow.py
│   ├── qb_inventory_api.py
│   └── run_inventory.py
│
├── Master_API/
│   ├── master_workflow.py
│   ├── qb_brand_api.py
│   ├── qb_category_api.py
│   ├── qb_product_api.py
│   ├── qb_subcategory_api.py
│   └── run_master.py
│
├── Sales_API/
│   ├── __init__.py
│   ├── backfill_sales.py
│   ├── qb_sales_api.py
│   ├── run_sales.py
│   └── sales_workflow.py
│
├── shared/
│   │
│   ├── database/
│   │   ├── repositories/
│   │   │   ├── alert_repository.py
│   │   │   ├── brand_repository.py
│   │   │   ├── category_repository.py
│   │   │   ├── inventory_repository.py
│   │   │   ├── product_barcode_repository.py
│   │   │   ├── product_repository.py
│   │   │   ├── run_repository.py
│   │   │   ├── sales_repository.py
│   │   │   ├── store_repository.py
│   │   │   └── sub_category_repository.py
│   │   │
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── schema.sql
│   │   └── seed.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── api_client.py
│       ├── auth.py
│       ├── brand_parser.py
│       ├── category_parser.py
│       ├── config.py
│       ├── constants.py
│       ├── exporter.py
│       ├── inventory_parser.py
│       ├── logger.py
│       ├── product_parser.py
│       ├── sales_parser.py
│       ├── store_loader.py
│       └── sub_category_parser.py
│
├── tests/
│   ├── test_connection.py
│   ├── test_master_api.py
│   ├── test_run.py
│   ├── test_sales_checkpoint.py
│   ├── test_sales_incremental.py
│   ├── test_sales_repository.py
│   └── test_sales_workflow.py
│
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```
## Current Architecture

The project is organized around three main ETL workflows:

                    QueueBuster APIs
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
      Master API      Inventory API     Sales API
          │               │               │
          ▼               ▼               ▼
    Master Workflow  Inventory Workflow  Sales Workflow
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                       MySQL
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
        Historical Data           ETL Monitoring
             │
             ▼
       Dataset Export
             │
             ▼
          Power BI



## ETL Flow
Master Data
