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