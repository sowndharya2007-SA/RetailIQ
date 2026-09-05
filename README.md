TRACK_ID=PS03

# RetailIQ - Sales & Inventory Copilot

RetailIQ is an AI-powered sales and inventory copilot for small retail businesses.

It combines deterministic retail analytics with Gemini to answer manager questions using verified sales and inventory data.

## Features

- Sales performance analysis
- Low-stock detection
- Stock-out risk prediction
- Slow-moving product detection
- Sales spike and drop detection
- Monthly sales performance
- Inventory-based reorder recommendations
- Natural-language questions using Gemini
- Verified evidence shown with every AI answer
- Graceful handling of unsupported questions
- Fallback to verified retail analysis when the AI service is unavailable
- Manager approval reminder for AI recommendations

## Tech Stack

- Python 3.11
- Flask
- Pandas
- Google Gemini API
- HTML
- CSS
- JavaScript
- CSV-based retail data

## Project Structure

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

## How to Run

Create and activate a Python virtual environment, then install the dependencies.

pip install -r requirements.txt

Create a `.env` file with:

GEMINI_API_KEY=your_api_key_here

Start the application:

python app.py

The application runs on:

http://localhost:8000

## Data

RetailIQ uses locally generated retail data containing:

- 3 stores
- 20 products
- Daily sales records
- Current inventory levels
- Product pricing
- Reorder levels
- Target stock levels

The generated sales dataset contains 2,100 sales records.

## How the AI Works

RetailIQ first performs deterministic analysis on the local retail dataset.

Depending on the manager's question, the system selects the relevant verified evidence such as:

- Stock-out risk
- Sales trends
- Slow-moving stock
- Monthly performance
- Reorder recommendations
- Sales summaries

The verified evidence is then provided to Gemini.

Gemini generates a concise manager-friendly explanation using only the supplied evidence.

The system does not allow the AI to invent missing retail facts. Unsupported questions are rejected when the available retail data cannot answer them.

## Verified Evidence

Every AI response includes the underlying verified retail data used to generate the answer.

This improves transparency and allows the store manager to validate the numbers before taking action.

## Human-in-the-Loop

AI recommendations are decision-support suggestions.

Store managers should review and approve recommendations before placing orders or making operational changes.

## Demo Video

Demo video link:

ADD_DEMO_VIDEO_LINK_HERE