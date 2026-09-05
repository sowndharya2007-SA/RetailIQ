TRACK_ID=PS03

# RetailIQ - Sales & Inventory Copilot

RetailIQ is an AI-powered sales and inventory copilot for small retail businesses.

It combines deterministic retail analytics with Gemini to answer manager questions using verified sales and inventory data.

## Features

- Inventory status across multiple stores
- Low-stock detection
- Stock-out risk prediction
- Slow-moving product detection
- Sales spike and drop detection
- Monthly sales and revenue performance
- Automated reorder recommendations
- Natural-language questions using Gemini
- Verified evidence shown with every AI answer
- Graceful handling of unsupported questions
- Live dashboard monitoring with automatic refresh

## Tech Stack

- Python
- Flask
- Pandas
- Google Gemini API
- HTML
- CSS
- JavaScript
- CSV-based retail data

## Project Structure

```text
RetailIQ/
├── app.py
├── analysis_engine.py
├── gemini_service.py
├── generate_sales.py
├── requirements.txt
├── README.md
├── data/
│   ├── products.csv
│   ├── inventory.csv
│   └── sales.csv
├── templates/
│   └── index.html
└── static/
    └── style.css