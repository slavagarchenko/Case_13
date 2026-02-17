import random
from datetime import datetime
import ru_local as ru
import constants
import file_operations
import simulation
import statistics
import traceback


def main() -> None:
    """
        Main function of the gas station simulation program.

        Orchestrates the entire simulation process by:
        1. Loading column configuration and client data from files.
        2. Displaying data summaries and statistics.
        3. Running the simulation with seeded random behavior.
        4. Calculating and displaying final statistics.
        5. Handling any exceptions that occur during execution.

        Returns:
            None
        """
    print("\n" + "=" * 60)
    print(ru.SYSTEM["program_title"])
    print("=" * 60 + "\n")

    try:
        columns_info = file_operations.read_fuel_info('fuel_info.txt')
        if not columns_info:
            print(ru.ERRORS["no_columns"])
            input(ru.SYSTEM["press_enter_exit"])
            return

        clients_data = file_operations.read_input('input.txt')
        if not clients_data:
            print(ru.ERRORS["no_clients"])
            input(ru.SYSTEM["press_enter_exit"])
            return

        show_calculation = input(ru.SYSTEM["show_calculation_prompt"]).lower()
        if show_calculation == "y":
            file_operations.print_refueling_summary(columns_info, clients_data)
        if show_calculation == "n":
            return

        print(
            f"\n{ru.SYSTEM['total_columns_loaded'].format(len(columns_info))}")
        print(ru.SYSTEM['total_clients_loaded'].format(len(clients_data)))
        print(ru.SYSTEM['gasoline_types'].format(
            ', '.join(constants.VALID_GASOLINE_TYPES)))

        random.seed(datetime.now().timestamp())
        print(ru.SYSTEM["running_full_simulation"])

        stats, columns = simulation.run_simulation(columns_info, clients_data)
        statistics.calculate_statistics(stats, columns)

    except Exception as e:
        print(ru.ERRORS["simulation_error"].format(str(e)))
        print(ru.SYSTEM["critical_error"])
        traceback.print_exc()

    input("\n" + ru.SYSTEM["press_enter_exit"])


if __name__ == "__main__":
    main()
