import pandas as pd
import numpy as np
import streamlit as st
from scipy.optimize import newton
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Bond Calculator and Comparator", page_icon="📈", layout="wide")

st.markdown("""
    <p style="font-size: 12px; text-align: center;">
        Created by: <a href="https://www.linkedin.com/in/luca-girlando-775463302/" target="_blank">Luca Girlando</a>
    </p>
""", unsafe_allow_html=True)

# Function to calculate the Yield to Maturity (YTM) after tax
def calculate_ytm(face_value, price, coupon_rate, years_to_maturity, tax_rate, frequency=1):
    def ytm_func(ytm):
        # Calculate the present value of cash flows (coupons + face value)
        cash_flows = [
            coupon_rate * face_value / frequency / (1 + ytm / frequency) ** (frequency * t)
            for t in range(1, int(years_to_maturity * frequency) + 1)
        ]
        cash_flows.append(face_value / (1 + ytm / frequency) ** (frequency * years_to_maturity))
        total_value = sum(cash_flows)
        return total_value - price

    # Solve for YTM with an initial guess of 5%
    ytm = newton(ytm_func, 0.05)
    ytm_after_tax = ytm * (1 - tax_rate)
    return ytm_after_tax

# Function to calculate the Duration
def calculate_duration(face_value, coupon_rate, years_to_maturity, ytm, frequency=1):
    # Calculate the cash flows (coupons + face value at the last period)
    cash_flows = [
        coupon_rate * face_value / frequency for _ in range(int(years_to_maturity * frequency))
    ]
    cash_flows[-1] += face_value  # Add the face value to the last period
    
    # Calculate the present values of the cash flows
    present_values = [
        cf / (1 + ytm / frequency) ** (i + 1) for i, cf in enumerate(cash_flows)
    ]
    
    # Calculate the weighted average
    weighted_avg = sum((i + 1) * pv for i, pv in enumerate(present_values)) / sum(present_values)
    return weighted_avg / frequency

# Function to calculate the Total Return after tax using the new formula
def calculate_total_return(face_value, coupon_rate, price, years_to_maturity, tax_rate, frequency=1):
    # Calculate the total coupon payments (net of tax)
    total_coupon = sum([ 
        coupon_rate * face_value / frequency * (1 - tax_rate) for _ in range(int(years_to_maturity * frequency))
    ])
    
    # Calculate the capital gain (final price - initial price)
    capital_gain = face_value - price
    
    # Calculate the net total return using the formula
    total_return_net = (total_coupon + capital_gain) / price
    
    return total_return_net

# Function to calculate YTM/Duration Ratio
def calc_ytm_duration_ratio(ytm, duration):
    return ytm / duration if duration != 0 else 0

# Function to calculate Years to Maturity from two dates
def calculate_years_to_maturity(purchase_date, maturity_date):
    # Calculate the difference between the purchase and maturity dates in years
    delta = maturity_date - purchase_date
    return delta.days / 365.25

# Main Streamlit function
def main():
    st.title("Bond Calculator and Comparator")

    # Section 1: Bond Metrics
    st.markdown("""
    ### Bond Metrics: Duration, YTM After Taxes, and Net Total Return

    In this section, you can calculate metrics for a single bond:
    - **Duration**: Measures interest rate sensitivity.
    - **YTM after tax**: Annualized return considering taxes.
    - **Net Total Return after tax**: Overall return after taxes.
    """)

    # Input for purchase date and maturity date
    purchase_date = st.date_input("Purchase Date")
    maturity_date = st.date_input("Maturity Date")

    # Calculate the Years to Maturity automatically
    if purchase_date and maturity_date:
        years_to_maturity_auto = calculate_years_to_maturity(purchase_date, maturity_date)
        st.write(f"**Years to Maturity:** {years_to_maturity_auto:.2f} years")
    else:
        years_to_maturity_auto = st.number_input("Years to Maturity", min_value=0.0, value=10.0, step=0.01)

    face_value = st.number_input("Face Value of Bond (€)", min_value=0.0, value=100.0, step=0.01)
    price = st.number_input("Current Purchase Price (€)", min_value=0.0, value=100.0, step=0.01)
    coupon_rate = st.number_input("Annual Coupon Rate (%)", min_value=0.0, max_value=100.0, value=5.0) / 100
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=12.5) / 100

    if st.button("Calculate Bond Metrics"):
        ytm_after_tax = calculate_ytm(face_value, price, coupon_rate, years_to_maturity_auto, tax_rate)
        duration = calculate_duration(face_value, coupon_rate, years_to_maturity_auto, ytm_after_tax)
        total_return_net = calculate_total_return(face_value, coupon_rate, price, years_to_maturity_auto, tax_rate)

        st.subheader("Bond Metrics Results:")
        st.write(f"**Duration:** {duration:.2f} years")
        st.write(f"**YTM after tax:** {ytm_after_tax * 100:.2f}%")
        st.write(f"**Net Total Return after tax:** {total_return_net * 100:.2f}%")

    # Section 2: Bond Comparison
    st.markdown("""
    ### Bond Comparison: YTM and Duration for Multiple Bonds

    Compare up to 20 bonds for the following metrics:
    - **YTM**: Annualized yield to maturity.
    - **Duration**: Sensitivity to interest rate changes.
    - **YTM/Duration Ratio**: Attractiveness relative to interest rate risk.

    The bonds will be sorted in descending order of the YTM/Duration ratio, meaning that the bonds with higher returns relative to their interest rate risk are listed first.
    """)

    bond_count = st.number_input("Number of Bonds to Compare", min_value=2, max_value=20, value=3)
    bonds = []

    for i in range(bond_count):
        st.subheader(f"Bond {i + 1}")
        bond_name = st.text_input(f"Name for Bond {i + 1}", value=f"Bond {i + 1}", key=f"bond_name_{i}")
        face_value = st.number_input(f"Face Value for Bond {i + 1} (€)", value=100.0, key=f"face_value_{i}", step=0.01)
        price = st.number_input(f"Current Price for Bond {i + 1} (€)", value=100.0, key=f"price_{i}", format="%.2f", step=0.01)
        coupon_rate = st.number_input(f"Coupon Rate (%) for Bond {i + 1}", value=5.0, key=f"coupon_rate_{i}") / 100
        years_to_maturity = st.number_input(f"Years to Maturity for Bond {i + 1}", value=10.0, key=f"years_to_maturity_{i}", step=0.01)

        bonds.append({
            "name": bond_name,
            "face_value": face_value,
            "price": price,
            "coupon_rate": coupon_rate,
            "years_to_maturity": years_to_maturity
        })

    if st.button("Calculate Bond Comparison"):
        bond_results = []

        for bond in bonds:
            face_value = bond["face_value"]
            price = bond["price"]
            coupon_rate = bond["coupon_rate"]
            years_to_maturity = bond["years_to_maturity"]
            bond_name = bond["name"]

            ytm_after_tax = calculate_ytm(face_value, price, coupon_rate, years_to_maturity, tax_rate)
            duration = calculate_duration(face_value, coupon_rate, years_to_maturity, ytm_after_tax)
            ytm_duration_ratio = calc_ytm_duration_ratio(ytm_after_tax, duration)

            bond_results.append({
                "Bond Name": bond_name,
                "YTM after tax (%)": ytm_after_tax * 100,
                "Duration (years)": duration,
                "YTM/Duration Ratio": ytm_duration_ratio
            })

        # Sort the results by YTM/Duration Ratio in descending order
        sorted_bond_results = sorted(bond_results, key=lambda x: x["YTM/Duration Ratio"], reverse=True)

        # Create a pandas DataFrame
        df = pd.DataFrame(sorted_bond_results)

        # Add an index column starting from 1
        df.insert(0, 'Bond #', range(1, len(df) + 1))

        # Highlight the best and worst bonds
        def highlight_best_worst(row):
            if row.name == 0:
                return ['background-color: green'] * len(row)
            elif row.name == len(df) - 1:
                return ['background-color: red'] * len(row)
            else:
                return [''] * len(row)

        st.write(df.style.apply(highlight_best_worst, axis=1))

        st.markdown("""
        ### Why the YTM/Duration Ratio is important:
        
        The **YTM/Duration Ratio** is used to measure the return relative to the interest rate risk (duration). A higher ratio indicates that the bond provides a better return for each unit of interest rate risk, making it more attractive compared to other bonds with lower ratios. Investors typically seek to maximize this ratio to achieve higher returns with less exposure to interest rate fluctuations.
        """)

if __name__ == "__main__":
    main()
