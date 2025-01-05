import os
import pandas as pd
import numpy as np
from .indicators import *
from .patterns import *
from .market_regime import *
from .candles import *
from .temporal import *

from .volatility_metrics import add_volatility_metrics
from .liquidity_metrics import add_liquidity_metrics
from .trade_labeling import identify_perfect_trades, analyze_perfect_trades
from .market_value import add_market_value_metrics

from .portfolio import calculate_portfolio_metrics

def optimize_dataframe(df):
    # Converter tipos de dados para reduzir uso de memória
    float_columns = df.select_dtypes(include=['float64']).columns
    df[float_columns] = df[float_columns].astype('float32')
    
    # Converter colunas binárias para uint8
    binary_columns = ['body_bullish', 'body_bearish', 'fvg_active']
    df[binary_columns] = df[binary_columns].astype('uint8')
    
    return df

def validate_dataset(df):
    # Verificar valores extremos
    def check_outliers(column):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return df[column].between(lower_bound, upper_bound).all()
    
    # Validar principais features
    price_columns = ['open', 'high', 'low', 'close']
    for col in price_columns:
        if not check_outliers(col):
            LoggingHelper.warning(f"Possíveis outliers encontrados em {col}")
    
    # Verificar consistência dos dados
    if not (df['high'] >= df['low']).all():
        raise ValueError("Inconsistência: high < low")
    
    if not ((df['high'] >= df['open']) & (df['high'] >= df['close'])).all():
        raise ValueError("Inconsistência: high não é o maior valor")
def prepare_enriched_dataset(df, config_params, tradeReportPath, tradeReportFileName):
    """
    Pipeline de enriquecimento do dataset
    
    Args:
        df (pd.DataFrame): DataFrame com dados brutos
        config_params (dict): Dicionário com parâmetros de configuração
            - timeframe: string com o timeframe atual
            - trade_type: tipo de operação
            - patterns_validity_window: janela de validade para padrões
            - fvg_validity_window: janela de validade para FVG
    """
    try:
        LoggingHelper.info("Iniciando pipeline de enriquecimento...")

        # 1. Features básicas de preço
        df = add_percentage_price_change(df, periods=5)
        LoggingHelper.debug("Features básicas de preço adicionadas")

        # 2. Análise de velas
        df = add_body_context(df)
        LoggingHelper.debug("Análise de velas adicionada")

        # 3. Indicadores técnicos básicos
        df = add_indicators_and_oscillators(df)
        LoggingHelper.debug("Indicadores técnicos básicos adicionados")

        # 4. Cruzamentos e tendências (cria a coluna 'trend')
        df = add_cross_and_trend_signals(df)
        LoggingHelper.debug("Cruzamentos e tendências calculados")

        # 5. Indicadores avançados (inclui ATR e normalized_atr)
        df = add_advanced_indicators(df)
        LoggingHelper.debug("Indicadores avançados adicionados")

        # 6. Adiciona métricas de valor de mercado
        add_market_value_metrics(df)
        LoggingHelper.debug("MVRV, Value Momentum, Value Oscilator adicionados")

        # 7. Adicionar novas métricas de volatilidade
        df = add_volatility_metrics(df)
        LoggingHelper.debug("Métricas de volatilidade adicionadas")
        
        # 8. Adicionar novas métricas de liquidez
        df = add_liquidity_metrics(df)
        LoggingHelper.debug("Métricas de liquidez adicionadas")

        # 9. Regime de mercado (agora todas as dependências existem)
        df = add_market_regime(df)
        LoggingHelper.debug("Regime de mercado calculado")

        # 10. Padrões gráficos
        df = identify_patterns_and_confirm(
            df, 
            config_params['timeframe'],
            config_params['trade_type'],
            config_params['patterns_validity_window']
        )
        LoggingHelper.debug("Padrões gráficos identificados")

        # 11. Fair Value Gaps
        df = identify_fvg(df, config_params['fvg_validity_window'])
        LoggingHelper.debug("Fair Value Gaps identificados")

        # 12. Price Action Features
        df = add_price_action_features(df)
        LoggingHelper.debug("Features de Price Action adicionadas")

        # 13. Features temporais
        df = add_temporal_features(df)
        LoggingHelper.debug("Features temporais adicionadas")

        # 14. Identificar trades perfeitos
        df = identify_perfect_trades(
            df,
            timeframe=config_params['timeframe'],
            min_rr_ratio=2.5,
            max_open_positions=4
        )
        
        # 15. Adicionar métricas de trades
        df['trade_opportunity'] = (df['perfect_long_entry'] | df['perfect_short_entry']).astype(int)
        df['trade_direction'] = np.where(
            df['perfect_long_entry'] == 1, 1,
            np.where(df['perfect_short_entry'] == 1, -1, 0)
        )
        
        LoggingHelper.info("\nTrades perfeitos identificados:")
        LoggingHelper.info(f"Trades encontrados: {df['trade_opportunity'].sum()}")
        LoggingHelper.info(f"  - Longs: {df['perfect_long_entry'].sum()}")
        LoggingHelper.info(f"  - Shorts: {df['perfect_short_entry'].sum()}")
        LoggingHelper.info(f"Holding period médio: {df[df['holding_periods'] > 0]['holding_periods'].mean():.1f} períodos")
        
        # 16. Analisar estatísticas dos trades
        trade_stats = analyze_perfect_trades(df)
        
        # 17. Calcular métricas de portfólio
        portfolio_results = calculate_portfolio_metrics(
            df, 
            initial_balance=1000,
            position_size_pct=0.1
        )
        
        # 18. Consolidar resultados
        results = {
            'trade_stats': trade_stats,
            'portfolio_metrics': portfolio_results
        }

        # Salvar relatório de trades
        report_file = os.path.join(tradeReportPath, tradeReportFileName)
        with open(report_file, 'w') as f:
            f.write(str(results))
            
        LoggingHelper.info(f"\nRelatório de trades salvo em: {report_file}")

        # 19. Limpeza de colunas intermediárias
        columns_to_drop = [
            'ema_8', 'ema_21', 'ema_50', 'ema_100', 'ema_200',
            'fed_rate_date',
            'direction',
            'bb_middle'   
        ]
        df = df.drop(columns=columns_to_drop, errors='ignore')
        LoggingHelper.debug("Colunas intermediárias removidas")

        # 20. Tratamento de valores ausentes
        LoggingHelper.debug(f"Valores ausentes antes da limpeza:\n{df.isna().sum()}")
        df = df.dropna()
        LoggingHelper.info(f"Registros restantes após remoção de NA: {len(df)}")

        # 21. Otimização do DataFrame
        df = optimize_dataframe(df)
        LoggingHelper.debug("DataFrame otimizado")

        # 22. Validação final dos dados
        validate_dataset(df)
        LoggingHelper.info("Validação final concluída")

        return df

    except Exception as e:
        LoggingHelper.error(f"\nFalha no processamento: {str(e)}")
        LoggingHelper.error("\nEstado do DataFrame no momento do erro:")
        LoggingHelper.error("Colunas disponíveis:", df.columns.tolist())
        raise
    
def save_dataset_report(df, output_path, file_name):
    """
    Salva relatório detalhado sobre o dataset
    """
    
    report = {
        "dimensões": df.shape,
        "colunas": df.columns.tolist(),
        "tipos_dados": df.dtypes.to_dict(),
        "memória_uso": df.memory_usage().to_dict(),
        "estatísticas_básicas": df.describe().to_dict(),
        "valores_únicos": {col: df[col].nunique() for col in df.columns},
        "timestamp_range": {
            "início": df['timestamp'].min(),
            "fim": df['timestamp'].max()
        }
    }
    
    report_file = os.path.join(output_path, file_name)
    with open(report_file, 'w') as f:
        for key, value in report.items():
            f.write(f"\n{key.upper()}:\n")
            f.write(f"{value}\n")
            f.write("-" * 80 + "\n")
    
    LoggingHelper.info(f"\nRelatório do dataset salvo em: {report_file}")
    return report
