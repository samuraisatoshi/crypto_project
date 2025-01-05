# app/utils/binance_client.py
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException
import os
from datetime import datetime
import pandas as pd

class BinanceClient:
    def __init__(self):
        trading_env = os.getenv('TRADING_ENV', 'TEST').upper()
        if trading_env == 'TEST':
            self.api_key = os.getenv('BINANCE_TESTNET_API_KEY')
            self.api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            self.client.API_URL = 'https://testnet.binance.vision/api'
        else:
            self.api_key = os.getenv('BINANCE_API_KEY')
            self.api_secret = os.getenv('BINANCE_API_SECRET')
            self.client = Client(self.api_key, self.api_secret)
        
        # Opcional: Configurar conexões websocket se necessário
        # self.twm = ThreadedWebsocketManager(api_key=self.api_key, api_secret=self.api_secret)
        # self.dcm = ThreadedDepthCacheManager(api_key=self.api_key, api_secret=self.api_secret)

    def get_order_book(self, symbol='BNBBTC'):
        """
        Obtém a profundidade do mercado para um símbolo específico.
        """
        try:
            depth = self.client.get_order_book(symbol=symbol)
            return depth
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao obter ordem de livro: {e}")
            return None
        except Exception as e:
            print(f"Erro ao obter ordem de livro: {e}")
            return None

    def create_test_order(self, symbol='BNBBTC', side=Client.SIDE_BUY, order_type=Client.ORDER_TYPE_MARKET, quantity=100):
        """
        Cria uma ordem de teste.
        """
        try:
            order = self.client.create_test_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
            return order
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao criar ordem de teste: {e}")
            return None
        except Exception as e:
            print(f"Erro ao criar ordem de teste: {e}")
            return None

    def get_all_tickers(self):
        """
        Obtém todos os preços dos símbolos disponíveis.
        """
        try:
            prices = self.client.get_all_tickers()
            return prices
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao obter todos os tickers: {e}")
            return []
        except Exception as e:
            print(f"Erro ao obter todos os tickers: {e}")
            return []

    def withdraw(self, asset='ETH', address='', amount=100):
        """
        Realiza uma retirada (withdraw) para um ativo específico.
        """
        try:
            result = self.client.withdraw(
                asset=asset,
                address=address,
                amount=amount
            )
            return result
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao realizar retirada: {e}")
            return None
        except Exception as e:
            print(f"Erro ao realizar retirada: {e}")
            return None

    def get_withdraw_history(self, coin=''):
        """
        Obtém o histórico de retiradas, opcionalmente filtrado por moeda.
        """
        try:
            withdraws = self.client.get_withdraw_history(coin=coin) if coin else self.client.get_withdraw_history()
            return withdraws
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao obter histórico de retiradas: {e}")
            return []
        except Exception as e:
            print(f"Erro ao obter histórico de retiradas: {e}")
            return []

    def get_deposit_address(self, coin='BTC'):
        """
        Obtém o endereço de depósito para uma moeda específica.
        """
        try:
            address = self.client.get_deposit_address(coin=coin)
            return address
        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao obter endereço de depósito: {e}")
            return None
        except Exception as e:
            print(f"Erro ao obter endereço de depósito: {e}")
            return None

    def get_historical_klines(self, symbol, interval, start_date, end_date=None):
        """
        Baixa dados históricos de klines (candlesticks) da Binance.

        :param symbol: Par de negociação, ex: 'BTCUSDT'
        :param interval: Timeframe, ex: '15m', '1h'
        :param start_date: Data de início no formato 'YYYY-MM-DD'
        :param end_date: Data de fim no formato 'YYYY-MM-DD' (opcional)
        :return: DataFrame com os dados históricos
        """
        try:
            klines = self.client.get_historical_klines(symbol, interval, start_date, end_date)
            if not klines:
                return pd.DataFrame()

            # Converter para DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Converter timestamp para datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            # Selecionar colunas relevantes
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

            # Converter para tipos numéricos
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

            return df

        except BinanceAPIException as e:
            print(f"Erro na API da Binance ao baixar klines: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao baixar klines: {e}")
            return pd.DataFrame()

    # Adicionar mais métodos conforme necessário, seguindo o exemplo fornecido
