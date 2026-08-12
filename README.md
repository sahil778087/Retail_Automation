# Retail Automation

## Overview

Retail Automation is a modular Python-based automation platform designed to integrate with the QueueBuster ERP system using REST APIs. The objective of the project is to automate data extraction, processing, and reporting for retail operations, replacing manual workflows with scheduled data pipelines.

The extracted data is transformed into analytics-ready datasets that are directly consumed by Power BI dashboards for operational monitoring and decision-making.

---

## Current Module

### Inventory API

The Inventory module retrieves stock information for all configured stores using the QueueBuster Inventory API.

Current workflow:

1. Generate Partner Token
2. Load configured store IDs
3. Fetch inventory for each store
4. Parse and flatten API responses
5. Export a consolidated CSV dataset
6. Refresh Power BI using the generated dataset

---

## Project Structure

```
Retail_Automation/
│
├── Inventory_API/
│   ├── config/
│   ├── logs/
│   ├── output/
│   ├── qb_inventory_api.py
│   └── run_inventory.py
│
├── shared/
│   ├── api_client.py
│   ├── auth.py
│   ├── config.py
│   ├── exporter.py
│   ├── inventory_parser.py
│   ├── logger.py
│   └── store_loader.py
│
├── .env
├── main.py
├── requirements.txt
└── README.md
```

---

## Features

- Automated QueueBuster Partner Token generation
- Multi-store inventory extraction
- JSON response parsing and flattening
- CSV generation for Power BI
- Modular project architecture
- Environment variable configuration
- Shared utility modules for reuse
- Version controlled using Git

---

## Technology Stack

- Python
- Requests
- Pandas
- QueueBuster REST API
- Power BI
- Git

---

## Current Version

**Version 1.0**

Implemented features:

- Partner authentication
- Inventory API integration
- Store-wise inventory extraction
- Inventory data parser
- CSV export pipeline
- Power BI compatible output

---

## Planned Enhancements

### Version 2

- Structured logging
- Retry mechanism for failed API calls
- Improved project architecture
- Execution summary reports
- Better exception handling

### Future Modules

- Sales API
- Purchase API
- Customer API
- Product API
- Automated Inventory Alerts
- Power BI Dataset Refresh
- Email Notifications
- Inventory Forecasting
- Demand Prediction
- Automated Report Distribution

---

## Project Status

### ✅ Version 1.0
- QueueBuster Inventory API
- CSV Export
- Power BI Dashboard

### ✅ Version 2.1
- MySQL ETL Pipeline
- Master Data Synchronization
- Inventory Snapshot History
- Inventory Run Tracking
- Canonical Data Model

### 🚧 Next (Version 2.2)
- Structured Logging
- Transaction Management
- Inventory Alert Engine
- Telegram Notifications

## License

This project is intended for educational and internal development purposes.
