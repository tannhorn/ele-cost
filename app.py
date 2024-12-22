"""Applet version of the LCOE estimator"""

import streamlit as st
import plotly.graph_objects as go

from lcoe import evaluate as evl

PRESENT_YEAR = 1
HOURS_IN_YEAR = 8760

# Dictionary of inputs
basic_inputs = [
    "discount_rate",
    "power",
    "overnight_cost",
    "o_and_m_cost",
    "fuel_cost",
    "capacity_factor",
]
extra_inputs = [
    "construction_duration",
    "operational_lifetime",
    "decommissioning_duration",
    "carbon_cost",
    "capital_cost_contingency",
    "decommissioning_cost_factor",
    "carbon_content",
]

# Define default values
default_values = {
    "discount_rate": 7.0,  # %
    "power": 1137,  # MWe
    "overnight_cost": 3370,  # $/kWe
    "capital_cost_contingency": 15,  # %
    "capacity_factor": 80,  # %
    "o_and_m_cost": 11.6,  # $/MWh
    "fuel_cost": 9.33,  # $/MWh
    "decommissioning_cost_factor": 15,  # %
    "construction_duration": 7,  # years
    "operational_lifetime": 60,  # years
    "decommissioning_duration": 10,  # years
    "carbon_cost": 30,  # $/t CO2
    "carbon_content": 0,  # t/MWh
}

# Define step values
step_values = {
    "discount_rate": 0.5,
    "power": 100,
    "overnight_cost": 100,
    "capital_cost_contingency": 1,
    "capacity_factor": 1,
    "o_and_m_cost": 0.5,
    "fuel_cost": 0.5,
    "decommissioning_cost_factor": 1,
    "construction_duration": 1,
    "operational_lifetime": 1,
    "decommissioning_duration": 1,
    "carbon_cost": 1,
    "carbon_content": 1,
}

# Define data labels
data_labels = {
    "discount_rate": "Discount rate (%)",
    "power": "Power (MWe)",
    "overnight_cost": "Overnight cost ($/kWe)",
    "capital_cost_contingency": "Capital cost contingency factor (%)",
    "capacity_factor": "Capacity factor (%)",
    "o_and_m_cost": "O&M cost ($/MWh)",
    "fuel_cost": "Fuel cost ($/MWh)",
    "decommissioning_cost_factor": "Decommissioning cost factor (%)",
    "construction_duration": "Construction duration (years)",
    "operational_lifetime": "Operational lifetime (years)",
    "decommissioning_duration": "Decommissioning duration (years)",
    "carbon_cost": "Cost of carbon ($/t CO2)",
    "carbon_content": "Carbon content (t CO2/MWh)",
}


# Function to generate the Plotly pie chart
def create_pie_chart(data):
    """Key functionality"""

    # capital cost
    power_kw = data["power"] * 1000  # kWe
    overnight_cost_total = data["overnight_cost"] * power_kw  # $
    capital_cost_cgy_abs = data["capital_cost_contingency"] / 100  # -
    overnight_cost_w_contingency = overnight_cost_total * (1 + capital_cost_cgy_abs)
    capital_cost_per_year = overnight_cost_w_contingency / data["construction_duration"]

    # fuel and O&M
    capacity_factor_abs = data["capacity_factor"] / 100
    mwh_per_year = HOURS_IN_YEAR * data["power"] * capacity_factor_abs
    o_and_m_cost_per_year = data["o_and_m_cost"] * mwh_per_year
    fuel_cost_per_year = data["fuel_cost"] * mwh_per_year

    # decommissioning
    decommissioning_cost_factor_abs = data["decommissioning_cost_factor"] / 100  # -
    decommissioning_cost = decommissioning_cost_factor_abs * overnight_cost_total
    decommissioning_cost_per_year = (
        decommissioning_cost / data["decommissioning_duration"]
    )

    # carbon
    carbon_cost_per_mwh = data["carbon_cost"] * data["carbon_content"]  # $/MWh
    carbon_cost_per_year = carbon_cost_per_mwh * mwh_per_year

    # discount rate
    discount_rate_abs = data["discount_rate"] / 100

    # timeline
    construction_start = PRESENT_YEAR
    construction_end = construction_start + int(data["construction_duration"]) - 1
    operation_start = construction_end + 1
    operation_end = operation_start + int(data["operational_lifetime"]) - 1
    decommissioning_start = operation_end + 1
    decommissioning_end = (
        decommissioning_start + int(data["decommissioning_duration"]) - 1
    )

    # cash flows
    cost_items_rolled = {
        "Capital": (construction_start, construction_end, capital_cost_per_year),
        "O&M": (operation_start, operation_end, o_and_m_cost_per_year),
        "Fuel": (operation_start, operation_end, fuel_cost_per_year),
        "Carbon": (operation_start, operation_end, carbon_cost_per_year),
        "Decommissioning": (
            decommissioning_start,
            decommissioning_end,
            decommissioning_cost_per_year,
        ),
    }

    # Create the cost_items dictionary from cost_items_rolled
    cost_items = evl.create_cost_items(cost_items_rolled)

    # Revenue in form of MWh per year
    revenue_data = evl.create_cash_flow((operation_start, operation_end, mwh_per_year))

    # LCOE
    lcoe = evl.calculate_lcoe(cost_items, revenue_data, discount_rate_abs, PRESENT_YEAR)

    # Cost data
    discounted_costs = evl.discount_cash_flows(
        cost_items, discount_rate_abs, PRESENT_YEAR
    )

    # Normalize values to 100% for each dictionary
    total = sum(discounted_costs.values())

    # Extract keys for labels
    labels = list(discounted_costs.keys())

    # Normalize to percentages
    values = [v / total * 100 for v in discounted_costs.values()]

    # Plotting
    title = f"LCOE {lcoe:.0f} $/MWh"

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=title, title_x=0.5, font=dict(size=16))

    return fig


# Streamlit app
def main():
    """The main function of the app"""
    st.write("## Cost Profile Calculator")
    st.write(
        "This applet calculates the Levelized Cost of Electricity (LCOE) using the [methodology]"
        "(https://iea.blob.core.windows.net/assets/ae17da3d-e8a5-4163-a3ec-2e6fb0b5677d/"
        "Projected-Costs-of-Generating-Electricity-2020.pdf)"
        " from the International Energy Agency (IEA) and the Organisation for"
        " Economic Co-operation and Development/Nuclear Energy Agency (OECD/NEA)."
        " It also shows the cost breakdown by category. You can change the inputs"
        " in the sidebar, the app will automatically update. Some of the inputs only"
        " appear by checking the toggle. The default values correspond to the median"
        " data for new nuclear power plants as per the report."
        " Source code: https://github.com/tannhorn/ele-cost/."
    )

    st.sidebar.header("Input Parameters")

    # Initialize or retrieve session state for user data
    if "user_data" not in st.session_state:
        st.session_state.user_data = default_values.copy()

    # Collect inputs from the user for basic inputs
    for category in basic_inputs:
        value_type = type(default_values[category])
        st.session_state.user_data[category] = st.sidebar.number_input(
            f"{data_labels[category]}:",
            value=st.session_state.user_data.get(category, default_values[category]),
            min_value=0 if value_type == int else 0.0,
            step=step_values[category],
        )

    # Add a checkbox to show additional inputs
    show_more = st.sidebar.checkbox("Show extra inputs")
    if show_more:
        for category in extra_inputs:
            value_type = type(default_values[category])
            st.session_state.user_data[category] = st.sidebar.number_input(
                f"{data_labels[category]}:",
                value=st.session_state.user_data.get(
                    category, default_values[category]
                ),
                min_value=0 if value_type == int else 0.0,
                step=step_values[category],
            )

    # Create and display the chart
    pie_chart = create_pie_chart(st.session_state.user_data)
    st.plotly_chart(pie_chart)


if __name__ == "__main__":
    main()
