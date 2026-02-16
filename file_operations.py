import math
from typing import List, Dict, Any
import ru_local as ru
import constants


def read_fuel_info(filepath: str = 'fuel_info.txt') -> List[Dict[str, Any]]:
    """
    Read fuel column information from a text file.

    Args:
        filepath: Path to the fuel information file.

    Returns:
        List of dictionaries with column information.
    """
    columns = []
    print(ru.FILES["reading_columns"].format(filepath))

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split()
                if len(parts) < 3:
                    print(ru.FILES["invalid_format"].format(line))
                    continue

                try:
                    column_number = int(parts[0])
                    max_workload = int(parts[1])
                    fuel_types = parts[2:]

                    valid_fuel_types = [
                        ft for ft in fuel_types
                        if ft in constants.VALID_GASOLINE_TYPES
                    ]

                    if valid_fuel_types:
                        column_info = {
                            'column_number': column_number,
                            'max_workload': max_workload,
                            'fuel_type': valid_fuel_types
                        }
                        columns.append(column_info)

                except ValueError:
                    print(ru.FILES["invalid_format"].format(line))

    except FileNotFoundError:
        print(ru.FILES["file_not_found"].format(filepath))
        return []

    except Exception as e:
        print(ru.ERRORS["simulation_error"].format(str(e)))
        return []

    columns.sort(key=lambda x: x['column_number'])
    print(ru.FILES["columns_loaded"].format(len(columns)))

    return columns


def read_input(filepath: str = 'input.txt') -> List[Dict[str, Any]]:
    """
    Read vehicle refueling requests from a text file.

    Args:
        filepath: Path to the input file.

    Returns:
        List of dictionaries with client requests.
    """
    requests = []
    print(ru.FILES["reading_input"].format(filepath))

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split()
                if len(parts) != 3:
                    print(ru.FILES["invalid_format"].format(line))
                    continue

                time_str = parts[0]

                try:
                    hours, minutes = map(int, time_str.split(':'))
                    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                        print(ru.ERRORS["invalid_time"].format(time_str))
                        continue

                    fuel_amount = int(parts[1])
                    if fuel_amount <= 0:
                        continue

                    fuel_type = parts[2]
                    if fuel_type not in constants.VALID_GASOLINE_TYPES:
                        print(ru.ERRORS["invalid_gasoline"].format(fuel_type))
                        continue

                    minutes_since_midnight = hours * 60 + minutes

                    request_info = {
                        'time': time_str,
                        'value': fuel_amount,
                        'fuel_type': fuel_type,
                        'minutes': minutes_since_midnight
                    }
                    requests.append(request_info)

                except ValueError:
                    print(ru.FILES["invalid_format"].format(line))

    except FileNotFoundError:
        print(ru.FILES["file_not_found"].format(filepath))
        return []

    except Exception as e:
        print(ru.ERRORS["simulation_error"].format(str(e)))
        return []

    requests.sort(key=lambda x: x['minutes'])
    print(ru.FILES["clients_loaded"].format(len(requests)))

    return requests


def calculate_refueling_time(requests: List[Dict[str, Any]],
                             columns: List[Dict[str, Any]]) -> int:
    """
    Calculate total time needed to process all refueling requests.

    Args:
        requests: List of refueling requests.
        columns: List of column information.

    Returns:
        Maximum finish time in minutes.
    """
    if not requests or not columns:
        print(ru.ERRORS["no_data"])
        return 0

    columns_states = {col['column_number']: [] for col in columns}
    max_finish_time = 0

    for request in requests:
        arrival_time = request['minutes']
        value = request['value']
        fuel_type = request['fuel_type']
        refueling_duration = math.ceil(value / constants.REFUELING_RATE)

        suitable_columns = [
            col for col in columns if fuel_type in col['fuel_type']
        ]

        if not suitable_columns:
            print(ru.EVENTS["skipped_request"].format(
                fuel_type, request['time']))
            continue

        best_column = None
        earliest_available_time = float('inf')

        for col in suitable_columns:
            col_num = col['column_number']
            max_workload = col['max_workload']

            columns_states[col_num] = [
                t for t in columns_states[col_num] if t > arrival_time
            ]

            if len(columns_states[col_num]) < max_workload:
                available_time = arrival_time

            else:
                columns_states[col_num].sort()
                available_time = max(arrival_time, columns_states[col_num][0])

            if available_time < earliest_available_time:
                earliest_available_time = available_time
                best_column = col_num

        if best_column is not None:
            finish_time = earliest_available_time + refueling_duration
            columns_states[best_column].append(finish_time)

            column_max = next(
                col['max_workload'] for col in columns
                if col['column_number'] == best_column
            )

            if len(columns_states[best_column]) > column_max:
                columns_states[best_column].sort()
                columns_states[best_column].pop(0)

            max_finish_time = max(max_finish_time, finish_time)

    return max_finish_time


def print_refueling_summary(columns: List[Dict[str, Any]],
                            requests: List[Dict[str, Any]]) -> None:
    """Print summary of refueling time calculation."""
    print(ru.CALCULATION["title"])
    print(ru.CALCULATION['columns_count'].format(len(columns)))
    print(ru.CALCULATION['requests_count'].format(len(requests)))

    for col in columns:
        fuel_types_str = ', '.join(col['fuel_type'])
        print(ru.CALCULATION["column_info"].format(
            col['column_number'], col['max_workload'], fuel_types_str
        ))

    finish_time = calculate_refueling_time(requests, columns)
    hours = finish_time // 60
    minutes = finish_time % 60

    print(ru.CALCULATION["total_time"].format(hours, minutes))
    print(ru.CALCULATION["total_days"].format(
        finish_time / constants.MINUTES_IN_DAY))
