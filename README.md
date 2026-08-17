# Retail Automation

An end-to-end retail data automation system built with **Python, MySQL, and QueueBuster APIs** for automated retail data collection, processing, storage, inventory monitoring, and reporting.

## Features

- **Master Data ETL** — Stores, Categories, Subcategories, Brands, Products
- **Inventory ETL** — Multi-store inventory collection, snapshots, thresholds, and alerts
- **Sales ETL** — Historical backfill, incremental processing, checkpoints, orders, and payments
- **Inventory Alerts** — Low-stock and negative-stock detection with Telegram notifications
- **MySQL Database** — Repository-based architecture with transactions and rollback
- **ETL Run Tracking** — Run IDs, status tracking, processing statistics, and failure tracking
- **Structured Logging** — Daily logs stored in the root `logs/` directory
- **API Reliability** — Request timeouts and retry handling
- **Power BI Export** — Processed datasets prepared for reporting
- **Testing** — Database, API, workflow, checkpoint, and repository tests

## Architecture

```text
                    QueueBuster APIs
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Master API    Inventory API    Sales API
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                         ETL
                           │
                           ▼
                         MySQL
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Inventory       Sales        Master Data
             │
             ▼
       Alert Engine
             │
             ▼
        Telegram
             │
             ▼
          Power BI
```
## Project Structure

```text
Retail_Automation/
│
├── Inventory_API/
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
│   ├── backfill_sales.py
│   ├── qb_sales_api.py
│   ├── run_sales.py
│   └── sales_workflow.py
│
├── shared/
│   ├── database/
│   │   └── repositories/
│   ├── alert_evaluator.py
│   ├── alert_service.py
│   ├── api_client.py
│   ├── auth.py
│   ├── config.py
│   ├── logger.py
│   ├── notification_service.py
│   └── telegram_service.py
│
├── tests/
├── logs/
├── main.py
├── .gitignore
├── README.md
└── requirements.txt
```
## Running the ETL
From the project root:  

### Master data
python main.py master

### Sales
python main.py sales

### Sales for a specific date
python main.py sales 2026-08-18

### Inventory
python main.py inventory

### Run the complete pipeline
python main.py all

### Run complete pipeline for a specific sales date
python main.py all 2026-08-18

The all workflow runs:  Master → Sales → Inventory → Alerts

## Inventory Alert Lifecycle

```text
Inventory Data
      │
      ▼
Evaluate State
      │
 ┌────┼─────────┐
 ▼    ▼         ▼
Healthy  Zero  Critical/Negative
 │        │         │
 ▼        ▼         ▼
Resolve  Ignore   Create/Keep Open
 │                  │
 ▼                  ▼
Telegram          Telegram
```
Zero stock does not create a new alert because inventory audits may temporarily set stock to zero.

## Reliability

The system includes:

- Database transactions and rollback
- Incremental sales checkpoints
- API timeout and retry handling
- ETL run tracking
- Structured daily logging
- Exception handling
- Repository-based database access
- Alert history
- Notification history
- Environment-based configuration
- Separate development/sandbox and production configuration

## Technology Stack

Python · Pandas · MySQL · QueueBuster REST APIs · Power BI · Telegram · Git · GitHub

## License

MIT License
