import numpy as np

def run_simulation(initial_balance, num_trades, risk_pct, rr, winrate, simulations, liquidation_pct, stop_pct):
    all_data = []
    final_balances = []
    liquidation_hits = 0
    liquidation_on_trade = []
    max_drawdowns = []
    all_trades_details = []

    threshold = initial_balance * (liquidation_pct / 100)
    fixed_risk_per_trade = initial_balance * (risk_pct / 100)

    for _ in range(int(simulations)):
        balance = initial_balance
        peak = balance
        row = [balance]
        trades = []
        liq_hit = None
        max_dd = 0

        for t in range(int(num_trades)):
            if balance <= threshold:
                balance = 0
                if liq_hit is None:
                    liquidation_hits += 1
                    liq_hit = t + 1
                    liquidation_on_trade.append(liq_hit)
                row.append(0)
                trades.append({"position_size": 0, "sl": 0, "tp": 0, "pnl": 0})
                continue

            is_win = np.random.rand() < winrate / 100

            if stop_pct == 0:
                position_size = 0
                pnl = 0
                stop_loss_dollars = 0
                take_profit_dollars = 0
            else:
                ideal_position = fixed_risk_per_trade / (stop_pct / 100)
                position_size = min(ideal_position, balance)
                stop_loss_dollars = position_size * stop_pct / 100
                take_profit_dollars = stop_loss_dollars * rr
                pnl = take_profit_dollars if is_win else -stop_loss_dollars

            balance += pnl
            peak = max(peak, balance)
            dd = (peak - balance) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
            row.append(max(balance, 0))
            trades.append({
                "position_size": position_size,
                "sl": stop_loss_dollars,
                "tp": take_profit_dollars,
                "pnl": pnl
            })

        all_data.append(row)
        all_trades_details.append(trades)
        final_balances.append(balance)
        max_drawdowns.append(max_dd)

    return (
        np.array(all_data),
        np.array(final_balances),
        liquidation_hits,
        liquidation_on_trade,
        np.array(max_drawdowns),
        all_trades_details
    )