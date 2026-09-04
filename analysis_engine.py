import pandas as pd


class RetailAnalyzer:
    def __init__(self):
        self.products = pd.read_csv("data/products.csv")
        self.inventory = pd.read_csv("data/inventory.csv")
        self.sales = pd.read_csv("data/sales.csv")

        self.sales["date"] = pd.to_datetime(self.sales["date"])

    def get_inventory_status(self):
        data = self.inventory.merge(
            self.products,
            on="product_id",
            how="left"
        )

        data["status"] = "Healthy"

        data.loc[
            data["current_stock"] <= data["reorder_level"],
            "status"
        ] = "Low Stock"

        data.loc[
            data["current_stock"] >= data["target_stock"],
            "status"
        ] = "Overstocked"

        return data

    def get_low_stock(self):
        data = self.get_inventory_status()

        return data[
            data["status"] == "Low Stock"
        ][
            [
                "store_name",
                "product_name",
                "current_stock",
                "reorder_level",
                "target_stock"
            ]
        ]

    def get_overstock(self):
        data = self.get_inventory_status()

        return data[
            data["status"] == "Overstocked"
        ][
            [
                "store_name",
                "product_name",
                "current_stock",
                "target_stock"
            ]
        ]

    def get_sales_summary(self):
        summary = self.sales.groupby(
            "product_id"
        )["units_sold"].sum().reset_index()

        summary = summary.merge(
            self.products[
                ["product_id", "product_name", "unit_price"]
            ],
            on="product_id",
            how="left"
        )

        summary["revenue"] = (
            summary["units_sold"] * summary["unit_price"]
        )

        return summary.sort_values(
            "revenue",
            ascending=False
        )

    def get_sales_trends(self):
        latest_date = self.sales["date"].max()

        recent_start = latest_date - pd.Timedelta(days=6)
        previous_start = latest_date - pd.Timedelta(days=13)
        previous_end = latest_date - pd.Timedelta(days=7)

        recent = self.sales[
            self.sales["date"] >= recent_start
        ].groupby("product_id")["units_sold"].sum()

        previous = self.sales[
            (self.sales["date"] >= previous_start) &
            (self.sales["date"] <= previous_end)
        ].groupby("product_id")["units_sold"].sum()

        result = pd.DataFrame({
            "recent_sales": recent,
            "previous_sales": previous
        }).fillna(0)

        result["change_percent"] = (
            (result["recent_sales"] - result["previous_sales"])
            / result["previous_sales"].replace(0, 1)
        ) * 100

        result = result.reset_index()

        result = result.merge(
            self.products[
                ["product_id", "product_name"]
            ],
            on="product_id",
            how="left"
        )

        return result.sort_values(
            "change_percent",
            ascending=False
        )
    def get_stockout_risk(self):
        latest_date = self.sales["date"].max()
        recent_start = latest_date - pd.Timedelta(days=6)

        recent_sales = self.sales[
            self.sales["date"] >= recent_start
        ].groupby(
            ["store_id", "product_id"]
        )["units_sold"].sum().reset_index()

        recent_sales["daily_avg_sales"] = (
            recent_sales["units_sold"] / 7
        )

        data = self.inventory.merge(
            self.products,
            on="product_id",
            how="left"
        )

        data = data.merge(
            recent_sales[
                ["store_id", "product_id", "daily_avg_sales"]
            ],
            on=["store_id", "product_id"],
            how="left"
        )

        data["daily_avg_sales"] = data["daily_avg_sales"].fillna(0)

        data["days_of_stock"] = data.apply(
            lambda row:
                row["current_stock"] / row["daily_avg_sales"]
                if row["daily_avg_sales"] > 0
                else 999,
            axis=1
        )

        data["risk_level"] = "Low"

        data.loc[
            data["days_of_stock"] <= 7,
            "risk_level"
        ] = "Medium"

        data.loc[
            data["days_of_stock"] <= 4,
            "risk_level"
        ] = "High"

        data.loc[
            data["days_of_stock"] <= 2,
            "risk_level"
        ] = "Critical"

        data["recommended_reorder"] = (
            data["target_stock"] - data["current_stock"]
        ).clip(lower=0)

        return data[
            data["risk_level"] != "Low"
        ][
            [
                "store_name",
                "product_name",
                "current_stock",
                "daily_avg_sales",
                "days_of_stock",
                "risk_level",
                "recommended_reorder"
            ]
        ].sort_values(
            "days_of_stock"
        )
    def get_recommendations(self):
        risk = self.get_stockout_risk()

        recommendations = []

        for _, row in risk.iterrows():

            if row["risk_level"] == "Critical":
                action = "Urgently reorder"
                priority = "Critical"

            elif row["risk_level"] == "High":
                action = "Reorder soon"
                priority = "High"

            else:
                action = "Monitor inventory"
                priority = "Medium"

            recommendations.append({
                "store": row["store_name"],
                "product": row["product_name"],
                "current_stock": int(row["current_stock"]),
                "daily_demand": round(row["daily_avg_sales"], 2),
                "days_remaining": round(row["days_of_stock"], 1),
                "risk": row["risk_level"],
                "recommended_order": int(row["recommended_reorder"]),
                "priority": priority,
                "action": action
            })

        return pd.DataFrame(recommendations)
    def get_slow_moving(self):
        """Identify products with consistently low sales velocity."""

        sales = self.sales.copy()

        product_sales = (
            sales.groupby("product_id")["units_sold"]
            .sum()
            .reset_index()
        )

        product_sales["daily_avg_sales"] = (
            product_sales["units_sold"] / sales["date"].nunique()
        )

        slow = product_sales[
            product_sales["daily_avg_sales"] <= 2.5
        ].copy()

        slow = slow.merge(
            self.products[["product_id", "product_name", "category"]],
            on="product_id",
            how="left"
        )

        slow["status"] = "Slow Moving"

        return slow[
            [
                "product_id",
                "product_name",
                "category",
                "units_sold",
                "daily_avg_sales",
                "status"
            ]
        ].sort_values(
            "daily_avg_sales"
        ).reset_index(drop=True)
    def get_attention_items(self):
        trends = self.get_sales_trends()

        trends["alert"] = ""

        trends.loc[
            trends["change_percent"] >= 50,
            "alert"
        ] = "Sales Spike"

        trends.loc[
            trends["change_percent"] <= -40,
            "alert"
        ] = "Sales Drop"

        return trends[
            trends["alert"] != ""
        ]


if __name__ == "__main__":
    analyzer = RetailAnalyzer()

    print("\nLOW STOCK")
    print(analyzer.get_low_stock().to_string(index=False))

    print("\nOVERSTOCK")
    print(analyzer.get_overstock().to_string(index=False))

    print("\nSALES SUMMARY")
    print(analyzer.get_sales_summary().head(10).to_string(index=False))

    print("\nATTENTION ITEMS")
    print(analyzer.get_attention_items().to_string(index=False))
    print("\nSTOCK-OUT RISK")
    print(analyzer.get_stockout_risk().to_string(index=False))
    print("\nRECOMMENDATIONS")
    print(analyzer.get_recommendations().to_string(index=False))
    