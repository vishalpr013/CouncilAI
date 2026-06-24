import yfinance as yf
import pandas as pd
from typing import Dict, Any

def get_ticker_data(ticker: str) -> Dict[str, Any]:
    """Fetches key valuation metrics and info for a stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Safe extraction of key fields
        return {
            "symbol": ticker.upper(),
            "name": info.get("longName", ticker.upper()),
            "price": info.get("currentPrice", info.get("regularMarketPreviousClose", 0.0)),
            "pe_ratio": info.get("trailingPE", None),
            "peg_ratio": info.get("pegRatio", None),
            "market_cap": info.get("marketCap", 0),
            "debt_to_equity": info.get("debtToEquity", None),
            "free_cash_flow": info.get("freeCashflow", 0),
            "beta": info.get("beta", None),
            "currency": info.get("financialCurrency", "USD"),
            "website": info.get("website", ""),
            "industry": info.get("industry", ""),
            "sector": info.get("sector", ""),
            "summary": info.get("longBusinessSummary", "")
        }
    except Exception as e:
        return {"error": f"Failed to get data for {ticker}: {str(e)}"}

def get_financial_statements(ticker: str) -> Dict[str, Any]:
    """Fetches key rows from the income statement, balance sheet, and cash flow statement."""
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch statements
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # If statements are empty
        if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
            return {"error": f"Missing financial statements for {ticker} in Yahoo Finance."}
        
        # Get years as string list
        years = [str(col.year) for col in income_stmt.columns][:4]
        
        # Extract rows safely helper
        def extract_row(df, keys):
            for key in keys:
                # Case-insensitive index match
                matches = [idx for idx in df.index if key.lower() in idx.lower()]
                if matches:
                    vals = df.loc[matches[0]].tolist()
                    # Clean NaN
                    return [0.0 if pd.isna(v) else float(v) for v in vals][:4]
            return [0.0] * len(years)

        revenue = extract_row(income_stmt, ["Total Revenue", "Revenue"])
        net_income = extract_row(income_stmt, ["Net Income"])
        operating_cash = extract_row(cash_flow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        capital_expenditures = extract_row(cash_flow, ["Capital Expenditure", "Capital Expenditures"])
        
        # Calculate Free Cash Flow
        fcf = []
        for oc, capex in zip(operating_cash, capital_expenditures):
            # Capex is typically negative in yfinance, so we add it or subtract absolute value
            fcf.append(oc + capex if capex < 0 else oc - capex)

        total_assets = extract_row(balance_sheet, ["Total Assets"])
        total_debt = extract_row(balance_sheet, ["Total Debt", "Total Liabilities Net Min Interest"])
        cash_equivalents = extract_row(balance_sheet, ["Cash And Cash Equivalents", "Cash And Short Term Investments", "Cash"])

        return {
            "years": years,
            "revenue": revenue[::-1],
            "net_income": net_income[::-1],
            "operating_cash": operating_cash[::-1],
            "capital_expenditures": [abs(c) for c in capital_expenditures][::-1],
            "free_cash_flow": fcf[::-1],
            "total_assets": total_assets[::-1],
            "total_debt": total_debt[::-1],
            "cash_equivalents": cash_equivalents[::-1]
        }
    except Exception as e:
        return {"error": f"Failed to parse financial statements: {str(e)}"}

def calculate_dcf(
    ticker: str,
    revenue_growth: float = 0.10,  # 10% base
    discount_rate: float = 0.09,   # 9% base
    terminal_multiple: float = 15.0, # 15x base
    margin_of_safety: float = 0.20  # 20% margin
) -> Dict[str, Any]:
    """Computes a Discounted Cash Flow valuation based on financial statement metrics."""
    try:
        # Get key ticker details
        ticker_data = get_ticker_data(ticker)
        if "error" in ticker_data:
            return ticker_data
            
        financials = get_financial_statements(ticker)
        if "error" in financials:
            return financials

        current_price = ticker_data["price"]
        shares_outstanding = ticker_data["market_cap"] / current_price if current_price > 0 else 0
        if shares_outstanding == 0:
            return {"error": "Shares outstanding cannot be zero."}

        # Use latest FCF as the starting cash flow.
        # Fallback to operating cash flow - capex or average of last 3 years if latest is negative
        fcf_history = financials["free_cash_flow"]
        latest_fcf = fcf_history[-1] if fcf_history else 0.0
        
        # If latest FCF is negative, try average FCF or default to 5% of revenue
        if latest_fcf <= 0:
            avg_fcf = sum(fcf_history) / len(fcf_history) if fcf_history else 0
            if avg_fcf > 0:
                starting_fcf = avg_fcf
            else:
                starting_fcf = financials["revenue"][-1] * 0.08  # Assume 8% FCF margin
        else:
            starting_fcf = latest_fcf

        # Cash & Debt
        cash = financials["cash_equivalents"][-1] if financials["cash_equivalents"] else 0.0
        debt = financials["total_debt"][-1] if financials["total_debt"] else 0.0

        # Project FCF for the next 5 years
        projected_fcfs = []
        discount_factors = []
        discounted_fcfs = []

        temp_fcf = starting_fcf
        for year in range(1, 6):
            temp_fcf = temp_fcf * (1 + revenue_growth)
            projected_fcfs.append(temp_fcf)
            
            factor = (1 + discount_rate) ** year
            discount_factors.append(factor)
            
            discounted_fcf = temp_fcf / factor
            discounted_fcfs.append(discounted_fcf)

        # Terminal Value (using multiple method)
        terminal_value = projected_fcfs[-1] * terminal_multiple
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)

        # Present Value of Cash Flows
        pv_of_cf = sum(discounted_fcfs)
        enterprise_value = pv_of_cf + discounted_terminal_value
        
        # Equity Value = Enterprise Value + Cash - Debt
        equity_value = enterprise_value + cash - debt
        intrinsic_value_per_share = equity_value / shares_outstanding
        
        # Margin of safety price
        buy_price_target = intrinsic_value_per_share * (1 - margin_of_safety)

        return {
            "symbol": ticker.upper(),
            "starting_fcf": starting_fcf,
            "projected_fcfs": projected_fcfs,
            "discounted_fcfs": discounted_fcfs,
            "terminal_value": terminal_value,
            "discounted_terminal_value": discounted_terminal_value,
            "pv_of_cf": pv_of_cf,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "shares_outstanding": shares_outstanding,
            "intrinsic_value": intrinsic_value_per_share,
            "buy_price_target": buy_price_target,
            "current_price": current_price,
            "margin_of_safety": margin_of_safety,
            "valuation_status": "UNDERVALUED" if current_price < buy_price_target else "OVERVALUED" if current_price > intrinsic_value_per_share else "FAIR VALUE"
        }
    except Exception as e:
        return {"error": f"Failed in DCF calculation: {str(e)}"}
