from sysdata.arctic.arctic_futures_per_contract_prices import (
    arcticFuturesContractPriceData,
)
from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysobjects.roll_calendars import rollCalendar
from sysdata.csv.csv_roll_calendars import csvRollCalendarData

"""
Generate a 'best guess' roll calendar based on some price data for individual contracts

"""


def build_and_write_roll_calendar(
    instrument_code, output_datapath=None, check_before_writing=True
):

    if output_datapath is None:
        print("*** WARNING *** This will overwrite the provided roll calendar. Better to use a temporary directory!")

    artic_prices = arcticFuturesContractPriceData()
    mongo_rollparameters = mongoRollParametersData()
    csv_roll_calendars = csvRollCalendarData(output_datapath)

    dict_of_all_futures_contract_prices = artic_prices.get_all_prices_for_instrument(
        instrument_code)
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()

    roll_parameters_object = mongo_rollparameters.get_roll_parameters(
        instrument_code)

    # might take a few seconds
    print("Prepping roll calendar... might take a few seconds")
    roll_calendar = rollCalendar.create_from_prices(
        dict_of_futures_contract_prices, roll_parameters_object
    )

    # checks - this might fail
    roll_calendar.check_if_date_index_monotonic()

    # this should never fail
    roll_calendar.check_dates_are_valid_for_prices(
        dict_of_futures_contract_prices
    )

    # Write to csv
    # Will not work if an existing calendar exists

    if check_before_writing:
        check_happy_to_write = input(
            "Are you ok to write this csv to path %s? [might be worth writing and hacking manually] (yes/other)?" % output_datapath
        )
    else:
        check_happy_to_write = "yes"

    if check_happy_to_write == "yes":
        csv_roll_calendars.add_roll_calendar(instrument_code, roll_calendar, ignore_duplication=True)
    else:
        print("Not writing")

    return roll_calendar



def check_saved_roll_calendar(
    instrument_code, input_datapath=None
):

    if input_datapath is None:
        print("This will check the roll calendar in the default directory : are you are that's what you want to do?")


    csv_roll_calendars = csvRollCalendarData(input_datapath)

    roll_calendar = csv_roll_calendars.get_roll_calendar(instrument_code)

    artic_prices = arcticFuturesContractPriceData()

    dict_of_all_futures_contract_prices = artic_prices.get_all_prices_for_instrument(
        instrument_code)
    dict_of_futures_contract_prices = dict_of_all_futures_contract_prices.final_prices()

    print(roll_calendar)

    # checks - this might fail
    roll_calendar.check_if_date_index_monotonic()

    # this should never fail
    roll_calendar.check_dates_are_valid_for_prices(
        dict_of_futures_contract_prices
    )


    return roll_calendar


