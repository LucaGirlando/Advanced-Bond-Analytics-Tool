import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import norm
from datetime import datetime, timedelta

# =============================================
# SETUP PAGE CONFIGURATION (PROFESSIONAL LOOK)
# =============================================
st.set_page_config(
    page_title="Advanced Bond Analytics Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .sidebar .sidebar-content {
            background-color: #343a40;
            color: white;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 24px;
        }
        .stSelectbox, .stNumberInput, .stDateInput, .stTextInput {
            margin-bottom: 15px;
        }
        .info-text {
            font-size: 14px;
            color: #6c757d;
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# =============================================
# SIDEBAR - MAIN NAVIGATION
# =============================================
with st.sidebar:
    st.title("Navigation Menu")
    analysis_type = st.radio(
        "Select Analysis Type:",
        ["Bond Pricing & Analytics", "Portfolio Analysis", "Yield Curve Analysis", "Risk Metrics", "Credit Risk Analysis", "Bond Comparison Tool"],
        index=0
    )

    # SPACE FOR FUTURE FUNCTION 1
    # SPACE FOR FUTURE DROPDOWN MENU
    
    st.markdown("---")
    st.markdown("""
    <p class='info-text'>
        The <strong>Advanced Bond Analytics Platform</strong> offers an integrated suite of tools for fixed income professionals — 
        including <em>bond pricing</em>, <em>portfolio analysis</em>, <em>yield curve modeling</em>, <em>risk metrics</em>, and <em>credit risk evaluation</em>.
        Effortlessly compare multiple bonds and analyze scenarios across various interest rate environments.
    </p>
    <p style="font-size: 12px; text-align: center; margin-top: 20px;">
        Created by: <a href="https://www.linkedin.com/in/luca-girlando-775463302/" target="_blank">Luca Girlando</a>
    </p>
""", unsafe_allow_html=True)

    # =============================================
    # BOND CALCULATION FUNCTIONS
    # =============================================
    def calculate_bond_metrics(face_value, coupon_rate, ytm, years_to_maturity, 
                             coupon_freq, bond_type, **kwargs):
        """
        Comprehensive bond valuation function that handles various bond types.
        
        Parameters:
        - face_value: Nominal value of the bond
        - coupon_rate: Annual coupon rate (%)
        - ytm: Yield to maturity (%)
        - years_to_maturity: Time to maturity in years
        - coupon_freq: Coupon payment frequency
        - bond_type: Type of bond structure
        
        Returns dictionary with all calculated metrics
        """
        # Convert annual rates to decimal
        coupon_rate = coupon_rate / 100
        ytm = ytm / 100
        
        # Determine payment frequency
        freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4, "Monthly": 12}
        n = freq_map[coupon_freq]
        periods = int(years_to_maturity * n)
        
        # Calculate periodic rates
        periodic_coupon = coupon_rate / n
        periodic_ytm = ytm / n
        
        # Initialize cash flows array
        cash_flows = np.zeros(periods)
        
        # Handle different bond types
        if bond_type == "Vanilla Fixed Rate":
            # Regular coupon payments
            cash_flows[:-1] = face_value * periodic_coupon
            # Final payment includes principal
            cash_flows[-1] = face_value * (1 + periodic_coupon)
            
        elif bond_type == "Zero Coupon":
            # Only final payment
            cash_flows[-1] = face_value
            
        elif bond_type == "Callable Bond":
            call_period = int((kwargs['call_date'].year - datetime.today().year) * n)
            if call_period < periods:
                # Coupons until call date
                cash_flows[:call_period] = face_value * periodic_coupon
                # Call price at call date
                cash_flows[call_period] = kwargs['call_price'] / 100 * face_value
                # Zero after call date
                cash_flows[call_period+1:] = 0
            else:
                # Not called - treat as vanilla
                cash_flows[:-1] = face_value * periodic_coupon
                cash_flows[-1] = face_value * (1 + periodic_coupon)
                
        # Similar logic for other bond types would go here...
        # (Putable, Step-Up, Step-Down, Fixed-to-Floating, etc.)
        
        # Calculate bond price as present value of cash flows
        discount_factors = 1 / (1 + periodic_ytm) ** np.arange(1, periods+1)
        price = np.sum(cash_flows * discount_factors)
        
        # Calculate Macaulay Duration
        times = np.arange(1, periods+1) / n
        pv_cash_flows = cash_flows * discount_factors
        mac_duration = np.sum(times * pv_cash_flows) / price
        
        # Calculate Modified Duration
        mod_duration = mac_duration / (1 + periodic_ytm)
        
        # Calculate Convexity
        convexity = np.sum(times * (times + 1/n) * pv_cash_flows / ((1 + periodic_ytm)**2)) / price
        
        return {
            "Price": price,
            "Macaulay Duration": mac_duration,
            "Modified Duration": mod_duration,
            "Convexity": convexity,
            "Yield to Maturity": ytm,
            "Cash Flows": cash_flows,
            "Discount Factors": discount_factors
        }

# =============================================
# MAIN PAGE CONTENT
# =============================================
st.title("📊 Advanced Bond Analytics Platform")
st.markdown("""
    <p class='info-text'>
        Perform detailed bond valuation and risk analysis for complex instruments including <em>callable</em>, <em>puttable</em>, 
        <em>step-up</em>, <em>step-down</em>, and <em>floating rate bonds</em>. 
        Gain insights into portfolio sensitivity, duration, convexity, and credit exposure with precision tools tailored for institutional-grade analytics.
    </p>
    <p style="font-size: 12px; text-align: center; margin-top: 20px;">
        Created by: <a href="https://www.linkedin.com/in/luca-girlando-775463302/" target="_blank">Luca Girlando</a>
    </p>
""", unsafe_allow_html=True)

# =============================================
# BOND PRICING & ANALYTICS FUNCTION
# =============================================
if analysis_type == "Bond Pricing & Analytics":
    st.header("Bond Pricing & Risk Analytics")
    
    with st.expander("⚙️ Bond Specifications", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Bond type selection
            bond_type = st.selectbox(
                "Bond Type:",
                ["Vanilla Fixed Rate", 
                 "Callable Bond", 
                 "Putable Bond",
                 "Step-Up Coupon",
                 "Step-Down Coupon",
                 "Fixed-to-Floating",
                 "Zero Coupon",
                 "Inflation-Linked"],
                index=0,
                help="Select the type of bond structure. This affects how cash flows are calculated."
            )
            
            # Face value input
            face_value = st.number_input(
                "Face Value (Principal):",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                help="The nominal value of the bond that will be repaid at maturity."
            )
            
            # Coupon rate input
            coupon_rate = st.number_input(
                "Coupon Rate (% p.a.):",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.25,
                help="Annual coupon rate as a percentage of face value."
            )
            
            # Coupon frequency
            coupon_freq = st.selectbox(
                "Coupon Frequency:",
                ["Annual", "Semi-Annual", "Quarterly", "Monthly"],
                index=1,
                help="How often coupon payments are made per year."
            )
            
        with col2:
            # Maturity selection method
            maturity_method = st.radio(
                "Maturity Specification:",
                ["Select Years to Maturity", "Input Exact Dates"],
                index=0,
                help="Choose whether to specify maturity in years or with exact dates."
            )
            
            if maturity_method == "Select Years to Maturity":
                years_to_maturity = st.slider(
                    "Years to Maturity:",
                    min_value=1,
                    max_value=50,
                    value=10,
                    step=1,
                    help="The remaining life of the bond in years."
                )
                settlement_date = datetime.today()
                maturity_date = settlement_date + relativedelta(years=years_to_maturity)
            else:
                settlement_date = st.date_input(
                    "Settlement Date:",
                    value=datetime.today(),
                    help="The date when the bond is purchased and the transaction settles."
                )
                maturity_date = st.date_input(
                    "Maturity Date:",
                    value=datetime.today() + relativedelta(years=10),
                    help="The date when the bond matures and principal is repaid."
                )
                # Calculate years to maturity
                delta = maturity_date - settlement_date
                years_to_maturity = delta.days / 365.25
            
            # Yield to Maturity input
            ytm = st.number_input(
                "Yield to Maturity (% p.a.):",
                min_value=0.0,
                max_value=100.0,
                value=6.0,
                step=0.25,
                help="The annualized discount rate used to price the bond."
            )
            
            # Day count convention
            day_count = st.selectbox(
                "Day Count Convention:",
                ["30/360", "Actual/360", "Actual/365", "Actual/Actual"],
                index=0,
                help="Method for calculating accrued interest between coupon dates."
            )
    
    # Additional features for complex bonds
    if bond_type in ["Callable Bond", "Putable Bond", "Step-Up Coupon", "Step-Down Coupon", "Fixed-to-Floating"]:
        with st.expander("🔧 Special Features", expanded=False):
            if bond_type == "Callable Bond":
                call_date = st.date_input(
                    "First Call Date:",
                    value=datetime.today() + relativedelta(years=5),
                    help="Earliest date the issuer can call (redeem) the bond."
                )
                call_price = st.number_input(
                    "Call Price (% of Face Value):",
                    min_value=0.0,
                    max_value=200.0,
                    value=102.0,
                    step=0.5,
                    help="Price at which the issuer can call the bond."
                )
                
            elif bond_type == "Putable Bond":
                put_date = st.date_input(
                    "First Put Date:",
                    value=datetime.today() + relativedelta(years=5),
                    help="Earliest date the investor can put (sell back) the bond."
                )
                put_price = st.number_input(
                    "Put Price (% of Face Value):",
                    min_value=0.0,
                    max_value=200.0,
                    value=98.0,
                    step=0.5,
                    help="Price at which the investor can put the bond."
                )
                
            elif bond_type in ["Step-Up Coupon", "Step-Down Coupon"]:
                st.markdown("**Coupon Schedule**")
                step_years = st.number_input(
                    "Years Between Steps:",
                    min_value=1,
                    max_value=10,
                    value=2,
                    step=1
                )
                step_amount = st.number_input(
                    "Coupon Change per Step (% points):",
                    value=0.5,
                    step=0.25,
                    help="Amount coupon increases (step-up) or decreases (step-down) each period."
                )
                
            elif bond_type == "Fixed-to-Floating":
                float_start = st.date_input(
                    "Floating Rate Start Date:",
                    value=datetime.today() + relativedelta(years=5))
                float_spread = st.number_input(
                    "Floating Spread (% over benchmark):",
                    value=2.0,
                    step=0.25
                )
                float_benchmark = st.selectbox(
                    "Benchmark Rate:",
                    ["LIBOR", "SOFR", "EURIBOR", "T-Bill Rate"],
                    index=0
                )
    
    # =============================================
    # DISPLAY RESULTS
    # =============================================
    if st.button("Calculate Bond Metrics", key="calculate_button"):
        # Prepare arguments based on bond type
        kwargs = {}
        if bond_type == "Callable Bond":
            kwargs = {'call_date': call_date, 'call_price': call_price}
        elif bond_type == "Putable Bond":
            kwargs = {'put_date': put_date, 'put_price': put_price}
        # Add other bond type parameters as needed...
        
        # Calculate metrics
        results = calculate_bond_metrics(
            face_value=face_value,
            coupon_rate=coupon_rate,
            ytm=ytm,
            years_to_maturity=years_to_maturity,
            coupon_freq=coupon_freq,
            bond_type=bond_type,
            **kwargs
        )
        
        # Display results in a professional layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Bond Price", f"${results['Price']:,.2f}")
            st.metric("Yield to Maturity", f"{results['Yield to Maturity']*100:.2f}%")
            
        with col2:
            st.metric("Macaulay Duration", f"{results['Macaulay Duration']:.2f} years")
            st.metric("Modified Duration", f"{results['Modified Duration']:.2f} years")
            
        with col3:
            st.metric("Convexity", f"{results['Convexity']:,.2f}")
            st.metric("Yield Value of 1bp (YV01)", 
                     f"${results['Price'] * results['Modified Duration'] * 0.0001:,.2f}")
        
        # Cash flow visualization
        st.subheader("Cash Flow Analysis")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=np.arange(1, len(results['Cash Flows'])+1),
            y=results['Cash Flows'],
            name='Cash Flows',
            marker_color='rgb(55, 83, 109)'
        ))
        fig.update_layout(
            title='Bond Cash Flow Schedule',
            xaxis_title='Period',
            yaxis_title='Amount ($)',
            showlegend=True,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed calculations expander
        with st.expander("📊 Detailed Calculations"):
            st.write("### Discounted Cash Flows")
            df = pd.DataFrame({
                "Period": np.arange(1, len(results['Cash Flows'])+1),
                "Cash Flow": results['Cash Flows'],
                "Discount Factor": results['Discount Factors'],
                "Present Value": results['Cash Flows'] * results['Discount Factors']
            })
            st.dataframe(df.style.format({
                "Cash Flow": "${:,.2f}",
                "Discount Factor": "{:.6f}",
                "Present Value": "${:,.2f}"
            }))
            
            st.write("### Duration Breakdown")
            st.markdown(f"""
                - **Macaulay Duration**: {results['Macaulay Duration']:.2f} years  
                  *The weighted average time to receive cash flows, measured in years*
                
                - **Modified Duration**: {results['Modified Duration']:.2f} years  
                  *Price sensitivity to yield changes (% price change per 1% yield change)*
                
                - **Dollar Duration**: ${results['Price'] * results['Modified Duration']:,.2f}  
                  *Price sensitivity in dollar terms per 1% yield change*
            """)
            
            st.write("### Convexity Analysis")
            st.markdown(f"""
                Convexity of {results['Convexity']:,.2f} indicates how the duration changes with yield.  
                Higher convexity is generally desirable as it means:  
                - Prices rise more when yields fall  
                - Prices fall less when yields rise  
                
                **Convexity Adjustment**:  
                For a 1% yield change, the price change considering convexity is approximately:  
                -Duration × Δy + 0.5 × Convexity × (Δy)²
            """)

# =============================================
# PORTFOLIO ANALYSIS FUNCTION
# =============================================
elif analysis_type == "Portfolio Analysis":
    st.header("Fixed Income Portfolio Analytics")
    
    with st.expander("📊 Portfolio Composition Setup", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Portfolio input method selection
            input_method = st.radio(
                "Portfolio Input Method:",
                ["Manual Entry", "CSV Upload"],
                index=0,
                help="Choose how to input portfolio holdings"
            )
            
            if input_method == "Manual Entry":
                num_bonds = st.number_input(
                    "Number of Bonds in Portfolio:",
                    min_value=1,
                    max_value=50,
                    value=3,
                    step=1
                )
            else:
                uploaded_file = st.file_uploader(
                    "Upload Portfolio CSV:",
                    type=["csv"],
                    help="Upload a CSV file with columns: BondID, FaceValue, CouponRate, YTM, YearsToMaturity, Weight"
                )
        
        with col2:
            st.markdown("**Portfolio Benchmark**")
            benchmark = st.selectbox(
                "Select Benchmark Index:",
                ["Bloomberg Barclays US Agg", "ICE BofA ML Treasury", 
                 "S&P U.S. IG Corp", "Custom Benchmark"],
                index=0
            )
            
            if benchmark == "Custom Benchmark":
                custom_bench_yield = st.number_input(
                    "Custom Benchmark Yield (%):",
                    min_value=0.0,
                    max_value=20.0,
                    value=4.5,
                    step=0.1
                )
    
    # Dynamic bond input form for manual entry
    if input_method == "Manual Entry":
        st.subheader("Bond Holdings Details")
        portfolio_bonds = []
        
        for i in range(num_bonds):
            with st.expander(f"Bond {i+1} Details", expanded=False):
                cols = st.columns(3)
                
                with cols[0]:
                    bond_id = st.text_input(f"ID/Bond Name {i+1}", value=f"Bond_{i+1}")
                    face_value = st.number_input(
                        f"Face Value {i+1}",
                        min_value=0.0,
                        value=1000.0,
                        step=100.0
                    )
                
                with cols[1]:
                    coupon_rate = st.number_input(
                        f"Coupon Rate % {i+1}",
                        min_value=0.0,
                        max_value=100.0,
                        value=5.0,
                        step=0.25
                    )
                    ytm = st.number_input(
                        f"YTM % {i+1}",
                        min_value=0.0,
                        max_value=100.0,
                        value=6.0,
                        step=0.25
                    )
                
                with cols[2]:
                    maturity = st.number_input(
                        f"Years to Maturity {i+1}",
                        min_value=0.0,
                        max_value=100.0,
                        value=10.0,
                        step=0.5
                    )
                    weight = st.number_input(
                        f"Portfolio Weight % {i+1}",
                        min_value=0.0,
                        max_value=100.0,
                        value=round(100/num_bonds, 2),
                        step=1.0
                    )
                
                portfolio_bonds.append({
                    'id': bond_id,
                    'face_value': face_value,
                    'coupon_rate': coupon_rate,
                    'ytm': ytm,
                    'maturity': maturity,
                    'weight': weight/100
                })
    else:
        # Process uploaded CSV
        if uploaded_file is not None:
            try:
                portfolio_bonds = pd.read_csv(uploaded_file).to_dict('records')
                st.success("CSV successfully loaded!")
                st.dataframe(pd.DataFrame(portfolio_bonds))
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                portfolio_bonds = []
        else:
            portfolio_bonds = []
            st.warning("Please upload a CSV file to continue")
    
    # Portfolio calculations
    if st.button("Analyze Portfolio", key="portfolio_button") and portfolio_bonds:
        # Calculate individual bond metrics
        for bond in portfolio_bonds:
            metrics = calculate_bond_metrics(
                face_value=bond['face_value'],
                coupon_rate=bond['coupon_rate'],
                ytm=bond['ytm'],
                years_to_maturity=bond['maturity'],
                coupon_freq="Semi-Annual",  # Default for portfolio analysis
                bond_type="Vanilla Fixed Rate"  # Default for portfolio analysis
            )
            bond.update(metrics)
        
        # Create portfolio DataFrame
        portfolio_df = pd.DataFrame(portfolio_bonds)
        
        # Calculate weighted portfolio metrics
        portfolio_metrics = {
            'Total Value': (portfolio_df['weight'] * portfolio_df['Price']).sum(),
            'Weighted YTM': (portfolio_df['weight'] * portfolio_df['Yield to Maturity']).sum(),
            'Weighted Duration': (portfolio_df['weight'] * portfolio_df['Modified Duration']).sum(),
            'Weighted Convexity': (portfolio_df['weight'] * portfolio_df['Convexity']).sum()
        }
        
        # Display portfolio summary
        st.subheader("Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Portfolio Value", f"${portfolio_metrics['Total Value']:,.2f}")
            st.metric("Number of Holdings", len(portfolio_df))
            
        with col2:
            st.metric("Weighted YTM", f"{portfolio_metrics['Weighted YTM']*100:.2f}%")
            st.metric("Yield Spread to Benchmark", 
                     f"{(portfolio_metrics['Weighted YTM'] - (custom_bench_yield/100 if benchmark == 'Custom Benchmark' else 0.045))*100:.2f}bps")
            
        with col3:
            st.metric("Weighted Duration", f"{portfolio_metrics['Weighted Duration']:.2f} years")
            st.metric("Weighted Convexity", f"{portfolio_metrics['Weighted Convexity']:,.2f}")
        
        # Risk analysis
        st.subheader("Portfolio Risk Analysis")
        
        # Initialize session state for portfolio metrics if not exists
        if 'portfolio_metrics' not in st.session_state:
            st.session_state.portfolio_metrics = portfolio_metrics
            st.session_state.portfolio_df = portfolio_df
        
        # Store calculated values in session state
        st.session_state.portfolio_metrics = portfolio_metrics
        st.session_state.portfolio_df = portfolio_df
        
        # Yield curve shift analysis with session state
        if 'shift_size' not in st.session_state:
            st.session_state.shift_size = 100
        
        def update_shift():
            st.session_state.shift_size = st.session_state.yield_shift_slider
        
        shift_size = st.slider(
            "Parallel Yield Curve Shift (bps):",
            min_value=-500,
            max_value=500,
            value=st.session_state.shift_size,
            step=25,
            key="yield_shift_slider",
            on_change=update_shift
        )
        
        # Calculate price impact using session state values
        portfolio_df = st.session_state.portfolio_df.copy()
        portfolio_metrics = st.session_state.portfolio_metrics
        
        portfolio_df['price_change'] = (
            -portfolio_df['Modified Duration'] * (shift_size/10000) * portfolio_df['Price'] +
            0.5 * portfolio_df['Convexity'] * (shift_size/10000)**2 * portfolio_df['Price']
        )
        
        total_change = (portfolio_df['weight'] * portfolio_df['price_change']).sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                f"Portfolio Value Change ({shift_size}bps shift)",
                f"${total_change:,.2f}",
                delta_color="inverse"
            )
            
        with col2:
            st.metric(
                "Estimated New Portfolio Value",
                f"${portfolio_metrics['Total Value'] + total_change:,.2f}"
            )
        
        # Display bond-by-bond impact
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=portfolio_df['id'],
            y=portfolio_df['price_change'],
            name='Price Impact',
            marker_color=np.where(portfolio_df['price_change'] < 0, 'red', 'green')
        ))
        fig3.update_layout(
            title=f'Price Impact per Holding ({shift_size}bps Yield Change)',
            yaxis_title='Price Change ($)'
        )
        st.plotly_chart(fig3, use_container_width=True)

# =============================================
# YIELD CURVE ANALYSIS FUNCTION 
# =============================================
elif analysis_type == "Yield Curve Analysis":
    st.header("Yield Curve Analytics")
    
    with st.expander("🌐 Yield Curve Configuration", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            curve_source = st.radio(
                "Yield Curve Source:",
                ["Market Data (API)", "Manual Input", "Historical Dataset"],
                index=1
            )
            
            curve_type = st.selectbox(
                "Yield Curve Type:",
                ["Government Bonds", "Swap Rates", "Corporate AA", "Corporate BBB", "Municipal"],
                index=0
            )
            
            if curve_source == "Historical Dataset":
                curve_date = st.date_input(
                    "As of Date:",
                    value=datetime.today(),
                    max_value=datetime.today()
                )
        
        with col2:
            if curve_source == "Manual Input":
                st.markdown("**Manual Yield Input**")
                manual_maturities = st.text_input(
                    "Maturities (years, comma separated):",
                    value="0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30"
                )
                manual_yields = st.text_input(
                    "Yields (% p.a., comma separated):",
                    value="0.5, 0.7, 1.0, 1.5, 1.8, 2.2, 2.5, 2.8, 3.2, 3.5"
                )
                
                try:
                    maturities = [float(x.strip()) for x in manual_maturities.split(",")]
                    yields = [float(x.strip())/100 for x in manual_yields.split(",")]
                except:
                    st.warning("Please enter valid comma-separated numbers")
                    maturities = []
                    yields = []
            else:
                maturities = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
                yields = [0.005, 0.007, 0.01, 0.015, 0.018, 0.022, 0.025, 0.028, 0.032, 0.035]
                st.info(f"Using sample {curve_type} yield curve data")
    
    # INTERPOLATION SECTION
    with st.expander("📈 Curve Modeling", expanded=False):
        model_type = st.selectbox(
            "Interpolation Model:",
            ["Linear", "Polynomial", "Nelson-Siegel"],
            index=0
        )
        
        if model_type == "Polynomial":
            degree = st.slider("Polynomial Degree", 2, 5, 3)
        
        if model_type in ["Nelson-Siegel"]:
            st.markdown("**Model Parameters**")
            cols = st.columns(3)
            with cols[0]:
                beta0 = st.number_input("β₀ (Level)", value=0.03, step=0.01)
            with cols[1]:
                beta1 = st.number_input("β₁ (Slope)", value=-0.02, step=0.01)
            with cols[2]:
                beta2 = st.number_input("β₂ (Curvature)", value=0.01, step=0.01)
                tau = st.number_input("τ (Decay rate)", value=1.0, step=0.1)
    
    if maturities and yields:
        st.subheader("Yield Curve Visualization")
        plot_maturities = np.linspace(min(maturities), max(maturities), 100)
        
        if model_type == "Linear":
            plot_yields = np.interp(plot_maturities, maturities, yields)
        elif model_type == "Polynomial":
            coeffs = np.polyfit(maturities, yields, degree)
            poly = np.poly1d(coeffs)
            plot_yields = poly(plot_maturities)
        else:  # Nelson-Siegel
            def nelson_siegel(t, b0, b1, b2, tau):
                return b0 + b1*(1-np.exp(-t/tau))/(t/tau) + b2*((1-np.exp(-t/tau))/(t/tau)-np.exp(-t/tau))
            plot_yields = nelson_siegel(plot_maturities, beta0, beta1, beta2, tau)
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Raw data points
        fig.add_trace(go.Scatter(
            x=maturities,
            y=[y*100 for y in yields],
            mode='markers',
            name='Market Data',
            marker=dict(size=10, color='red')
        ))
        
        # Fitted curve
        fig.add_trace(go.Scatter(
            x=plot_maturities,
            y=[y*100 for y in plot_yields],
            mode='lines',
            name=f'{model_type} Fit',
            line=dict(width=3, color='blue')
        ))
        
        fig.update_layout(
            title=f'{curve_type} Yield Curve',
            xaxis_title='Time to Maturity (years)',
            yaxis_title='Yield (%)',
            hovermode='x unified',
            template='plotly_white',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Curve analytics
        st.subheader("Curve Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Calculate slope (10Y-2Y)
            if max(maturities) >= 10 and min(maturities) <= 2:
                y10 = np.interp(10, maturities, yields)
                y2 = np.interp(2, maturities, yields)
                slope = (y10 - y2)*100
                st.metric("10Y-2Y Slope", f"{slope:.2f} bps")
            else:
                st.warning("Need 2Y and 10Y points for slope")
            
        with col2:
            # Calculate curvature (2*5Y - 2Y - 10Y)
            if max(maturities) >= 10 and min(maturities) <= 2 and 5 in maturities:
                y5 = np.interp(5, maturities, yields)
                curvature = (2*y5 - y2 - y10)*10000
                st.metric("Curvature (Butterfly)", f"{curvature:.2f} bps")
        
        with col3:
            # Identify if inverted
            if slope < 0:
                st.metric("Curve Shape", "INVERTED", delta="Bearish Signal", delta_color="inverse")
            elif slope < 50:
                st.metric("Curve Shape", "FLAT", delta="Caution")
            else:
                st.metric("Curve Shape", "NORMAL", delta="Bullish Signal")
        
        # Forward rate calculations
        with st.expander("🔮 Forward Rate Projections", expanded=False):
            st.markdown("""
                **Implied Forward Rates**  
                The forward rate between time t₁ and t₂ is calculated as:
            """)
            st.latex(r"""
            f(t_1,t_2) = \left( \frac{(1+y(t_2))^{t_2}}{(1+y(t_1))^{t_1}} \right)^{\frac{1}{t_2-t_1}} - 1
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                start_year = st.number_input("Start Year", min_value=0.0, value=1.0, step=0.5)
            with col2:
                end_year = st.number_input("End Year", min_value=0.0, value=2.0, step=0.5)
            
            if end_year > start_year:
                y_start = np.interp(start_year, maturities, yields)
                y_end = np.interp(end_year, maturities, yields)
                forward_rate = (((1+y_end)**end_year)/((1+y_start)**start_year))**(1/(end_year-start_year)) - 1
                
                st.metric(
                    f"Implied Forward Rate {start_year}-{end_year}Y",
                    f"{forward_rate*100:.2f}%",
                    help="The expected future interest rate between these dates implied by the current yield curve"
                )
        
        # Stress testing
        with st.expander("🧪 Curve Stress Testing", expanded=False):
            st.markdown("**Parallel and Non-Parallel Shifts**")
            
            shift_type = st.radio(
                "Shift Type:",
                ["Parallel", "Steepening", "Flattening", "Hump"],
                index=0
            )
            
            shift_size = st.slider(
                "Shift Magnitude (bps):",
                min_value=-300,
                max_value=300,
                value=100,
                step=25
            )
            
            # Apply shifts
            if shift_type == "Parallel":
                new_yields = [y + shift_size/10000 for y in yields]
            elif shift_type == "Steepening":
                new_yields = [y + (shift_size/10000)*(t/max(maturities)) for t,y in zip(maturities,yields)]
            elif shift_type == "Flattening":
                new_yields = [y + (shift_size/10000)*(1-t/max(maturities)) for t,y in zip(maturities,yields)]
            else:  # Hump
                new_yields = [y + (shift_size/10000)*np.exp(-((t-5)**2)/10) for t,y in zip(maturities,yields)]
            
            # Plot comparison
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=maturities,
                y=[y*100 for y in yields],
                mode='lines+markers',
                name='Current Curve',
                line=dict(width=2, color='blue')
            ))
            fig2.add_trace(go.Scatter(
                x=maturities,
                y=[y*100 for y in new_yields],
                mode='lines+markers',
                name=f'Shifted Curve ({shift_type})',
                line=dict(width=2, color='red', dash='dash')
            ))
            fig2.update_layout(
                title='Yield Curve Stress Test',
                xaxis_title='Maturity',
                yaxis_title='Yield (%)',
                template='plotly_white'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Calculate bond price impact example
            st.markdown("**Price Impact Example**")
            col1, col2 = st.columns(2)
            with col1:
                example_maturity = st.number_input("Example Bond Maturity", min_value=0.5, value=5.0, step=0.5)
            with col2:
                example_coupon = st.number_input("Example Coupon Rate (%)", min_value=0.0, value=5.0, step=0.1)
            
            if example_maturity:
                original_yield = np.interp(example_maturity, maturities, yields)
                new_yield = np.interp(example_maturity, maturities, new_yields)
                
                # Simplified price calculation
                original_price = sum([example_coupon/100/(1+original_yield)**t for t in np.arange(1, example_maturity+1)]) + 1/(1+original_yield)**example_maturity
                new_price = sum([example_coupon/100/(1+new_yield)**t for t in np.arange(1, example_maturity+1)]) + 1/(1+new_yield)**example_maturity
                
                st.metric(
                    f"Price Change for {example_maturity}Y {example_coupon}% Bond",
                    f"{(new_price - original_price)*100:.2f}%",
                    delta_color="inverse"
                )

# =============================================
# RISK METRICS FUNCTION
# =============================================
elif analysis_type == "Risk Metrics":
    st.header("Fixed Income Risk Analytics")
    
    # Initialize variables needed for stress testing
    if 'dollar_duration' not in st.session_state:
        st.session_state.dollar_duration = 0
        st.session_state.dollar_convexity = 0
        st.session_state.price = 0
    
    with st.expander("⚙️ Risk Parameters Setup", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            risk_bond_type = st.selectbox(
                "Bond Type:",
                ["Vanilla Fixed Rate"],
                index=0,
                key="risk_bond_type"
            )
            
            risk_face_value = st.number_input(
                "Face Value:",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key="risk_face_value"
            )
            
            risk_coupon_rate = st.number_input(
                "Coupon Rate (% p.a.):",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.25,
                key="risk_coupon_rate"
            )
            
        with col2:
            risk_maturity = st.number_input(
                "Years to Maturity:",
                min_value=0.1,
                max_value=50.0,
                value=10.0,
                step=0.5,
                key="risk_maturity"
            )
            
            risk_ytm = st.number_input(
                "Current Yield to Maturity (%):",
                min_value=0.0,
                max_value=100.0,
                value=6.0,
                step=0.25,
                key="risk_ytm"
            )
            
            risk_coupon_freq = st.selectbox(
                "Coupon Frequency:",
                ["Annual", "Semi-Annual", "Quarterly"],
                index=1,
                key="risk_coupon_freq"
            )
    
    with st.expander("📉 Market Risk Factors", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            yield_vol = st.number_input(
                "Yield Volatility (bps/day):",
                min_value=0.1,
                max_value=100.0,
                value=5.0,
                step=0.5,
                help="Historical daily volatility of yields"
            )
            
        with col2:
            credit_spread = st.number_input(
                "Credit Spread (bps):",
                min_value=0.0,
                max_value=1000.0,
                value=150.0,
                step=5.0
            )
            
        with col3:
            liquidity_factor = st.number_input(
                "Liquidity Factor:",
                min_value=0.1,
                max_value=10.0,
                value=1.5,
                step=0.1,
                help="Multiplier for bid-ask spreads (higher = less liquid)"
            )
    
    with st.expander("🧮 Advanced Risk Calculations", expanded=False):
        st.markdown("**Value-at-Risk (VaR) Parameters**")
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_level = st.selectbox(
                "Confidence Level:",
                [90, 95, 99, 99.5, 99.9],
                index=2,
                format_func=lambda x: f"{x}%"
            )
            
        with col2:
            horizon_days = st.number_input(
                "Horizon (days):",
                min_value=1,
                max_value=30,
                value=10,
                step=1
            )
    
    if st.button("Calculate Risk Metrics", key="risk_calc_button"):
        bond_metrics = calculate_bond_metrics(
            face_value=risk_face_value,
            coupon_rate=risk_coupon_rate,
            ytm=risk_ytm,
            years_to_maturity=risk_maturity,
            coupon_freq=risk_coupon_freq,
            bond_type=risk_bond_type
        )
        
        price = bond_metrics['Price']
        mod_duration = bond_metrics['Modified Duration']
        convexity = bond_metrics['Convexity']
        
        rate_shock = yield_vol * np.sqrt(horizon_days) / 10000
        st.session_state.dollar_duration = price * mod_duration
        st.session_state.dollar_convexity = price * convexity
        st.session_state.price = price
        
        delta_price_linear = -st.session_state.dollar_duration * rate_shock
        delta_price_convex = delta_price_linear + 0.5 * st.session_state.dollar_convexity * (rate_shock**2)
        
        z_score = {90: 1.282, 95: 1.645, 99: 2.326, 99.5: 2.576, 99.9: 3.090}[confidence_level]
        price_volatility = st.session_state.dollar_duration * yield_vol / 10000
        var = z_score * price_volatility * np.sqrt(horizon_days)
        
        liquidity_adj = 0.5 * price * liquidity_factor * 0.01
        
        st.subheader("Risk Metrics Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Price", f"${price:,.2f}")
            st.metric("DV01", f"${st.session_state.dollar_duration * 0.0001:,.2f}",
                     help="Price change per 1bp yield move")
            
        with col2:
            st.metric("Modified Duration", f"{mod_duration:.2f} years")
            st.metric("Convexity", f"{convexity:,.2f}")
            
        with col3:
            st.metric("Yield Volatility", f"{yield_vol:.1f} bps/day")
            st.metric("Credit Spread", f"{credit_spread:.1f} bps")
        
        st.subheader("Portfolio Risk Measures")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"{confidence_level}% {horizon_days}-day VaR",
                f"${var:,.2f}",
                delta=f"{-var/price*100:.2f}% of price",
                delta_color="inverse"
            )
            
        with col2:
            st.metric(
                "Expected Price Change",
                f"${delta_price_convex:,.2f}",
                help="Including convexity adjustment"
            )
            
        with col3:
            st.metric(
                "Liquidity Adjustment",
                f"${liquidity_adj:,.2f}",
                help="Estimated bid-ask spread impact"
            )
        
        st.subheader("Risk Decomposition")
        
        risk_factors = {
            'Interest Rate Risk': abs(delta_price_convex),
            'Credit Spread Risk': price * (credit_spread/10000) * mod_duration,
            'Liquidity Risk': liquidity_adj,
            'Convexity Effect': 0.5 * st.session_state.dollar_convexity * (rate_shock**2)
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(risk_factors.keys()),
            y=list(risk_factors.values()),
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        ))
        fig.update_layout(
            title="Risk Factor Contribution (USD)",
            yaxis_title="Risk Amount ($)",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🧪 Stress Testing Scenarios", expanded=False):
        st.markdown("**Historical & Hypothetical Scenarios**")
        
        if 'selected_scenario' not in st.session_state:
            st.session_state.selected_scenario = "2020 COVID Crisis"
        
        def update_scenario():
            st.session_state.selected_scenario = st.session_state.scenario_selectbox
        
        scenario = st.selectbox(
            "Select Scenario:",
            ["2020 COVID Crisis", "2008 Lehman Shock", "1994 Bond Massacre", "Custom Shock"],
            index=0,
            key="scenario_selectbox",
            on_change=update_scenario
        )
        
        current_scenario = st.session_state.selected_scenario
        
        if current_scenario == "Custom Shock":
            custom_shock = st.number_input(
                "Yield Shock (bps):",
                min_value=-500,
                max_value=500,
                value=100,
                step=25,
                key="custom_shock_input"
            )
        else:
            scenario_shocks = {
                "2020 COVID Crisis": 75,
                "2008 Lehman Shock": 125,
                "1994 Bond Massacre": 200
            }
            custom_shock = scenario_shocks[current_scenario]
        
        if st.session_state.dollar_duration == 0:
            st.warning("Please calculate risk metrics first")
        else:
            shock_size = custom_shock / 10000
            scenario_delta = (
                -st.session_state.dollar_duration * shock_size + 
                0.5 * st.session_state.dollar_convexity * (shock_size**2))
            
            st.metric(
                f"Scenario Impact ({current_scenario})",
                f"${scenario_delta:,.2f}",
                delta=f"{scenario_delta/st.session_state.price*100:.2f}%",
                delta_color="inverse"
            )
            
            if current_scenario != "Custom Shock":
                historical_recovery = {
                    "2020 COVID Crisis": "3 months",
                    "2008 Lehman Shock": "12 months",
                    "1994 Bond Massacre": "6 months"
                }
                st.markdown(f"**Historical Recovery Time:** {historical_recovery[current_scenario]}")

# =============================================
# CREDIT RISK ANALYSIS FUNCTION
# =============================================
elif analysis_type == "Credit Risk Analysis":
    st.header("📊 Advanced Credit Risk Analytics")
    
    with st.expander("🔍 Bond Credit Fundamentals", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            credit_rating = st.selectbox(
                "Credit Rating:",
                ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", 
                 "BBB+", "BBB", "BBB-", "BB+", "BB", "BB-", "B+", "B", "B-", 
                 "CCC+", "CCC", "CCC-", "CC", "C", "D"],
                index=7,
                help="Standard & Poor's rating scale"
            )
            
            cds_spread = st.number_input(
                "CDS Spread (bps):",
                min_value=0,
                max_value=5000,
                value=150,
                step=5,
                help="5-year Credit Default Swap spread in basis points"
            )
            
        with col2:
            probability_default = st.slider(
                "Annual PD (%):",
                min_value=0.0,
                max_value=50.0,
                value=2.5,
                step=0.1,
                help="Probability of Default"
            )
            
            recovery_rate = st.slider(
                "Recovery Rate (%):",
                min_value=0,
                max_value=100,
                value=40,
                step=5,
                help="Expected recovery in case of default"
            )
    
    # CreditMetrics Model Implementation
    with st.expander("📈 CreditMetrics Model (J.P. Morgan)", expanded=False):
        st.markdown("""
        **CreditMetrics Framework**:
        - Value-at-Risk approach for credit risk
        - Incorporates rating migrations
        - Accounts for correlation between obligors
        """)
        
        st.latex(r"""
        \text{Credit VaR} = \text{Portfolio Value} \times \text{Worst Case Loss} \times \sqrt{\text{Time Horizon}}
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            rating_matrix = pd.DataFrame({
                'Rating': ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'Default'],
                '1Y Transition (%)': [0.09, 2.27, 91.05, 5.52, 0.74, 0.26, 0.01, 0.06],
                '5Y Spread (bps)': [15, 30, 50, 120, 300, 550, 1000, 5000]
            })
            st.dataframe(rating_matrix.style.format({'1Y Transition (%)': '{:.2f}%'}))
        
        with col2:
            confidence_level = st.selectbox(
                "Confidence Level:",
                [90, 95, 99, 99.5, 99.9],
                index=2,
                key="credit_var_conf"
            )
            
            # Simplified Credit VaR without scipy.stats
            z_scores = {90: 1.282, 95: 1.645, 99: 2.326, 99.5: 2.576, 99.9: 3.090}
            risk_neutral_pd = (cds_spread/10000)/(1-recovery_rate/100)
            credit_var = risk_neutral_pd * z_scores[confidence_level] * 100
            st.metric("1Y Credit VaR", f"{credit_var:.2f}%", 
                     help=f"At {confidence_level}% confidence level")
    
    # CreditRisk+ Model Implementation
    with st.expander("📉 CreditRisk+ Model (CSFB)", expanded=False):
        st.markdown("""
        **CreditRisk+ Framework**:
        - Actuarial approach based on Poisson distribution
        - Models default events as random variables
        - Suitable for large portfolios
        """)
        
        st.latex(r"""
        P(n) = \frac{e^{-\lambda}\lambda^n}{n!}
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            exposure = st.number_input(
                "Exposure at Default ($):",
                min_value=0,
                max_value=1000000000,
                value=1000000,
                step=100000
            )
            
            default_volatility = st.slider(
                "Default Rate Volatility (%):",
                min_value=0.1,
                max_value=50.0,
                value=5.0,
                step=0.1
            )
        
        with col2:
            # CreditRisk+ calculations
            lambda_param = probability_default/100
            unexpected_loss = exposure * np.sqrt(
                (probability_default/100)*(1-probability_default/100)*(default_volatility/100)**2
            )
            
            st.metric("Expected Loss", f"${exposure * probability_default/100 * (1-recovery_rate/100):,.2f}")
            st.metric("Unexpected Loss", f"${unexpected_loss:,.2f}")
    
    # Advanced Credit Analytics
    with st.expander("🧠 Deep Credit Analysis", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Structural Models", "Reduced-Form Models", "Credit Derivatives"])
        
        with tab1:
            st.markdown("""
            **Merton Model (Structural Approach)**:
            - Models default as option exercise
            - Firm value follows geometric Brownian motion
            - Default when assets < liabilities
            """)
            st.latex(r"""
            PD = N\left(-\frac{\ln(V_0/D) + (\mu - \sigma^2/2)T}{\sigma\sqrt{T}}\right)
            """)
        
        with tab2:
            st.markdown("""
            **Intensity Models (Reduced-Form)**:
            - Default as exogenous Poisson process
            - Hazard rate λ(t) drives default probability
            - Popular for credit derivatives pricing
            """)
            st.latex(r"""
            PD(t,T) = 1 - e^{-\int_t^T \lambda(s)ds}
            """)
        
        with tab3:
            st.markdown("""
            **Credit Derivatives Pricing**:
            - CDS spread = (1 - RR) × Hazard Rate
            - Collateralized Debt Obligations (CDOs)
            - Credit Valuation Adjustment (CVA)
            """)
            st.latex(r"""
            \text{CDS Spread} = (1-RR) \times \lambda \times 10000 \text{ bps}
            """)
    
    # Practical Applications
    with st.expander("💼 Practical Applications", expanded=False):
        st.markdown("""
        1. **Risk-Adjusted Pricing**:
           - Incorporate credit risk into bond pricing
           - Adjust yields for expected losses
        
        2. **Portfolio Optimization**:
           - Diversify across ratings/industries
           - Match duration while managing credit risk
        
        3. **Regulatory Capital**:
           - Basel III credit risk requirements
           - RWA calculations for bonds
        """)
        
        # Credit risk heatmap
        ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
        default_probs = [0.03, 0.06, 0.15, 0.30, 1.20, 5.00, 20.00]
        fig = px.bar(x=ratings, y=default_probs, 
                    labels={'x':'Credit Rating', 'y':'Historical PD (%)'},
                    title='Historical Default Probabilities by Rating')
        st.plotly_chart(fig, use_container_width=True)

# =============================================
# BOND COMPARISON TOOL (FIXED VERSION)
# =============================================
elif analysis_type == "Bond Comparison Tool":
    st.header("🔍 Bond Comparison Tool")
    
    # Initialize session state
    if 'bond_data' not in st.session_state:
        st.session_state.bond_data = []
        st.session_state.advanced_mode = False
    
    # Function to add new bond
    def add_bond(name, purchase_price, face_value, coupon_rate, coupon_freq, purchase_date, maturity_date):
        st.session_state.bond_data.append({
            'name': name,
            'purchase_price': purchase_price,
            'face_value': face_value,
            'coupon_rate': coupon_rate,
            'coupon_freq': coupon_freq,
            'purchase_date': purchase_date,
            'maturity_date': maturity_date,
            'current_date': datetime.now().date(),
            'ytm': None,
            'duration': None,
            'credit_spread': 100,  # Default values for advanced
            'rating': 'BBB',
            'sector': 'Corporate'
        })
    
    # Basic input form - CORRECTED FORM WITH SUBMIT BUTTON
    with st.expander("➕ Add New Bond (Basic)", expanded=True):
        form = st.form("bond_form")
        with form:
            col1, col2 = st.columns(2)
            
            with col1:
                name = form.text_input("Bond Name/ID:")
                purchase_price = form.number_input("Purchase Price:", min_value=0.0, value=100.0)
                face_value = form.number_input("Face Value at Maturity:", min_value=0.0, value=100.0)
            
            with col2:
                coupon_rate = form.number_input("Coupon Rate (% p.a.):", min_value=0.0, max_value=100.0, value=5.0)
                coupon_freq = form.selectbox("Coupon Frequency:", ["Annual", "Semi-Annual", "Quarterly"])
                purchase_date = form.date_input("Purchase Date:", value=datetime.now().date())
                maturity_date = form.date_input("Maturity Date:", 
                                             value=datetime.now().date() + timedelta(days=365*5))
            
            submitted = form.form_submit_button("Add Bond")
            if submitted and name:
                add_bond(name, purchase_price, face_value, coupon_rate, coupon_freq, purchase_date, maturity_date)
                st.success(f"Added {name} to comparison")
                st.rerun()
    
    # Calculate basic metrics for all bonds
    def calculate_basic_metrics():
        for bond in st.session_state.bond_data:
            try:
                # Calculate years to maturity from current date
                years_to_maturity = (bond['maturity_date'] - bond['current_date']).days / 365.25
                
                # Calculate periodic coupon payment
                freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4}
                periods_per_year = freq_map[bond['coupon_freq']]
                coupon_payment = bond['face_value'] * (bond['coupon_rate']/100) / periods_per_year
                
                # Simplified YTM calculation (approximation)
                total_coupons = coupon_payment * years_to_maturity * periods_per_year
                total_gain = bond['face_value'] - bond['purchase_price']
                bond['ytm'] = ((total_coupons + total_gain) / years_to_maturity) / bond['purchase_price']
                
                # Simplified duration calculation
                bond['duration'] = years_to_maturity / (1 + bond['ytm'])
            except:
                bond['ytm'] = 0
                bond['duration'] = 0
    
    # Toggle advanced mode
    if st.button("🛠️ Toggle Advanced Mode"):
        st.session_state.advanced_mode = not st.session_state.advanced_mode
        st.rerun()
    
    # Display bonds table
    if st.session_state.bond_data:
        calculate_basic_metrics()
        
        st.markdown("### Your Bond Portfolio")
        display_df = pd.DataFrame(st.session_state.bond_data)
        
        # Format columns for display
        display_cols = ['name', 'purchase_price', 'face_value', 'coupon_rate', 
                       'coupon_freq', 'ytm', 'duration']
        display_df = display_df[display_cols]
        display_df['ytm'] = display_df['ytm'].apply(lambda x: f"{x*100:.2f}%")
        display_df['duration'] = display_df['duration'].apply(lambda x: f"{x:.2f} years")
        
        st.dataframe(display_df)
        
        # Basic comparison charts
        st.markdown("### Basic Comparison")
        fig = px.bar(display_df, x='name', y='purchase_price', title="Purchase Price Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
        # Advanced analysis section
        if st.session_state.advanced_mode:
            st.markdown("---")
            st.subheader("Advanced Analysis")
            
            # Advanced parameters
            with st.expander("⚙️ Advanced Parameters", expanded=True):
                cols = st.columns(3)
                headers = ["Bond", "Credit Spread (bps)", "Rating", "Sector"]
                for i, h in enumerate(headers[:3]):
                    cols[i].write(f"**{h}**")
                
                for i, bond in enumerate(st.session_state.bond_data):
                    cols = st.columns(3)
                    cols[0].write(bond['name'])
                    
                    with cols[1]:
                        bond['credit_spread'] = st.number_input(
                            label="", 
                            min_value=0, 
                            max_value=1000, 
                            value=bond['credit_spread'], 
                            key=f"spread_{i}"
                        )
                    
                    with cols[2]:
                        bond['rating'] = st.selectbox(
                            label="", 
                            options=["AAA","AA","A","BBB","BB","B","CCC"], 
                            index=["AAA","AA","A","BBB","BB","B","CCC"].index(bond['rating']),
                            key=f"rating_{i}"
                        )
            
            # Advanced analysis tabs
            tab1, tab2 = st.tabs(["Risk-Return Profile", "Scenario Analysis"])
            
            with tab1:
                st.markdown("#### Risk-Return Profile")
                adv_df = pd.DataFrame(st.session_state.bond_data)
                adv_df['ytm_num'] = adv_df['ytm'].astype(float)
                fig = px.scatter(adv_df, x='duration', y='ytm_num', color='rating',
                                size='credit_spread', hover_name='name',
                                title="Risk-Return Profile",
                                labels={'duration': 'Duration (years)', 'ytm_num': 'Yield to Maturity'})
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown("#### Scenario Analysis")
                scenario = st.selectbox("Select Scenario:", 
                                      ["Rates +100bps", "Rates -50bps", "Credit Spread +50bps"])
                
                scenario_df = pd.DataFrame(st.session_state.bond_data)
                scenario_df['duration_num'] = scenario_df['duration'].astype(float)
                
                if scenario == "Rates +100bps":
                    scenario_df['price_change'] = -scenario_df['duration_num'] * 1.0
                elif scenario == "Rates -50bps":
                    scenario_df['price_change'] = -scenario_df['duration_num'] * -0.5
                else: # Credit Spread +50bps
                    scenario_df['price_change'] = -scenario_df['duration_num'] * 0.5
                
                fig = px.bar(scenario_df, x='name', y='price_change', color='rating',
                            title=f"Price Change in {scenario} Scenario (%)")
                st.plotly_chart(fig, use_container_width=True)
    
    # Clear all button
    if st.button("❌ Clear All Bonds"):
        st.session_state.bond_data = []
        st.session_state.advanced_mode = False
        st.rerun()

# =============================================
# FOOTER AND DISCLAIMER
# =============================================
st.markdown("---")
st.markdown("""
    <p class='info-text'>
        Disclaimer: This tool is for educational and professional use only. Bond valuations are sensitive to input parameters 
        and market conditions. Always verify calculations with independent sources before making investment decisions.
    </p>
""", unsafe_allow_html=True)
