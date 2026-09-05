from flask import Flask, jsonify, request, render_template
import json
import pandas as pd

from analysis_engine import RetailAnalyzer
from gemini_service import GeminiService


app = Flask(__name__)

# Initialize the deterministic retail analysis engine once.
analyzer = RetailAnalyzer()
gemini = GeminiService()


def to_json_records(data):
    """Convert pandas or Python data into JSON-safe data."""
    if isinstance(data, pd.DataFrame):
        return data.replace({pd.NA: None}).to_dict(orient="records")

    if isinstance(data, dict):
        return data

    if isinstance(data, list):
        return data

    return data
def build_evidence(question):
    question_lower = question.lower()
    """
    Select the deterministic analysis most relevant to the
    manager's question.
    """
    q = question.lower()

    if any(word in q for word in [
        "stockout",
        "stock out",
        "run out",
        "running out",
        "days of stock",
        "stock risk"
    ]):
        return {
            "analysis_type": "stockout_risk",
            "data": to_json_records(
                analyzer.get_stockout_risk()
            )
        }

    if any(word in q for word in [
        "overstock",
        "overstocked",
        "too much stock",
        "excess stock",
        "excess inventory"
    ]):
        return {
            "analysis_type": "overstock",
            "data": to_json_records(
                analyzer.get_overstock()
            )
        }

    if any(word in q for word in [
        "low stock",
        "low inventory",
        "below reorder",
        "reorder level",
        "low items"
    ]):
        return {
            "analysis_type": "low_stock",
            "data": to_json_records(
                analyzer.get_low_stock()
            )
        }
    if any(word in question_lower for word in [
        "monthly",
        "month",
        "monthly performance"
    ]):
        return {
            "analysis_type": "monthly_performance",
            "data": to_json_records(
                analyzer.get_monthly_performance()
            )
        }

    if any(word in q for word in [
        "spike",
        "drop",
        "trend",
        "trending",
        "increasing",
        "decreasing",
        "sales change",
        "sales changes"
    ]):
        return {
            "analysis_type": "sales_trends",
            "data": to_json_records(
                analyzer.get_sales_trends()
            )
        }
    if "slow" in q or "slow-moving" in q or "slow moving" in q:
        return {
        "analysis_type": "slow_moving",
        "data": to_json_records(
            analyzer.get_slow_moving()
        )
    }

    if any(word in q for word in [
        "recommend",
        "recommendation",
        "what should i do",
        "what should we do",
        "what action",
        "action should"
    ]):
        return {
            "analysis_type": "recommendations",
            "data": to_json_records(
                analyzer.get_recommendations()
            )
        }

    # General retail/sales questions use the sales summary.
    if any(word in q for word in [
        "sales",
        "sold",
        "revenue",
        "performance",
        "top product",
        "best selling",
        "best-selling",
        "product",
        "products",
        "store",
        "stores",
        "inventory",
        "stock",
        "monthly",
        "daily"
    ]):
        return {
            "analysis_type": "sales_summary",
            "data": to_json_records(
                analyzer.get_sales_summary()
            )
        }

    # The dataset cannot answer unrelated questions.
    return None
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "RetailIQ"
    })


@app.route("/api/dashboard")
def dashboard():
    """Return verified retail metrics for the dashboard."""
    try:
        result = {
            "inventory": to_json_records(
                analyzer.get_inventory_status()
            ),
            "low_stock": to_json_records(
                analyzer.get_low_stock()
            ),
            "overstock": to_json_records(
                analyzer.get_overstock()
            ),
            "sales_summary": to_json_records(
                analyzer.get_sales_summary()
            ),
            "sales_trends": to_json_records(
                analyzer.get_sales_trends()
            ),
            "attention_items": to_json_records(
                analyzer.get_attention_items()
            ),
            "stockout_risk": to_json_records(
                analyzer.get_stockout_risk()
            ),
            "recommendations": to_json_records(
                analyzer.get_recommendations()
            ),
            "slow_moving": to_json_records(
                analyzer.get_slow_moving()
            ),
            "monthly_performance": to_json_records(
                analyzer.get_monthly_performance()
            )

        }

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Unable to load dashboard data.",
            "details": str(error)
        }), 500
@app.route("/api/ask", methods=["POST"])
def ask():
    """Answer a manager question using verified retail evidence."""
    try:
        body = request.get_json(silent=True) or {}
        question = body.get("question", "").strip()

        if not question:
            return jsonify({
                "status": "error",
                "message": "Please provide a question."
            }), 400

        evidence = build_evidence(question)
        if evidence is None:
            return jsonify({
                "status": "unsupported",
                "question": question,
                "message": "I don't have enough retail data to answer that question."
            }), 200

        data_context = json.dumps(
            evidence,
            indent=2,
            default=str
        )

        answer = gemini.ask(
            question,
            data_context
        )

        return jsonify({
            "status": "success",
            "question": question,
            "analysis_type": evidence["analysis_type"],
            "answer": answer,
            "evidence": evidence["data"]
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Unable to answer the question.",
            "details": str(error)
        }), 500
    

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )