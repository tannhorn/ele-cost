import json
import sys
sys.path.append('..')

from lcoe import evaluate as evl

if __name__ == "__main__":
    # world
    discount_rate = 0.07
    present_year = 1

    # durations
    construction_duration = 7 # years
    operational_lifetime = 60 # years
    decommissioning_duration = 10 # years

    # configuration
    power = 1000 # MWe
    power_kw = power * 1000 # kWe

    # overnight_costs
    overnight_cost_per_kwe = 3370 # $/kWe, median
    overnight_cost_net = overnight_cost_per_kwe * power_kw

    contingency_factor = 0.15
    overnight_cost = overnight_cost_net * (1+contingency_factor)
    capital_cost_per_year = overnight_cost/construction_duration

    # production
    capacity_factor = 0.85
    hours_in_year = 8760
    mwh_per_year = hours_in_year*power*capacity_factor
 
    # O&M
    o_and_m_cost_per_kw_year = 80 # $/kwe/year
    o_and_m_cost_per_year = o_and_m_cost_per_kw_year * power_kw

    # fuel
    front_end_fuel_cost_per_mwh = 7 # $/MWh
    back_end_fuel_cost_per_mwh = 2.33 # $/MWh
    total_fuel_cost_per_mwh = front_end_fuel_cost_per_mwh\
                            + back_end_fuel_cost_per_mwh

    fuel_cost_per_year = total_fuel_cost_per_mwh*mwh_per_year

    # decommissioning
    decommissioning_cost_factor = 0.15
    decommissioning_cost = decommissioning_cost_factor\
                         * overnight_cost
    decommissioning_cost_per_year = decommissioning_cost\
                                  / decommissioning_duration

    # timeline
    construction_start = present_year
    construction_end = present_year + construction_duration - 1
    operation_start = construction_end + 1
    operation_end = operation_start + operational_lifetime - 1
    decommissioning_start = operation_end + 1
    decommissioning_end = decommissioning_start\
                        + decommissioning_duration - 1

    # cash flows
    cost_items_rolled = {
      "Capital": (construction_start, construction_end, capital_cost_per_year),
      "O&M": (operation_start, operation_end, o_and_m_cost_per_year),
      "Fuel": (operation_start, operation_end, fuel_cost_per_year),
      "Decommissioning": (decommissioning_start, decommissioning_end, decommissioning_cost_per_year),
    }

    # Create the cost_items dictionary from cost_items_rolled
    cost_items = evl.create_cost_items(cost_items_rolled)

    # Revenue in form of MWh per year
    revenue_data = evl.create_cash_flow(
            (operation_start, operation_end, mwh_per_year)
            )

    # LCOE eval
    lcoe = evl.calculate_lcoe(cost_items, revenue_data, discount_rate, present_year)

    # print
    print(f"LCOE with a discount rate of {discount_rate*100}%: ${lcoe:.2f}/MWh")
