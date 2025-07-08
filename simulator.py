import numpy as np

def run_simulation(initial_balance, num_trades, risk_pct, rr, winrate, simulations, liquidation_pct):
    all_data = []
    final_balances = []
    liquidation_hits = 0
    liquidation_on_trade = []
    max_drawdowns = []

    threshold = initial_balance * (liquidation_pct / 100)

    for _ in range(int(simulations)):
        balance = initial_balance
        peak = balance
        row = [balance]
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
                continue

            is_win = np.random.rand() < winrate / 100
            risk = balance * risk_pct / 100
            pnl = risk * rr if is_win else -risk
            balance += pnl
            peak = max(peak, balance)
            dd = (peak - balance) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)
            row.append(max(balance, 0))

        all_data.append(row)
        final_balances.append(balance)
        max_drawdowns.append(max_dd)

    return (
        np.array(all_data),
        np.array(final_balances),
        liquidation_hits,
        liquidation_on_trade,
        np.array(max_drawdowns)
    )
