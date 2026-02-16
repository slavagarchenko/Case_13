import math


def read_fuel_info(filepath: str = 'fuel_info.txt') -> List[Dict[str, Any]]:
    """
        Read fuel column information from a text file.

        This function parses a file containing information about fuel dispensing columns,
        including their column number, maximum workload capacity, and supported fuel types.

        Args:
            filepath (str): Path to the fuel information file. Defaults to 'fuel_info.txt'.
                           Each line should contain: column_number max_workload fuel_type1 fuel_type2...

        Returns:
            list: A list of dictionaries, each containing:
                - 'column_number': int, unique identifier for the fuel column
                - 'max_workload': int, maximum number of vehicles that can use this column simultaneously
                - 'fuel_type': list, fuel types supported by this column (e.g., ['95', '98'])
        """
    colums = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                column_info = {'column_number': int(parts[0]),
                               'max_workload': int(parts[1]),
                               'fuel_type': (parts[2:])
                               }
                colums.append(column_info)
    return colums


def read_input(filepath: str = 'input.txt') -> List[Dict[str, Any]]:
    """
        Read vehicle refueling requests from a text file.

        This function parses a file containing refueling requests with arrival times,
        required fuel amounts, and requested fuel types.

        Args:
            filepath (str): Path to the input file. Defaults to 'input.txt'.
                           Each line should contain: arrival_time fuel_amount fuel_type

        Returns:
            list: A list of dictionaries, each containing:
                - 'time': str, arrival time in "HH:MM" format
                - 'value': int, required fuel amount in liters
                - 'fuel_type': str, requested fuel type (e.g., '95', '98', '92')
        """
    requests = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                requests_info = {'time': (parts[0]),
                                 'value': int(parts[1]),
                                 'fuel_type': (parts[2])
                                 }
                requests.append(requests_info)
    return requests


def calculate_refueling_time(requests: List[Dict[str, Any]],
                             colums: List[Dict[str, Any]]) -> int:
    """
      Calculate the total time needed to process all refueling requests.

      This function simulates the refueling process by assigning vehicles to available
      fuel columns based on fuel type compatibility and current workload. It uses a
      greedy algorithm to select the earliest available column for each request.

      The refueling duration is calculated as ceil(fuel_amount / 10) minutes,
      assuming a refueling rate of 10 liters per minute.

      Args:
          requests (list): List of refueling requests from read_input()
          columns (list): List of fuel column information from read_fuel_info()

      Returns:
          int: The maximum finish time among all processed requests, in minutes.
               This represents the total time needed to complete all refueling operations.
      """

    def time_on_minutes(time_str: str) -> int:
        """
                Convert time string "HH:MM" to minutes since midnight.

                Args:
                    time_str (str): Time in "HH:MM" format (24-hour)

                Returns:
                    int: Total minutes since midnight
                """
        hours, minutes = map(int, time.split(':'))
        return hours * 60 + minutes

    colums_states = {}
    for col in colums:
        colums_states[col['column_number']] = []
    max_finish_time = 0
    for request in requests:
        arrival_time = time_on_minutes(request['time'])
        value = request['value']
        fuel_type = request['fuel_type']
        refueling_duration = math.ceil(value / 10)
        suitable_colums = [col for col in colums if fuel_type in col['fuel_type']]
        if not suitable_colums:
            continue
        best_colum = None
        earliest_available_time = float('inf')
        for col in suitable_colums:
            col_num = col['column_number']
            max_workload = col['max_workload']
            colums_states[col_num] = [time for time in colums_states[col_num] if time > arrival_time]
            if len(colums_states[col_num]) < max_workload:
                available_time = arrival_time
            else:
                colums_states[col_num].sort()
                available_time = max(arrival_time, colums_states[col_num][0])
            if available_time < earliest_available_time:
                earliest_available_time = available_time
                best_colum = col_num
        if best_colum is not None:
            start_time = earliest_available_time
            finish_time = start_time + refueling_duration
            colums_states[best_colum].append(finish_time)
            if len(colums_states[best_colum]) > colums[best_colum - 1]['max_workload']:
                colums_states[best_colum].sort()
                colums_states[best_colum].pop(0)
            max_finish_time = max(max_finish_time, finish_time)
    return max_finish_time


colums = read_fuel_info()
requests = read_input()
finish_time = calculate_refueling_time(requests, colums)
print(f'Общее время заправки:{finish_time // 60} часа,{finish_time % 60} минут')
