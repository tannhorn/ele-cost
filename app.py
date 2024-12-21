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
]
extra_inputs = [
    "construction_duration",
    "operational_lifetime",
    "decommissioning_duration",
    "capacity_factor",
    "capital_cost_contingency",
    "decommissioning_cost_factor",
]


# Function to generate the Plotly pie chart
def create_pie_chart(data):
    """Key functionality"""
    power_kw = data["power"] * 1000  # kWe

    overnight_cost_total = data["overnight_cost"] * power_kw  # $
    capital_cost_per_year = overnight_cost_total / data["construction_duration"]

    mwh_per_year = HOURS_IN_YEAR * data["power"] * data["capacity_factor"]
    o_and_m_cost_per_year = data["o_and_m_cost"] * mwh_per_year
    fuel_cost_per_year = data["fuel_cost"] * mwh_per_year

    decommissioning_cost = data["decommissioning_cost_factor"] * overnight_cost_total
    decommissioning_cost_per_year = (
        decommissioning_cost / data["decommissioning_duration"]
    )

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
    lcoe = evl.calculate_lcoe(
        cost_items, revenue_data, data["discount_rate"], PRESENT_YEAR
    )

    # Cost data
    discounted_costs = evl.discount_cash_flows(
        cost_items, data["discount_rate"], PRESENT_YEAR
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
    fig.update_layout(title_text=title, title_x=0.5)

    return fig


# Streamlit app
def main():
    """The main function of the app"""
    st.title("Cost Profile Calculator")

    st.sidebar.header("Input Parameters")

    # Define default values
    default_values = {
        "discount_rate": 0.07,  # -
        "power": 1137.0,  # MWe
        "overnight_cost": 3370.0,  # $/kWe
        "capital_cost_contingency": 0.15,  # -
        "capacity_factor": 0.8,  # -
        "o_and_m_cost": 11.6,  # $/MWh
        "fuel_cost": 9.33,  # $/MWh
        "decommissioning_cost_factor": 0.15,  # -
        "construction_duration": 7.0,  # years
        "operational_lifetime": 60.0,  # years
        "decommissioning_duration": 10.0,  # years
    }

    # Initialize or retrieve session state for user data
    if "user_data" not in st.session_state:
        st.session_state.user_data = default_values.copy()

    # Collect inputs from the user for basic inputs
    for category in basic_inputs:
        st.session_state.user_data[category] = st.sidebar.number_input(
            f"{category}:",
            value=st.session_state.user_data.get(category, default_values[category]),
            min_value=0.0,
            step=1.0,
        )

    # Add a checkbox to show additional inputs
    show_more = st.sidebar.checkbox("Show extra inputs")
    if show_more:
        for category in extra_inputs:
            st.session_state.user_data[category] = st.sidebar.number_input(
                f"{category}:",
                value=st.session_state.user_data.get(
                    category, default_values[category]
                ),
                min_value=0.0,
                step=1.0,
            )

    # Create and display the chart
    pie_chart = create_pie_chart(st.session_state.user_data)
    st.plotly_chart(pie_chart)


if __name__ == "__main__":
    main()
