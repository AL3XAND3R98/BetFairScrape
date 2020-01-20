import os, json, time, csv

from datetime import datetime, timedelta

from betfair_python_rest.managers import (
    BetFairAPIManagerBetting,
    BetFairAPIManagerAccounts,
)
from betfair_python_rest.forms import (
    MarketFilterAndTimeGranularityForm,
    MarketFilterAndLocaleForm,
    ListMarketCatalogueForm,
    ListMarketBookForm,
    ListRunnerBookForm,
    ListMarketProfitAndLossForm,
    ListCurrentOrdersForm,
    LimitOrder,
    ListClearedOrdersForm,
    PlaceOrderForm,
    CancelOrdersForm,
    ReplaceOrdersForm,
    PlaceInstruction,
    CancelInstruction,
    ReplaceInstruction,
    UpdateOrdersForm,
    UpdateInstruction,
)
from betfair_python_rest.enums.betting import (
    TimeGranularity,
    BetStatus,
    OrderType,
    PersistenceType,
    SideChoices,
    MarketProjection,
    PriceData,
    MatchProjection,
)

'''KEY DETaiLS GO HERE'''

api_key = "API KEY GOES HERE"
login = "USERNAME GOES HERE"
password = "PASSWORD GOES HERE"
outputPath = "outputFile.csv"


class CustomBetFairAPIManagerBetting(BetFairAPIManagerBetting):
    cwd = os.getcwd()
    crt_path = os.path.join(cwd, "certFiles", "client-2048.crt")
    crt_key_path = os.path.join(cwd, "certFiles", "client-2048.key")


test_manager = CustomBetFairAPIManagerBetting(
    login, password, api_key, log_mode=True, raise_exceptions=False
)

"""LIST COMPETITIONS IN ENGLISH"""


def list_competitions(apiManager):
    market_and_locale = MarketFilterAndLocaleForm(text_query="English")
    return apiManager.list_competitions(request_class_object=market_and_locale)


"""LIST EVENTS IN COMPETITION"""


def list_events(apiManager, competitionId):
    market_and_locale = MarketFilterAndLocaleForm(competitions_ids=[competitionId])
    return apiManager.list_events(request_class_object=market_and_locale)


"""LIST MARKETS IN EVENT"""


def list_market_catalogue(apiManager, eventId):
    market_projection = [
        MarketProjection.RUNNER_DESCRIPTION.name,
        MarketProjection.RUNNER_METADATA.name,
    ]
    list_market_catalogue_form = ListMarketCatalogueForm(
        market_projection=market_projection, event_ids=[eventId]
    )
    return apiManager.list_market_catalogue(
        request_class_object=list_market_catalogue_form
    )


"""LIST MARKETS BOOK"""


def list_market_book(apiManager, marketId):
    match_proj = MatchProjection.ROLLED_UP_BY_PRICE.name
    price_datz = PriceData.EX_TRADED.name
    list_market_catalogue_form = ListMarketBookForm(
        market_ids=[marketId], price_data=[price_datz]
    )
    return apiManager.list_market_book(request_class_object=list_market_catalogue_form)


titleRow = [
    "League",
    "EventID",
    "Event Name",
    "Open Time",
    "Market ID",
    "Market Name",
    "Market Total Matched",
    "Market Total Available",
    "SelectionID",
    "Selection Name",
    "Selection Handicap",
    "Last Price Traded",
    "Total Matched",
]

with open(outputPath, "w+") as csv_file:
    writer = csv.writer(csv_file, delimiter=",")
    writer.writerow(titleRow)






#leaguesJson = test_list_competitions(test_manager)


premierLeague = 10932509
faCup = 30558
championship = 7129730
league1 = 35
laLiga = 117


eventsJson = list_events(test_manager, premierLeague)


print("--------------------------------DATA--------------------------------")

for event in eventsJson:
    event = event["event"]
    eventId = event["id"]
    eventName = event["name"]
    eventOpenDate = event["openDate"]

    marketsJson = list_market_catalogue(test_manager, eventId)
    print("\n")
    print(eventName + "  ::  " + eventId)
    print(
        "------------------------------------------------------------------------------"
    )

    for market in marketsJson:
        marketId = market["marketId"]
        marketName = market["marketName"]

        runnersList = {}
        for runner in market["runners"]:
            runnersList[runner["selectionId"]] = {}
            runnersList[runner["selectionId"]]["name"] = runner["runnerName"]

        marketJson = list_market_book(test_manager, marketId)
        print(marketJson)
        if "faultcode" not in json.dumps(marketJson):
            marketJson = marketJson[0]
            marketTotalMatched = marketJson["totalMatched"]
            marketTotalAvailable = marketJson["totalAvailable"]

            print(marketName + "  ::  " + marketId)
            print("Market Total Matched: " + str(marketTotalMatched))
            print("Market Total Available: " + str(marketTotalAvailable))
            print("\n")

            for runner in marketJson["runners"]:
                if runner["status"] == "ACTIVE":
                    try:
                        selectionId = runner["selectionId"]
                       
                        runnersList[selectionId]["handicap"] = runner["handicap"]
                        runnersList[selectionId]["totalMatched"] = runner["totalMatched"]
                        try:
                            runnersList[selectionId]["lastPriceTraded"] = runner[
                                "lastPriceTraded"
                            ]
                        except:
                            runnersList[selectionId]["lastPriceTraded"] = 0.0

                        print(
                            str(runnersList[selectionId]["name"])
                            + "  ::   "
                            + str(runnersList[selectionId]["handicap"])
                            + "  ::   "
                            + str(runnersList[selectionId]["lastPriceTraded"])
                        )


                        line = []

                        line.append("Premier League")
                        line.append(eventId)
                        line.append(eventName)
                        line.append(eventOpenDate)
                        line.append(marketId)
                        line.append(marketName)
                        line.append(marketTotalMatched)
                        line.append(marketTotalAvailable)
                        line.append(selectionId)
                        line.append(runnersList[selectionId]["name"])
                        line.append(runnersList[selectionId]["handicap"])
                        try:
                            line.append(runnersList[selectionId]["lastPriceTraded"])
                        except:
                            line.append(0.0)
                        try:
                            line.append(runnersList[selectionId]["totalMatched"])
                        except:
                            line.append(0.0)

                        with open(outputPath, "a+") as csv_file:
                            writer = csv.writer(csv_file, delimiter=",")

                            writer.writerow(line)
                    except KeyError:
                        print("Malformed Row")
