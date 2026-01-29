import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Use Exponential Moving Average for smoother RSI (wilder's smoothing) is often preferred but simple rolling mean is also common.
    # Standard formula often uses RMA (Rolling Moving Average) or SMMA.
    # Let's use the standard Wilder's smoothing method for accuracy.
    delta = data['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window - 1, adjust=False).mean()
    ema_down = down.ewm(com=window - 1, adjust=False).mean()
    rs = ema_up / ema_down
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def implement_strategy(data, rsi_lower=30, rsi_upper=70):
    """
    Buy when RSI crosses above lower threshold (oversold).
    Sell when RSI crosses below upper threshold (overbought).
    """
    buy_price = []
    sell_price = []
    rsi_signal = []
    signal = 0

    # We need to iterate to simulate the trade logic
    # 0 = Hold/None, 1 = Buy, -1 = Sell
    
    # A simple vectorization approach:
    # 1. Buy signal: RSI < lower (Buying the dip) - often people wait for it to cross back UP over 30 to confirm reversal.
    # Let's do the "Cross back up" logic for Buy and "Cross back down" for Sell to avoid catching a falling knife.
    
    # Strategy:
    # Buy if RSI(t-1) < 30 and RSI(t) > 30
    # Sell if RSI(t-1) > 70 and RSI(t) < 70
    
    # However, standard request usually implies simple condition. Let's stick to the crossing logic for better robustness.
    
    for i in range(len(data)):
        if i == 0:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            continue
            
        # Current and previous RSI
        current_rsi = data['RSI'].iloc[i]
        prev_rsi = data['RSI'].iloc[i-1]
        current_price = data['Close'].iloc[i]
        
        if prev_rsi < rsi_lower and current_rsi > rsi_lower:
            if signal != 1: # If not already holding
                buy_price.append(current_price)
                sell_price.append(np.nan)
                signal = 1
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
        elif prev_rsi > rsi_upper and current_rsi < rsi_upper:
            if signal == 1: # If holding, sell
                buy_price.append(np.nan)
                sell_price.append(current_price)
                signal = 0
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            
    return buy_price, sell_price

def run_backtest(ticker_symbol, start_date, end_date):
    print(f"Downloading data for {ticker_symbol}...")
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    
    if len(data) == 0:
        print("No data found.")
        return

    print("Calculating RSI...")
    data = calculate_rsi(data)
    
    print("Implementing Strategy...")
    data['Buy_Signal_Price'], data['Sell_Signal_Price'] = implement_strategy(data)
    
    # Plotting
    plt.figure(figsize=(14, 8))
    
    # Top plot: Price and Signals
    ax1 = plt.subplot2grid((10, 1), (0, 0), rowspan=5, colspan=1)
    ax1.plot(data['Close'], label=f'{ticker_symbol} Close Price', color='skyblue', linewidth=2)
    ax1.plot(data.index, data['Buy_Signal_Price'], marker='^', color='green', markersize=10, label='BUY SIGNAL', linestyle='None')
    ax1.plot(data.index, data['Sell_Signal_Price'], marker='v', color='red', markersize=10, label='SELL SIGNAL', linestyle='None')
    ax1.set_title(f'{ticker_symbol} RSI Trading Signals')
    ax1.legend()
    
    # Bottom plot: RSI
    ax2 = plt.subplot2grid((10, 1), (6, 0), rowspan=4, colspan=1)
    ax2.plot(data['RSI'], color='orange', linewidth=2)
    ax2.axhline(70, linestyle='--', alpha=0.5, color='red')
    ax2.axhline(30, linestyle='--', alpha=0.5, color='green')
    ax2.set_title('Relative Strength Index')
    ax2.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('rsi_strategy.png')
    print("Strategy chart saved to rsi_strategy.png")

if __name__ == "__main__":
    # Example usage
    ticker = 'AAPL' # Apple Inc.
    start = '2023-01-01'
    end = '2024-01-01'
    
    run_backtest(ticker, start, end)
