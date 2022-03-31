# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
from datetime import time
from dataclasses import dataclass
from decimal import Decimal, Context, ROUND_HALF_UP
from enum import Enum

import discord
import yfinance as yf
from discord import app_commands
from discord.ext import commands, tasks

from main import CBot


def fifteen_min_interval_generator():
    """Generator for 15 min intervals for a day from 00:00 to 23:45 as time objects"""
    for hour in range(24):
        for minute in range(0, 60, 15):
            yield time(hour, minute)


class tickers(Enum):
    """Enum of tickers to be used in the stock commands"""

    AAPL = "Apple Inc."
    MSFT = "Microsoft Corporation"
    GOOG = "Alphabet Inc."
    FB = "Facebook Inc."
    AMZN = "Amazon.com Inc."
    TSLA = "Tesla Inc."
    INTC = "Intel Corporation"
    CSCO = "Cisco Systems Inc."
    NVDA = "NVIDIA Corporation"
    ORCL = "Oracle Corporation"
    PYPL = "PayPal Holdings Inc."
    QCOM = "Qualcomm Inc."
    CMCSA = "Comcast Corporation"
    GPRO = "GoPro Inc."
    TWTR = "Twitter Inc."
    GME = "GameStop Corp."
    BTC_USD = "Bitcoin"
    ETH_USD = "Ethereum"
    LTC_USD = "Litecoin"
    XRP_USD = "Ripple"
    BCH_USD = "Bitcoin Cash"
    ADA_USD = "Cardano"
    XMR_USD = "Monero"
    DASH_USD = "Dash"
    EOS_USD = "EOS"


@dataclass
class Stock:
    name: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: Decimal

    def __init__(self, **data):
        """Initializes a stock object."""
        self.name = data["name"]
        self.price = Decimal(data["price"], Context(prec=2, rounding=ROUND_HALF_UP))
        self.change = Decimal(data["change"], Context(prec=2, rounding=ROUND_HALF_UP))
        self.change_percent = Decimal(
            data["change_percent"], Context(prec=2, rounding=ROUND_HALF_UP)
        )
        self.volume = Decimal(data["volume"], Context(prec=2, rounding=ROUND_HALF_UP))

    def as_dict(self):
        """Returns a dict representation of the stock."""
        return {
            "name": self.name,
            "price": str(self.price),
            "change": str(self.change),
            "volume": str(self.volume),
        }


STOCKS = [
    "AAPL",
    "MSFT",
    "GOOG",
    "FB",
    "AMZN",
    "TSLA",
    "INTC",
    "CSCO",
    "NVDA",
    "ORCL",
    "PYPL",
    "QCOM",
    "CMCSA",
    "GPRO",
    "TWTR",
    "GME",
    "BTC-USD",
    "ETH-USD",
    "LTC-USD",
    "XRP-USD",
    "BCH-USD",
    "ADA-USD",
    "XMR-USD",
    "DASH-USD",
    "EOS-USD",
]


@dataclass
class StockDict:
    """
    A dictionary of stock objects, with the stock symbol as the key.
    Has a variety of methods to update, create, and export the stock objects.
    """

    AAPL: Stock
    MSFT: Stock
    GOOG: Stock
    FB: Stock
    AMZN: Stock
    TSLA: Stock
    INTC: Stock
    CSCO: Stock
    NVDA: Stock
    ORCL: Stock
    PYPL: Stock
    QCOM: Stock
    CMCSA: Stock
    GPRO: Stock
    TWTR: Stock
    GME: Stock
    BTC: Stock
    ETH: Stock
    LTC: Stock
    XRP: Stock
    BCH: Stock
    ADA: Stock
    XMR: Stock
    DASH: Stock
    EOS: Stock

    def __init__(self, **data: Stock):
        """Initializes a StockDict object."""
        self.AAPL = data["AAPL"]
        self.MSFT = data["MSFT"]
        self.GOOG = data["GOOG"]
        self.FB = data["FB"]
        self.AMZN = data["AMZN"]
        self.TSLA = data["TSLA"]
        self.INTC = data["INTC"]
        self.CSCO = data["CSCO"]
        self.NVDA = data["NVDA"]
        self.ORCL = data["ORCL"]
        self.PYPL = data["PYPL"]
        self.QCOM = data["QCOM"]
        self.CMCSA = data["CMCSA"]
        self.GPRO = data["GPRO"]
        self.TWTR = data["TWTR"]
        self.GME = data["GME"]
        self.BTC = data["BTC"]
        self.ETH = data["ETH"]
        self.LTC = data["LTC"]
        self.XRP = data["XRP"]
        self.BCH = data["BCH"]
        self.ADA = data["ADA"]
        self.XMR = data["XMR"]
        self.DASH = data["DASH"]
        self.EOS = data["EOS"]

    @classmethod
    def empty(cls):
        """Returns an empty StockDict object."""
        return cls(
            AAPL=Stock(
                name="Apple Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            MSFT=Stock(
                name="Microsoft Corporation",
                price=0,
                change=0,
                change_percent=0,
                volume=0,
            ),
            GOOG=Stock(
                name="Alphabet Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            FB=Stock(
                name="Facebook Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            AMZN=Stock(
                name="Amazon.com Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            TSLA=Stock(
                name="Tesla Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            INTC=Stock(
                name="Intel Corporation", price=0, change=0, change_percent=0, volume=0
            ),
            CSCO=Stock(
                name="Cisco Systems Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            NVDA=Stock(
                name="NVIDIA Corporation", price=0, change=0, change_percent=0, volume=0
            ),
            ORCL=Stock(
                name="Oracle Corporation", price=0, change=0, change_percent=0, volume=0
            ),
            PYPL=Stock(
                name="PayPal Holdings Inc.",
                price=0,
                change=0,
                change_percent=0,
                volume=0,
            ),
            QCOM=Stock(
                name="Qualcomm Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            CMCSA=Stock(
                name="Comcast Corporation",
                price=0,
                change=0,
                change_percent=0,
                volume=0,
            ),
            GPRO=Stock(
                name="GoPro Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            TWTR=Stock(
                name="Twitter Inc.", price=0, change=0, change_percent=0, volume=0
            ),
            GME=Stock(
                name="GameStop Corp.", price=0, change=0, change_percent=0, volume=0
            ),
            BTC=Stock(name="Bitcoin", price=0, change=0, change_percent=0, volume=0),
            ETH=Stock(name="Ethereum", price=0, change=0, change_percent=0, volume=0),
            LTC=Stock(name="Litecoin", price=0, change=0, change_percent=0, volume=0),
            XRP=Stock(name="Ripple", price=0, change=0, change_percent=0, volume=0),
            BCH=Stock(
                name="Bitcoin Cash", price=0, change=0, change_percent=0, volume=0
            ),
            ADA=Stock(name="Cardano", price=0, change=0, change_percent=0, volume=0),
            XMR=Stock(name="Monero", price=0, change=0, change_percent=0, volume=0),
            DASH=Stock(name="Dash", price=0, change=0, change_percent=0, volume=0),
            EOS=Stock(name="EOS", price=0, change=0, change_percent=0, volume=0),
        )

    async def update(self, stock: tuple[str, Stock]):
        """Updates a stock object with the given stock."""
        if any(
            item.is_nan()
            for item in [
                stock[1].price,
                stock[1].change,
                stock[1].change_percent,
                stock[1].volume,
            ]
        ):
            return
        if stock[0] == "AAPL":
            self.AAPL = stock[1]
        elif stock[0] == "MSFT":
            self.MSFT = stock[1]
        elif stock[0] == "GOOG":
            self.GOOG = stock[1]
        elif stock[0] == "FB":
            self.FB = stock[1]
        elif stock[0] == "AMZN":
            self.AMZN = stock[1]
        elif stock[0] == "TSLA":
            self.TSLA = stock[1]
        elif stock[0] == "INTC":
            self.INTC = stock[1]
        elif stock[0] == "CSCO":
            self.CSCO = stock[1]
        elif stock[0] == "NVDA":
            self.NVDA = stock[1]
        elif stock[0] == "ORCL":
            self.ORCL = stock[1]
        elif stock[0] == "PYPL":
            self.PYPL = stock[1]
        elif stock[0] == "QCOM":
            self.QCOM = stock[1]
        elif stock[0] == "CMCSA":
            self.CMCSA = stock[1]
        elif stock[0] == "GPRO":
            self.GPRO = stock[1]
        elif stock[0] == "TWTR":
            self.TWTR = stock[1]
        elif stock[0] == "GME":
            self.GME = stock[1]
        elif stock[0] == "BTC":
            self.BTC = stock[1]
        elif stock[0] == "ETH":
            self.ETH = stock[1]
        elif stock[0] == "LTC":
            self.LTC = stock[1]
        elif stock[0] == "XRP":
            self.XRP = stock[1]
        elif stock[0] == "BCH":
            self.BCH = stock[1]
        elif stock[0] == "ADA":
            self.ADA = stock[1]
        elif stock[0] == "XMR":
            self.XMR = stock[1]
        elif stock[0] == "DASH":
            self.DASH = stock[1]
        elif stock[0] == "EOS":
            self.EOS = stock[1]

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, str | Decimal]]):
        """Initializes a StockDict object from a dict."""
        return cls(**data)

    async def export(self):
        """Exports the stock objects to a dictionary."""
        return {
            "AAPL": self.AAPL.as_dict(),
            "MSFT": self.MSFT.as_dict(),
            "GOOG": self.GOOG.as_dict(),
            "FB": self.FB.as_dict(),
            "AMZN": self.AMZN.as_dict(),
            "TSLA": self.TSLA.as_dict(),
            "INTC": self.INTC.as_dict(),
            "CSCO": self.CSCO.as_dict(),
            "NVDA": self.NVDA.as_dict(),
            "ORCL": self.ORCL.as_dict(),
            "PYPL": self.PYPL.as_dict(),
            "QCOM": self.QCOM.as_dict(),
            "CMCSA": self.CMCSA.as_dict(),
            "GPRO": self.GPRO.as_dict(),
            "TWTR": self.TWTR.as_dict(),
            "GME": self.GME.as_dict(),
            "BTC": self.BTC.as_dict(),
            "ETH": self.ETH.as_dict(),
            "LTC": self.LTC.as_dict(),
            "XRP": self.XRP.as_dict(),
            "BCH": self.BCH.as_dict(),
            "ADA": self.ADA.as_dict(),
            "XMR": self.XMR.as_dict(),
            "DASH": self.DASH.as_dict(),
            "EOS": self.EOS.as_dict(),
        }


def get_stock(symbol: str) -> tuple[str, Stock]:
    """Gets the stock data from the API."""
    data = yf.download(symbol, period="1d", interval="15m")
    return symbol, Stock(
        **{
            "name": tickers[symbol.replace("-", "_")].value,
            "price": Decimal(str(data.iloc[-2]["Close"])),
            "change": (
                Decimal(str(data.iloc[-2]["Close"]))
                - Decimal(str(data.iloc[-3]["Close"]))
            ),
            "change_percent": (
                100
                * (
                    Decimal(str(data.iloc[-2]["Close"]))
                    - Decimal(str(data.iloc[-3]["Close"]))
                )
                / Decimal(str(data.iloc[-3]["Close"]))
            ),
            "volume": Decimal(str(data.iloc[-3]["Volume"])),
        }
    )


class Stocks(app_commands.Group, commands.Cog):
    """Stocks"""

    def __init__(self, bot: CBot):
        super().__init__(name="Stocks", description="Stocks commands")
        self.bot = bot
        self.stocks: StockDict = StockDict.empty()

    async def get_stocks(self) -> dict[str, Stock]:
        """Get stocks"""
        _tasks = [
            await self.bot.loop.run_in_executor(self.bot.executor, get_stock, symbol)
            for symbol in STOCKS
        ]
        return {result[0].split("-")[0]: result[1] for result in _tasks}

    async def cog_load(self) -> None:
        """Cog load callback"""
        self.stocks = StockDict(**await self.get_stocks())
        self.update_stocks.start()

    async def cog_unload(self) -> None:
        """Cog unload callback"""
        self.update_stocks.cancel()

    @tasks.loop(time=list(fifteen_min_interval_generator()))
    async def update_stocks(self) -> None:
        """Update stocks"""
        self.stocks = StockDict(**await self.get_stocks())


async def setup(bot: CBot):
    """Setup"""
    await bot.add_cog(
        Stocks(bot), override=True, guild=discord.Object(id=225345178955808768)
    )
