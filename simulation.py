import math
import heapq
import random
from typing import List, Dict, Any, Optional, Tuple
import ru_local as ru
import constants


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to 'HH:MM' format."""
    minutes = minutes % constants.MINUTES_IN_DAY
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def calculate_service_time(fuel_amount: int) -> int:
    """Calculate service time with random variation."""
    base_time = math.ceil(fuel_amount / constants.REFUELING_RATE)
    variation = random.choice([-1, 0, 1])
    return max(1, base_time + variation)


def prepare_columns_data(columns_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare column data structure for simulation."""
    columns = []
    for col in columns_info:
        column_data = {
            'number': col['column_number'],
            'max_queue': col['max_workload'],
            'fuel_types': col['fuel_type'],
            'queue': [],
            'current_client': None,
            'time_free': 0,
            'total_liters_sold': 0,
            'clients_served': 0,
            'sales_by_brand': {b: 0 for b in constants.VALID_GASOLINE_TYPES},
            'max_queue_observed': 0
        }
        columns.append(column_data)
    return sorted(columns, key=lambda x: x['number'])


def find_best_column(columns: List[Dict[str, Any]],
                     fuel_type: str) -> Optional[Dict[str, Any]]:
    """Find the best column for a client based on queue length."""
    suitable = []
    for col in columns:
        if (fuel_type in col['fuel_types'] and
                len(col['queue']) < col['max_queue']):
            suitable.append({
                'column': col,
                'queue_length': len(col['queue']),
                'number': col['number']
            })

    if not suitable:
        return None

    suitable.sort(key=lambda x: (x['queue_length'], x['number']))
    return suitable[0]['column']


def display_columns_state(columns: List[Dict[str, Any]]) -> None:
    """Display current state of all columns."""
    for col in sorted(columns, key=lambda x: x['number']):
        queue_str = ''
        for client in col['queue']:
            queue_str += ru.COLUMN["queue_marker"] + \
                str(client['service_time'])

        if col['current_client']:
            queue_str = (ru.COLUMN["queue_marker"] +
                         str(col['current_client']['service_time']) + queue_str)

        if not queue_str:
            queue_str = ru.COLUMN["empty_queue"]

        fuel_types_str = ' '.join(col['fuel_types'])
        print(ru.COLUMN["column_info"].format(
            col['number'], col['max_queue'], fuel_types_str, queue_str
        ))


def process_arrival(client: Dict[str, Any], columns: List[Dict[str, Any]],
                    current_time: int, stats: Dict[str, int]) -> Optional[Dict[str, Any]]:
    """Process a new client arrival."""
    fuel_type = client['fuel_type']
    fuel_amount = client['value']
    service_time = calculate_service_time(fuel_amount)

    best_column = find_best_column(columns, fuel_type)
    client_info = f"{client['time']} {fuel_type} {fuel_amount} {service_time}"

    if not best_column:
        print(ru.EVENTS["rejected"].format(
            minutes_to_time(current_time), client_info))
        stats['rejected'] += 1
        return None

    queue_client = {
        'time': client['time'],
        'arrival_minutes': current_time,
        'amount': fuel_amount,
        'fuel_type': fuel_type,
        'service_time': service_time,
        'column': best_column['number']
    }

    best_column['queue'].append(queue_client)

    current_queue_len = len(best_column['queue'])
    if current_queue_len > best_column['max_queue_observed']:
        best_column['max_queue_observed'] = current_queue_len

    print(ru.EVENTS["new_client"].format(
        minutes_to_time(current_time), client_info, best_column['number']
    ))

    if (best_column['current_client'] is None and
            best_column['time_free'] <= current_time):
        return start_service(best_column, current_time)

    return None


def start_service(column: Dict[str, Any],
                  current_time: int) -> Optional[Dict[str, Any]]:
    """Start serving the next client in queue."""
    if not column['queue'] or column['current_client'] is not None:
        return None

    client = column['queue'].pop(0)
    column['current_client'] = client

    start = max(current_time, column['time_free'])
    finish = start + client['service_time']
    column['time_free'] = finish

    column['total_liters_sold'] += client['amount']
    column['clients_served'] += 1
    column['sales_by_brand'][client['fuel_type']] += client['amount']

    return {
        'time': finish,
        'type': 'departure',
        'column': column['number'],
        'client': client
    }


def process_departure(event: Dict[str, Any], columns: List[Dict[str, Any]],
                      current_time: int, stats: Dict[str, int]) -> Optional[Dict[str, Any]]:
    """Process a client departure."""
    column = next((c for c in columns if c['number'] == event['column']), None)

    if column and column['current_client'] is not None:
        current = column['current_client']
        event_client = event['client']

        if (current['arrival_minutes'] == event_client['arrival_minutes'] and
                current['amount'] == event_client['amount'] and
                current['fuel_type'] == event_client['fuel_type']):

            column['current_client'] = None

            client = event['client']
            client_info = (
                f"{minutes_to_time(client['arrival_minutes'])} "
                f"{client['fuel_type']} {client['amount']} {client['service_time']}"
            )
            print(ru.EVENTS["departure"].format(
                minutes_to_time(current_time), client_info))

            stats['served'] += 1

            if column['queue']:
                return start_service(column, current_time)

    return None


def run_simulation(columns_info: List[Dict[str, Any]],
                   clients_data: List[Dict[str, Any]]) -> Tuple[Dict[str, int], List[Dict]]:
    """Run the complete gas station simulation."""
    columns = prepare_columns_data(columns_info)

    print("\n" + "=" * 60)
    print(ru.SYSTEM["simulation_start"])
    print("=" * 60 + "\n")

    event_queue = []
    stats = {'served': 0, 'rejected': 0}
    event_counter = 0

    for client in clients_data:
        heapq.heappush(event_queue,
                       (client['minutes'], event_counter, 'arrival', client))
        event_counter += 1

    current_time = 0
    last_time = -1

    while event_queue and current_time <= constants.MINUTES_IN_DAY:
        time, counter, event_type, data = heapq.heappop(event_queue)
        current_time = time

        if current_time > constants.MINUTES_IN_DAY:
            break

        if current_time != last_time:
            if last_time != -1:
                print()
            last_time = current_time

        if event_type == 'arrival':
            dep_event = process_arrival(data, columns, current_time, stats)
            if dep_event:
                heapq.heappush(event_queue, (
                    dep_event['time'], event_counter, dep_event['type'], dep_event
                ))
                event_counter += 1

            for col in columns:
                if col['current_client'] is None and col['queue']:
                    dep = start_service(col, current_time)
                    if dep:
                        heapq.heappush(event_queue, (
                            dep['time'], event_counter, dep['type'], dep
                        ))
                        event_counter += 1

        elif event_type == 'departure':
            next_dep = process_departure(data, columns, current_time, stats)
            if next_dep:
                heapq.heappush(event_queue, (
                    next_dep['time'], event_counter, next_dep['type'], next_dep
                ))
                event_counter += 1

        display_columns_state(columns)

    print("\n" + "=" * 60)
    print(ru.SYSTEM["simulation_end"])
    print("=" * 60 + "\n")

    print(ru.SYSTEM["final_stats"])
    print(ru.SYSTEM["served"].format(stats['served']))
    print(ru.SYSTEM["rejected"].format(stats['rejected']))
    print(ru.SYSTEM["total"].format(stats['served'] + stats['rejected']))

    return stats, columns
