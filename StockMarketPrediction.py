import yfinance as yf
import pandas as pd
from prophet import Prophet
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Define the list of stock tickers and quantities
stock_data = [
    {"Instrument": "SPIC.BO", "Qty": 1020, "Avg_cost": 101.15},
    {"Instrument": "RTNPOWER.BO", "Qty": 17000, "Avg_cost": 10.56},
    {"Instrument": "RALLIS.BO", "Qty": 400, "Avg_cost": 264.40},
    {"Instrument": "PNB.BO", "Qty": 400, "Avg_cost": 117.90},
    {"Instrument": "PENIND.BO", "Qty": 650, "Avg_cost": 153.30},
    {"Instrument": "JIOFIN.BO", "Qty": 140, "Avg_cost": 347.32},
    {"Instrument": "IRCON.BO", "Qty": 260, "Avg_cost": 187.85},
    {"Instrument": "GREENPOWER.BO", "Qty": 8600, "Avg_cost": 23.55},
    {"Instrument": "BPCL.BO", "Qty": 180, "Avg_cost": 565.33},
    {"Instrument": "BAJAJHIND.BO", "Qty": 1000, "Avg_cost": 38.25},
    {"Instrument": "ACC.BO", "Qty": 10, "Avg_cost": 2687.25}
]

def fetch_and_predict(stock):
    try:
        ticker = yf.Ticker(stock["Instrument"])
        data = ticker.history(period="5y")
        if data.empty:
            raise ValueError("No data found, symbol may be delisted")

        data.reset_index(inplace=True)

        df = data[['Date', 'Close']].copy()
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone information
        df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)

        # Initialize Prophet model and fit the data
        model = Prophet()
        model.fit(df)

        # Make future dataframe for next 5 months
        future = model.make_future_dataframe(periods=5 * 30)
        forecast = model.predict(future)

        # Get the predictions for the next 5 months
        prediction = forecast[['ds', 'yhat']].tail(5)
        prediction.set_index('ds', inplace=True)

        stock["LTP"] = round(data["Close"].iloc[-1], 2)
        stock["Cur_val"] = round(stock["LTP"] * stock["Qty"], 2)
        stock["P&L"] = round(((stock["LTP"] - stock["Avg_cost"]) / stock["Avg_cost"]) * 100, 2)

        for i, date in enumerate(prediction.index):
            stock[f"Month_{i + 1}"] = round(prediction.loc[date, "yhat"] * stock["Qty"], 2)

    except Exception as e:
        print(f"Error fetching data for {stock['Instrument']}: {e}")
        stock["LTP"] = stock["Cur_val"] = stock["P&L"] = "N/A"
        for i in range(1, 6):
            stock[f"Month_{i}"] = "N/A"

# Fetch and predict stock data
for stock in stock_data:
    fetch_and_predict(stock)

# Calculate total current value and total percentage change
total_cur_val = 0
total_invested = 0

for stock in stock_data:
    if stock["Cur_val"] != 'N/A':
        cur_val = float(stock["Cur_val"]) if isinstance(stock["Cur_val"], str) else stock["Cur_val"]
        stock["Cur_val"] = cur_val
        total_cur_val += stock["Cur_val"]
    total_invested += stock["Avg_cost"] * stock["Qty"]

total_PL = round(((total_cur_val - total_invested) / total_invested) * 100, 2)

# Create Tkinter window
root = tk.Tk()
root.title("Stock Market Data with Forecast")

# Create a frame for the table and chart
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

# Create Treeview for the table
tree = ttk.Treeview(frame, columns=("Instrument", "Qty", "Avg. cost", "LTP", "Cur. val", "P&L",
                                   "Month 1", "Month 2", "Month 3", "Month 4", "Month 5"), show='headings')

# Define column widths and alignments
tree.column("Instrument", width=100, anchor="center")
tree.column("Qty", width=60, anchor="center")
tree.column("Avg. cost", width=80, anchor="center")
tree.column("LTP", width=80, anchor="center")
tree.column("Cur. val", width=100, anchor="center")
tree.column("P&L", width=80, anchor="center")
tree.column("Month 1", width=100, anchor="center")
tree.column("Month 2", width=100, anchor="center")
tree.column("Month 3", width=100, anchor="center")
tree.column("Month 4", width=100, anchor="center")
tree.column("Month 5", width=100, anchor="center")

# Define column headings
tree.heading("Instrument", text="Instrument")
tree.heading("Qty", text="Quantity")
tree.heading("Avg. cost", text="Average Cost")
tree.heading("LTP", text="Last Traded Price")
tree.heading("Cur. val", text="Current Value")
tree.heading("P&L", text="P&L (%)")
tree.heading("Month 1", text="Month 1")
tree.heading("Month 2", text="Month 2")
tree.heading("Month 3", text="Month 3")
tree.heading("Month 4", text="Month 4")
tree.heading("Month 5", text="Month 5")

# Apply grid style
style = ttk.Style()
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
style.configure("Treeview", font=('Arial', 10), rowheight=25)

# Add alternating row colors
style.map('Treeview', background=[('alternate', 'sky blue')])

# Add data to Treeview
for i, stock in enumerate(stock_data):
    tag = 'even' if i % 2 == 0 else 'odd'
    values = (
        stock["Instrument"], stock["Qty"], f"{stock['Avg_cost']:.2f}",
        f"{stock['LTP']:.2f}" if isinstance(stock["LTP"], (int, float)) else stock["LTP"],
        f"{stock['Cur_val']:.2f}" if isinstance(stock["Cur_val"], (int,float)) else stock["Cur_val"],
        f"{stock['P&L']:.2f}%" if isinstance(stock["P&L"], (int, float)) else stock["P&L"],
        f"{stock['Month_1']:.2f}" if isinstance(stock["Month_1"], (int, float)) else stock["Month_1"],
        f"{stock['Month_2']:.2f}" if isinstance(stock["Month_2"], (int, float)) else stock["Month_2"],
        f"{stock['Month_3']:.2f}" if isinstance(stock["Month_3"], (int, float)) else stock["Month_3"],
        f"{stock['Month_4']:.2f}" if isinstance(stock["Month_4"], (int, float)) else stock["Month_4"],
        f"{stock['Month_5']:.2f}" if isinstance(stock["Month_5"], (int, float)) else stock["Month_5"]
    )
    item_id = tree.insert("", "end", values=values, tags=(tag,))

    # Highlight negative values in red for the prediction columns
    for j in range(6, 11):
        cell_value = tree.set(item_id, column=tree["columns"][j])
        if isinstance(cell_value, str) and cell_value != "N/A" and float(cell_value) < 0:
            tree.tag_configure(f'cell_{i}_{j}', foreground='red')
            tree.item(item_id, tags=(tag, f'cell_{i}_{j}'))

# Calculate total values for each month
total_month_values = [0] * 5
for stock in stock_data:
    for i in range(1, 6):
        month_key = f"Month_{i}"
        if isinstance(stock[month_key], (int, float)):
            total_month_values[i - 1] += stock[month_key]

# Add total row
total_values = ["Total", "", "", "", f"{total_cur_val:.2f}", f"{total_PL:.2f}%"]
for i in range(5):
    total_values.append(f"{total_month_values[i]:.2f}")

tree.insert("", "end", values=total_values,                   tags=('total',))

tree.tag_configure('total', background='lightgrey', font=('Arial', 10, 'bold'))

# Pack the treeview
tree.pack(fill="both", expand=True)

# Function to create and display the chart
def show_chart():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(1, 6), total_month_values, marker='o', linestyle='-', color='b')
    ax.set_title('Total Forecasted Values for Next 5 Months')
    ax.set_xlabel('Months')
    ax.set_ylabel('Total Value')
    ax.grid(True)

    # Embed the chart in the Tkinter window
    chart = FigureCanvasTkAgg(fig, frame)
    chart.get_tk_widget().pack(fill="both", expand=True)

# Button to show the chart
chart_button = tk.Button(frame, text="Show Chart", command=show_chart)
chart_button.pack()

root.mainloop()

