# Bond Calculator and Comparator

This Streamlit-based web application allows users to calculate key bond metrics such as Yield to Maturity (YTM), Duration, Net Total Return after tax, and the YTM/Duration ratio. It also offers a comparison tool for multiple bonds, allowing investors to analyze bonds and sort them by their attractiveness (YTM/Duration ratio).

## Key Features:
- **Yield to Maturity (YTM) after tax**: Calculates the annualized return considering taxes.
- **Duration**: Measures the bond's sensitivity to interest rate changes.
- **Net Total Return after tax**: Calculates the overall return after accounting for taxes.
- **YTM/Duration Ratio**: Compares the return relative to the bond's interest rate risk, highlighting bonds that provide the best return per unit of risk.
- **Bond Comparison**: Compare up to 20 bonds and sort them by the YTM/Duration ratio.

## Usage:
1. **Bond Metrics Section**: Enter the bond details (Face Value, Price, Coupon Rate, Tax Rate, and Years to Maturity) to calculate the YTM after tax, Duration, and Net Total Return after tax.
2. **Bond Comparison Section**: Enter details for multiple bonds (up to 20) and calculate their YTM after tax, Duration, and YTM/Duration ratio. The bonds are sorted in descending order based on their YTM/Duration ratio.

## Requirements

To run the application, you will need:
- Python 3.8+
- Streamlit
- pandas
- numpy
- scipy
