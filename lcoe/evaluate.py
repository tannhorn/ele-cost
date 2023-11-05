class CashFlowData:
    def __init__(self, years, values, discount_rate=None):
        self.years = years
        self.values = values
        self.discount_rate = discount_rate

    def net_present_value(self, present_year, external_discount_rate=None):
        discount_rate = external_discount_rate if external_discount_rate is not None else self.discount_rate
        npv = 0.0
        for year, value in zip(self.years, self.values):
            periods_into_future = year - present_year
            npv += value / (1 + discount_rate) ** periods_into_future
        return npv

def create_cash_flow(expense_tuple,discount_rate=None):
    """
    Create a CashFlow object.

    Args:
        expense_tuple (tuple): Tuple containing (start_year, end_year, expense_value).
        discount_rate (float, optional): Discount rate for the cas flow.

    Returns:
        CashFlow object.
    """
    start_year, end_year, expense_value = expense_tuple
    years = list(range(start_year, end_year + 1))

    return CashFlowData(years, [expense_value for y in years], discount_rate)

def create_cost_item(cost_item_name, expense_tuple, discount_rate=None):
    """
    Create a cost item dictionary entry.

    Args:
        cost_item_name (str): Name of the cost item.
        expense_tuple (tuple): Tuple containing (start_year, end_year, expense_value).
        discount_rate (float, optional): Discount rate for the cost item.

    Returns:
        dict: Cost item dictionary entry with appropriate structure.
    """

    cost_item = {
        cost_item_name: create_cash_flow(expense_tuple,discount_rate)
    }

    return cost_item

def unroll_cost_item(cost_item_name,expense_data):
    """
    Body of the function below.
    """
    if isinstance(expense_data, tuple) and len(expense_data) == 3:
        # If expense_data is a tuple, assume it contains (start_year, end_year, expense_value)
        cost_item = create_cost_item(cost_item_name, expense_data)
    elif isinstance(expense_data, tuple) and len(expense_data) == 4:
        # If expense_data is a tuple and has 4 elements, assume it contains (start_year, end_year, expense_value, discount_rate)
        cost_item = create_cost_item(cost_item_name, expense_data[:-1], expense_data[-1])
    else:
        raise ValueError("Invalid format for expense data.")

    return cost_item

def create_cost_items(cost_items_rolled):
    """
    Create cost_items dictionary from cost_items_rolled.

    Args:
        cost_items_rolled (dict): Dictionary with cost_item_name as keys and expense_tuple as values,
                                  possibly including discount_rate.

    Returns:
        dict: Dictionary with cost_item_name as keys and corresponding expense tuples in the format used in cost_items.
    """
    cost_items = {}  # Initialize the cost_items dictionary

    for cost_item_name, expense_data in cost_items_rolled.items():
        cost_item = unroll_cost_item(cost_item_name,expense_data)
        cost_items.update(cost_item)

    return cost_items

def calculate_lcoe(cost_items, revenue_data, default_discount_rate, present_year):
    """
    Calculate the Levelized Cost of Energy (LCOE) for an energy infrastructure project.

    Args:
        cost_items (dict): Dictionary of cost items where keys are cost item names,
                           and values are CashFlowData objects.
        revenue_data (CashFlowData): CashFlowData object for revenue data.
        default_discount_rate (float): Default discount rate to be used if not specified for a cost item.
        present_year (int): The year against which all cash flows should be discounted.

    Returns:
        float: LCOE in $/MWh.
    """
    revenue_discount_rate = revenue_data.discount_rate or default_discount_rate
    total_discounted_revenue = revenue_data.net_present_value(present_year,revenue_discount_rate)

    total_discounted_expenses = 0.0
    for cost_item_name, cash_flow_data in cost_items.items():
        item_discount_rate = cash_flow_data.discount_rate or default_discount_rate
        total_discounted_expenses += cash_flow_data.net_present_value(present_year,item_discount_rate)

    lcoe = total_discounted_expenses / total_discounted_revenue

    return lcoe
