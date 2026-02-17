from typing import Dict, List, Any
import ru_local as ru
import constants


def calculate_statistics(
        stats: Dict[str, int],
        columns: List[Dict[str, Any]]
) -> None:
    """
        Calculate and display final simulation statistics.

        Analyzes the simulation results including:
        - Total fuel sales by brand and corresponding revenue.
        - Lost revenue analysis from rejected clients.
        - Column utilization metrics 
                (served clients, liters sold, queue lengths).
        - Profitability analysis and recommendations for business improvements.
        - Per-column detailed statistics.

        Args:
            stats (Dict[str, int]): Simulation statistics containing 
                                    'served' and 'rejected' counts.
            columns (List[Dict[str, Any]]): List of column data structures 
                                    with sales information.
        Returns:
            None
        """
    print(ru.STATISTICS["simulation_period"])
    print()

    total_by_brand = {brand: 0 for brand in constants.VALID_GASOLINE_TYPES}
    total_sales = 0
    column_utilization = []

    for col in columns:
        for brand, liters in col['sales_by_brand'].items():
            total_by_brand[brand] += liters

        col_util = {
            'number': col['number'],
            'served': col['clients_served'],
            'liters': col['total_liters_sold'],
            'max_queue': col['max_queue'],
            'max_observed': col.get('max_queue_observed', 0),
            'fuel_types': col['fuel_types']
        }
        column_utilization.append(col_util)

    print(ru.STATISTICS["total_sold"])
    for brand, liters in total_by_brand.items():
        sales = liters * constants.GASOLINE_PRICES[brand]
        total_sales += sales
        print(ru.STATISTICS["by_brand"].format(brand, liters, sales))

    print()
    print(ru.STATISTICS["total_sales"].format(total_sales))
    print()

    print(ru.LOSS_ANALYSIS["title"])

    avg_check = total_sales / stats['served'] if stats['served'] > 0 else 0
    lost_revenue = stats['rejected'] * avg_check
    lost_liters = stats['rejected'] * 35

    print(ru.LOSS_ANALYSIS["lost_clients"].format(stats['rejected']))
    print(ru.LOSS_ANALYSIS["avg_check"].format(avg_check))
    print(ru.LOSS_ANALYSIS["lost_revenue"].format(lost_revenue))
    print(ru.LOSS_ANALYSIS["lost_liters"].format(lost_liters))

    print(ru.UTILIZATION["title"])

    for col in column_utilization:
        fuel_types_str = ', '.join(col['fuel_types'])
        utilization = (col['served'] / 100) * 100 if col['served'] > 0 else 0

        print(ru.UTILIZATION["column_header"].format(
            col['number'], fuel_types_str))
        print(ru.UTILIZATION["served"].format(col['served']))
        print(ru.UTILIZATION["liters"].format(col['liters']))
        print(ru.UTILIZATION["utilization"].format(utilization))
        print(ru.UTILIZATION["max_queue"].format(col['max_queue']))
        print(ru.UTILIZATION["max_observed"].format(col['max_observed']))

    print(ru.PROFITABILITY["title"])

    print(ru.PROFITABILITY["current_revenue"].format(total_sales))
    print(ru.PROFITABILITY["lost_daily"].format(lost_revenue))
    print(ru.PROFITABILITY["lost_monthly"].format(lost_revenue * 30))
    print(ru.PROFITABILITY["new_column_cost"].format(
        constants.NEW_COLUMN_COST))
    print(ru.PROFITABILITY["monthly_cost"].format(
        constants.MONTHLY_OPERATING_COST))

    monthly_lost = lost_revenue * 30
    additional_revenue = monthly_lost * constants.POTENTIAL_RECAPTURE_RATE

    print(ru.PROFITABILITY["additional_revenue"].format(additional_revenue))

    if additional_revenue > constants.MONTHLY_OPERATING_COST:
        net_profit = additional_revenue - constants.MONTHLY_OPERATING_COST
        payback = constants.NEW_COLUMN_COST / net_profit

        print(ru.PROFITABILITY["net_profit"].format(net_profit))
        print(ru.PROFITABILITY["payback"].format(payback))

        if payback < 24:
            print(ru.PROFITABILITY["recommend_yes"])

        elif payback < 36:
            print(ru.PROFITABILITY["recommend_maybe"])

        else:
            print(ru.PROFITABILITY["recommend_no"])

    else:
        print(ru.PROFITABILITY["covers_no"])

    print(ru.PROFITABILITY["alternative_title"])

    loss_percentage = (stats['rejected'] /
                       (stats['served'] + stats['rejected'])) * 100

    if loss_percentage > 20:
        print(ru.PROFITABILITY["high_loss"].format(loss_percentage))

    overloaded = [
        c for c in column_utilization if c['max_observed'] >= c['max_queue']]
    if overloaded:
        print(ru.PROFITABILITY["increase_queue"])

        for col in overloaded:
            print(ru.PROFITABILITY["column_item"].format(
                col['number'], col['max_queue'], col['max_observed']))

    print("\n" + "=" * 40)
    print(ru.STATISTICS["per_column_title"])
    print("=" * 40)

    for col in sorted(columns, key=lambda x: x['number']):
        print(ru.STATISTICS["column_number"].format(col['number']))
        print(ru.STATISTICS["clients_served"].format(col['clients_served']))
        print(ru.STATISTICS["liters_sold"].format(col['total_liters_sold']))

        col_sales = sum(
            col['sales_by_brand'][b] * constants.GASOLINE_PRICES[b]
            for b in constants.VALID_GASOLINE_TYPES
        )
        print(ru.STATISTICS["revenue"].format(col_sales))
