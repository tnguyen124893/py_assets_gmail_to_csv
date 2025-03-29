import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

# Read and process the data
data = []
with open('extracted_text.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('Ngày'):
            i += 1  # Skip header
            if i < len(lines):
                values = lines[i].strip().split('| ')
                if len(values) >= 5:
                    record = {
                        'Ngày': values[0].strip(),
                        'Giá CCQ': values[1].strip(),
                        'SL CCQ sở hữu': values[2].strip(),
                        'Giá trị tài sản hiện tại': values[3].strip(),
                        'Tỷ lệ lãi lỗ trên vốn': values[4].strip()
                    }
                    data.append(record)
        i += 1

# Convert to DataFrame
df = pd.DataFrame(data)

logging.info("\nFirst few rows of raw DataFrame:")
logging.info(df.head())

# Convert date strings to datetime
df['Ngày'] = pd.to_datetime(df['Ngày'], format='%d/%m/%Y')

# Convert numeric columns with proper handling of thousands separator
df['Giá CCQ'] = df['Giá CCQ'].str.replace(',', '').astype(int)
df['SL CCQ sở hữu'] = df['SL CCQ sở hữu'].str.replace(',', '').astype(int)
df['Giá trị tài sản hiện tại'] = df['Giá trị tài sản hiện tại'].str.replace(',', '').astype(int)
df['Tỷ lệ lãi lỗ trên vốn'] = df['Tỷ lệ lãi lỗ trên vốn'].str.rstrip('%').astype(float)

# Sort by date
df = df.sort_values('Ngày')

# Calculate 7-day moving average
df['MA7'] = df['Giá trị tài sản hiện tại'].rolling(window=7, min_periods=1).mean()

# Filter out records where current value is more than 100% higher than moving average
df = df[df['Giá trị tài sản hiện tại'] <= (df['MA7'] * 2)]

# Drop the MA7 column as it's no longer needed
df = df.drop('MA7', axis=1)

# Calculate changes in number of shares
df['SL_Change'] = df['SL CCQ sở hữu'].diff().fillna(0)

# Calculate total invested capital
df['Additional_Investment'] = df.apply(lambda row: row['SL_Change'] * row['Giá CCQ'] if row['SL_Change'] > 0 else 0, axis=1)
df['Cumulative_Investment'] = df['Additional_Investment'].cumsum()

# Calculate Return on Capital
df['ROC'] = ((df['Giá trị tài sản hiện tại'] - df['Cumulative_Investment']) / df['Cumulative_Investment'] * 100).round(2)

# Log investment events
investment_dates = df[df['SL_Change'] > 0]['Ngày']
if not investment_dates.empty:
    logging.info("\nInvestment Events:")
    for date in investment_dates:
        row = df[df['Ngày'] == date].iloc[0]
        logging.info(f"Date: {date.strftime('%d/%m/%Y')}")
        logging.info(f"Additional Shares: {row['SL_Change']:,.0f}")
        logging.info(f"Investment Amount: {row['Additional_Investment']:,.0f} VND")
        logging.info(f"Share Price: {row['Giá CCQ']:,.0f} VND")
        logging.info("---")

logging.info("\nFirst few rows after processing and filtering:")
logging.info(df.head())

# Calculate growth metrics
initial_value = df['Giá trị tài sản hiện tại'].iloc[0]
final_value = df['Giá trị tài sản hiện tại'].iloc[-1]
total_growth = ((final_value - initial_value) / initial_value) * 100
total_days = (df['Ngày'].iloc[-1] - df['Ngày'].iloc[0]).days
annualized_return = ((1 + total_growth/100) ** (365/total_days) - 1) * 100

# Calculate monthly returns
df['Month'] = df['Ngày'].dt.to_period('M')
monthly_returns = df.groupby('Month')['Giá trị tài sản hiện tại'].agg(['first', 'last'])
monthly_returns['return'] = ((monthly_returns['last'] - monthly_returns['first']) / monthly_returns['first'] * 100)

# Create the report
report = f"""
Investment Growth Report
=======================

Period: {df['Ngày'].iloc[0].strftime('%d/%m/%Y')} to {df['Ngày'].iloc[-1].strftime('%d/%m/%Y')}
Duration: {total_days} days

Initial Investment: {initial_value:,.0f} VND
Final Value: {final_value:,.0f} VND
Total Growth: {total_growth:.2f}%
Annualized Return: {annualized_return:.2f}%

Key Statistics:
-------------
Highest Value: {df['Giá trị tài sản hiện tại'].max():,.0f} VND
Lowest Value: {df['Giá trị tài sản hiện tại'].min():,.0f} VND
Average Value: {df['Giá trị tài sản hiện tại'].mean():,.0f} VND

Number of Units:
---------------
Initial Units: {df['SL CCQ sở hữu'].iloc[0]:,.0f}
Final Units: {df['SL CCQ sở hữu'].iloc[-1]:,.0f}
Unit Change: {df['SL CCQ sở hữu'].iloc[-1] - df['SL CCQ sở hữu'].iloc[0]:,.0f}

Price Analysis:
-------------
Initial Price: {df['Giá CCQ'].iloc[0]:,.0f} VND
Final Price: {df['Giá CCQ'].iloc[-1]:,.0f} VND
Price Change: {((df['Giá CCQ'].iloc[-1] - df['Giá CCQ'].iloc[0]) / df['Giá CCQ'].iloc[0] * 100):.2f}%

Return Analysis:
--------------
Best Monthly Return: {monthly_returns['return'].max():.2f}%
Worst Monthly Return: {monthly_returns['return'].min():.2f}%
Average Monthly Return: {monthly_returns['return'].mean():.2f}%

Investment Strategy Analysis:
--------------------------
Total Units Acquired: {df['SL CCQ sở hữu'].max() - df['SL CCQ sở hữu'].min():,.0f}
Average Unit Price: {df['Giá CCQ'].mean():,.0f} VND
Price Volatility: {df['Giá CCQ'].std():,.0f} VND
"""

# Save the report
with open('investment_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

# Create visualizations
plt.style.use('default')  # Use default style instead of seaborn
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

# Plot 1: Asset Value Over Time
# ax1.plot(df['Ngày'], df['Giá trị tài sản hiện tại'], linewidth=2)
# ax1.set_title('Total Asset Value Over Time')
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Asset Value (VND)')
# ax1.grid(True)
# ax1.tick_params(axis='x', rotation=45)

# Plot 2: Number of Units and Price
# ax2.plot(df['Ngày'], df['SL CCQ sở hữu'], label='Number of Units', linewidth=2)
# ax2_twin = ax2.twinx()
# ax2_twin.plot(df['Ngày'], df['Giá CCQ'], label='Unit Price', color='orange', linewidth=2)
# ax2.set_title('Number of Units and Unit Price Over Time')
# ax2.set_xlabel('Date')
# ax2.set_ylabel('Number of Units')
# ax2_twin.set_ylabel('Unit Price (VND)')
# ax2.grid(True)
# ax2.tick_params(axis='x', rotation=45)

# Plot 3: Returns Over Time
ax3.plot(df['Ngày'], df['Tỷ lệ lãi lỗ trên vốn'], label='Tỷ lệ lãi lỗ trên vốn', color='blue', linewidth=2)
ax3.plot(df['Ngày'], df['ROC'], label='Return on Capital', color='red', linewidth=2)
ax3.set_title('Investment Returns Over Time')
ax3.set_xlabel('Date')
ax3.set_ylabel('Return (%)')
ax3.grid(True)
ax3.tick_params(axis='x', rotation=45)
ax3.legend()

# Add legends for Plot 2
# lines1, labels1 = ax2.get_legend_handles_labels()
# lines2, labels2 = ax2_twin.get_legend_handles_labels()
# ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# Adjust layout
plt.tight_layout()
plt.savefig('investment_growth.png')
plt.close()

print("\nReport generated! Check 'investment_report.txt' and 'investment_growth.png' for details.") 