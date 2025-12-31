#!/usr/bin/env python3
"""
Financial and Business Metadata Extraction Module - Ultimate Edition

Extracts comprehensive metadata from financial and business data including:
- Financial Reports (annual reports, 10-K, 10-Q, earnings statements)
- Trading Data (market data, order books, transaction logs, algorithmic trading)
- Banking Data (transaction records, account statements, payment processing)
- Insurance Data (policies, claims, actuarial data, risk assessments)
- Accounting Data (general ledger, trial balance, journal entries, tax records)
- Business Intelligence (dashboards, KPIs, analytics reports, data warehouses)
- CRM Data (customer records, sales data, marketing campaigns, lead tracking)
- ERP Data (enterprise resource planning, inventory, procurement, HR data)
- Compliance Data (regulatory filings, audit trails, risk management, SOX compliance)
- Investment Data (portfolio data, fund performance, asset allocation, derivatives)
- Cryptocurrency Data (blockchain transactions, wallet data, DeFi protocols)
- Economic Data (GDP, inflation, employment, market indicators, forecasts)

Author: MetaExtract Team
Version: 1.0.0
"""

import os
import json
import csv
import logging
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union, Tuple
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

# Library availability checks
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def extract_financial_business_metadata(filepath: str) -> Dict[str, Any]:
    """Extract comprehensive financial and business metadata"""
    
    result = {
        "available": True,
        "business_type": "unknown",
        "financial_reports": {},
        "trading_data": {},
        "banking_data": {},
        "insurance_data": {},
        "accounting_data": {},
        "business_intelligence": {},
        "crm_data": {},
        "erp_data": {},
        "compliance_data": {},
        "investment_data": {},
        "cryptocurrency_data": {},
        "economic_data": {},
        "financial_metrics": {},
        "risk_analysis": {}
    }
    
    try:
        file_ext = Path(filepath).suffix.lower()
        filename = Path(filepath).name.lower()
        
        # Financial Reports
        if any(term in filename for term in ['10k', '10q', 'annual', 'earnings', 'financial', 'report']):
            result["business_type"] = "financial_report"
            financial_result = _analyze_financial_reports(filepath, file_ext)
            if financial_result:
                result["financial_reports"].update(financial_result)
        
        # Trading Data
        elif any(term in filename for term in ['trade', 'market', 'order', 'tick', 'quote', 'price']):
            result["business_type"] = "trading_data"
            trading_result = _analyze_trading_data(filepath, file_ext)
            if trading_result:
                result["trading_data"].update(trading_result)
        
        # Banking Data
        elif any(term in filename for term in ['bank', 'transaction', 'payment', 'account', 'statement']):
            result["business_type"] = "banking_data"
            banking_result = _analyze_banking_data(filepath, file_ext)
            if banking_result:
                result["banking_data"].update(banking_result)
        
        # Insurance Data
        elif any(term in filename for term in ['insurance', 'policy', 'claim', 'actuarial', 'risk']):
            result["business_type"] = "insurance_data"
            insurance_result = _analyze_insurance_data(filepath, file_ext)
            if insurance_result:
                result["insurance_data"].update(insurance_result)
        
        # Accounting Data
        elif any(term in filename for term in ['accounting', 'ledger', 'journal', 'balance', 'tax']):
            result["business_type"] = "accounting_data"
            accounting_result = _analyze_accounting_data(filepath, file_ext)
            if accounting_result:
                result["accounting_data"].update(accounting_result)
        
        # Business Intelligence
        elif any(term in filename for term in ['dashboard', 'kpi', 'analytics', 'bi', 'report']):
            result["business_type"] = "business_intelligence"
            bi_result = _analyze_business_intelligence_data(filepath, file_ext)
            if bi_result:
                result["business_intelligence"].update(bi_result)
        
        # CRM Data
        elif any(term in filename for term in ['crm', 'customer', 'sales', 'lead', 'contact']):
            result["business_type"] = "crm_data"
            crm_result = _analyze_crm_data(filepath, file_ext)
            if crm_result:
                result["crm_data"].update(crm_result)
        
        # ERP Data
        elif any(term in filename for term in ['erp', 'inventory', 'procurement', 'hr', 'payroll']):
            result["business_type"] = "erp_data"
            erp_result = _analyze_erp_data(filepath, file_ext)
            if erp_result:
                result["erp_data"].update(erp_result)
        
        # Compliance Data
        elif any(term in filename for term in ['compliance', 'audit', 'regulatory', 'sox', 'gdpr']):
            result["business_type"] = "compliance_data"
            compliance_result = _analyze_compliance_data(filepath, file_ext)
            if compliance_result:
                result["compliance_data"].update(compliance_result)
        
        # Investment Data
        elif any(term in filename for term in ['portfolio', 'investment', 'fund', 'asset', 'derivative']):
            result["business_type"] = "investment_data"
            investment_result = _analyze_investment_data(filepath, file_ext)
            if investment_result:
                result["investment_data"].update(investment_result)
        
        # Cryptocurrency Data
        elif any(term in filename for term in ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'wallet']):
            result["business_type"] = "cryptocurrency_data"
            crypto_result = _analyze_cryptocurrency_data(filepath, file_ext)
            if crypto_result:
                result["cryptocurrency_data"].update(crypto_result)
        
        # Economic Data
        elif any(term in filename for term in ['economic', 'gdp', 'inflation', 'employment', 'forecast']):
            result["business_type"] = "economic_data"
            economic_result = _analyze_economic_data(filepath, file_ext)
            if economic_result:
                result["economic_data"].update(economic_result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in financial business analysis: {e}")
        return {"available": False, "error": str(e)}

def _analyze_financial_reports(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze financial reports and statements"""
    try:
        result = {
            "report_analysis": {
                "report_type": "unknown",
                "period_info": {},
                "financial_statements": {},
                "key_metrics": {},
                "company_info": {},
                "regulatory_info": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect report type
        if '10k' in filename:
            result["report_analysis"]["report_type"] = "10-K Annual Report"
        elif '10q' in filename:
            result["report_analysis"]["report_type"] = "10-Q Quarterly Report"
        elif 'earnings' in filename:
            result["report_analysis"]["report_type"] = "Earnings Report"
        elif 'annual' in filename:
            result["report_analysis"]["report_type"] = "Annual Report"
        
        # For CSV financial data
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Look for financial statement indicators
            financial_indicators = {
                'income_statement': ['revenue', 'income', 'profit', 'loss', 'expense', 'ebitda'],
                'balance_sheet': ['assets', 'liabilities', 'equity', 'cash', 'debt', 'inventory'],
                'cash_flow': ['cash_flow', 'operating', 'investing', 'financing', 'capex']
            }
            
            detected_statements = []
            for statement_type, indicators in financial_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_statements.append(statement_type)
                        break
            
            result["report_analysis"]["financial_statements"]["detected_types"] = list(set(detected_statements))
            
            # Extract key financial metrics
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                # Look for key financial ratios and metrics
                key_metrics = {}
                for col in numeric_cols.columns:
                    col_lower = col.lower()
                    if any(metric in col_lower for metric in ['ratio', 'margin', 'return', 'yield']):
                        key_metrics[col] = {
                            "mean": float(numeric_cols[col].mean()),
                            "latest": float(numeric_cols[col].iloc[-1]) if len(numeric_cols[col]) > 0 else None
                        }
                
                result["report_analysis"]["key_metrics"] = key_metrics
        
        return result
        
    except Exception as e:
        logger.error(f"Financial reports analysis error: {e}")
        return {}

def _analyze_trading_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze trading and market data"""
    try:
        result = {
            "trading_analysis": {
                "data_type": "unknown",
                "market_info": {},
                "trading_metrics": {},
                "price_data": {},
                "volume_analysis": {},
                "volatility_metrics": {},
                "order_book_data": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=50000)  # Larger sample for trading data
            
            # Detect trading data type
            trading_indicators = {
                'price_data': ['price', 'open', 'high', 'low', 'close', 'ohlc'],
                'volume_data': ['volume', 'shares', 'quantity', 'size'],
                'order_data': ['bid', 'ask', 'order', 'trade'],
                'tick_data': ['tick', 'timestamp', 'millisecond']
            }
            
            detected_types = []
            for data_type, indicators in trading_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_types.append(data_type)
                        break
            
            result["trading_analysis"]["data_type"] = detected_types
            
            # Price analysis
            price_columns = [col for col in df.columns if any(price_term in col.lower() 
                           for price_term in ['price', 'close', 'last'])]
            
            if price_columns:
                price_col = price_columns[0]  # Use first price column
                price_data = df[price_col].dropna()
                
                if len(price_data) > 1:
                    result["trading_analysis"]["price_data"] = {
                        "min_price": float(price_data.min()),
                        "max_price": float(price_data.max()),
                        "mean_price": float(price_data.mean()),
                        "price_range": float(price_data.max() - price_data.min()),
                        "price_change": float(price_data.iloc[-1] - price_data.iloc[0]) if len(price_data) > 1 else 0
                    }
                    
                    # Calculate volatility (standard deviation of returns)
                    if len(price_data) > 2:
                        returns = price_data.pct_change().dropna()
                        result["trading_analysis"]["volatility_metrics"] = {
                            "daily_volatility": float(returns.std()),
                            "annualized_volatility": float(returns.std() * np.sqrt(252)),  # Assuming daily data
                            "max_daily_return": float(returns.max()),
                            "min_daily_return": float(returns.min())
                        }
            
            # Volume analysis
            volume_columns = [col for col in df.columns if 'volume' in col.lower()]
            if volume_columns:
                volume_col = volume_columns[0]
                volume_data = df[volume_col].dropna()
                
                if len(volume_data) > 0:
                    result["trading_analysis"]["volume_analysis"] = {
                        "total_volume": float(volume_data.sum()),
                        "average_volume": float(volume_data.mean()),
                        "max_volume": float(volume_data.max()),
                        "volume_std": float(volume_data.std())
                    }
            
            # Time analysis
            time_columns = [col for col in df.columns if any(time_term in col.lower() 
                           for time_term in ['time', 'timestamp', 'date'])]
            
            if time_columns:
                result["trading_analysis"]["market_info"]["has_timestamps"] = True
                result["trading_analysis"]["market_info"]["data_points"] = len(df)
                
                # Try to determine market session
                if len(df) > 100:
                    # Estimate if this is high-frequency data
                    data_frequency = "high_frequency" if len(df) > 10000 else "low_frequency"
                    result["trading_analysis"]["market_info"]["frequency"] = data_frequency
        
        return result
        
    except Exception as e:
        logger.error(f"Trading data analysis error: {e}")
        return {}

def _analyze_banking_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze banking and transaction data"""
    try:
        result = {
            "banking_analysis": {
                "data_type": "unknown",
                "transaction_info": {},
                "account_info": {},
                "payment_methods": {},
                "fraud_indicators": {},
                "compliance_info": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Detect banking data type
            banking_indicators = {
                'transactions': ['transaction', 'amount', 'debit', 'credit', 'balance'],
                'accounts': ['account', 'customer', 'holder', 'number'],
                'payments': ['payment', 'transfer', 'wire', 'ach', 'card'],
                'statements': ['statement', 'period', 'beginning', 'ending']
            }
            
            detected_types = []
            for data_type, indicators in banking_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_types.append(data_type)
                        break
            
            result["banking_analysis"]["data_type"] = detected_types
            
            # Transaction analysis
            amount_columns = [col for col in df.columns if any(amount_term in col.lower() 
                             for amount_term in ['amount', 'value', 'sum', 'total'])]
            
            if amount_columns:
                amount_col = amount_columns[0]
                amounts = df[amount_col].dropna()
                
                if len(amounts) > 0:
                    result["banking_analysis"]["transaction_info"] = {
                        "total_transactions": len(amounts),
                        "total_amount": float(amounts.sum()),
                        "average_amount": float(amounts.mean()),
                        "max_transaction": float(amounts.max()),
                        "min_transaction": float(amounts.min()),
                        "large_transactions": int(len(amounts[amounts > amounts.quantile(0.95)]))
                    }
                    
                    # Fraud indicators (simple heuristics)
                    fraud_indicators = {}
                    
                    # Unusually large transactions
                    threshold = amounts.mean() + 3 * amounts.std()
                    outliers = amounts[amounts > threshold]
                    fraud_indicators["outlier_transactions"] = len(outliers)
                    
                    # Round number bias (potential synthetic data)
                    round_amounts = amounts[amounts % 100 == 0]
                    fraud_indicators["round_number_ratio"] = len(round_amounts) / len(amounts)
                    
                    result["banking_analysis"]["fraud_indicators"] = fraud_indicators
            
            # Payment method analysis
            method_columns = [col for col in df.columns if any(method_term in col.lower() 
                             for method_term in ['method', 'type', 'channel', 'mode'])]
            
            if method_columns:
                method_col = method_columns[0]
                method_counts = df[method_col].value_counts().to_dict()
                result["banking_analysis"]["payment_methods"] = method_counts
        
        return result
        
    except Exception as e:
        logger.error(f"Banking data analysis error: {e}")
        return {}

def _analyze_cryptocurrency_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze cryptocurrency and blockchain data"""
    try:
        result = {
            "crypto_analysis": {
                "data_type": "unknown",
                "blockchain_info": {},
                "transaction_data": {},
                "wallet_analysis": {},
                "defi_data": {},
                "token_metrics": {},
                "network_stats": {}
            }
        }
        
        filename = Path(filepath).name.lower()
        
        # Detect cryptocurrency data type
        if any(term in filename for term in ['bitcoin', 'btc']):
            result["crypto_analysis"]["blockchain_info"]["network"] = "Bitcoin"
        elif any(term in filename for term in ['ethereum', 'eth']):
            result["crypto_analysis"]["blockchain_info"]["network"] = "Ethereum"
        elif any(term in filename for term in ['defi', 'uniswap', 'compound']):
            result["crypto_analysis"]["data_type"] = "defi"
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Look for blockchain transaction indicators
            crypto_indicators = {
                'transactions': ['hash', 'txid', 'transaction', 'block'],
                'addresses': ['address', 'from', 'to', 'sender', 'receiver'],
                'amounts': ['value', 'amount', 'wei', 'satoshi'],
                'fees': ['fee', 'gas', 'gwei'],
                'tokens': ['token', 'contract', 'erc20', 'nft']
            }
            
            detected_types = []
            for data_type, indicators in crypto_indicators.items():
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        detected_types.append(data_type)
                        break
            
            result["crypto_analysis"]["data_type"] = detected_types
            
            # Transaction analysis
            if 'transactions' in detected_types:
                tx_count = len(df)
                result["crypto_analysis"]["transaction_data"] = {
                    "total_transactions": tx_count,
                    "unique_addresses": 0,
                    "transaction_frequency": "unknown"
                }
                
                # Count unique addresses
                address_columns = [col for col in df.columns if any(addr_term in col.lower() 
                                  for addr_term in ['address', 'from', 'to'])]
                
                if address_columns:
                    unique_addresses = set()
                    for col in address_columns:
                        unique_addresses.update(df[col].dropna().unique())
                    result["crypto_analysis"]["transaction_data"]["unique_addresses"] = len(unique_addresses)
            
            # Value analysis
            value_columns = [col for col in df.columns if any(value_term in col.lower() 
                            for value_term in ['value', 'amount', 'price'])]
            
            if value_columns:
                value_col = value_columns[0]
                values = pd.to_numeric(df[value_col], errors='coerce').dropna()
                
                if len(values) > 0:
                    result["crypto_analysis"]["token_metrics"] = {
                        "total_value": float(values.sum()),
                        "average_value": float(values.mean()),
                        "max_value": float(values.max()),
                        "value_distribution": {
                            "median": float(values.median()),
                            "q75": float(values.quantile(0.75)),
                            "q95": float(values.quantile(0.95))
                        }
                    }
        
        return result
        
    except Exception as e:
        logger.error(f"Cryptocurrency analysis error: {e}")
        return {}

def _analyze_business_intelligence_data(filepath: str, file_ext: str) -> Dict[str, Any]:
    """Analyze business intelligence and analytics data"""
    try:
        result = {
            "bi_analysis": {
                "report_type": "unknown",
                "kpi_metrics": {},
                "data_dimensions": {},
                "time_analysis": {},
                "performance_indicators": {},
                "dashboard_elements": {}
            }
        }
        
        if file_ext == '.csv' and PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, nrows=10000)
            
            # Detect KPI and metric columns
            kpi_indicators = {
                'revenue': ['revenue', 'sales', 'income', 'earnings'],
                'costs': ['cost', 'expense', 'expenditure', 'spend'],
                'customers': ['customer', 'client', 'user', 'subscriber'],
                'conversion': ['conversion', 'rate', 'percentage', 'ratio'],
                'growth': ['growth', 'increase', 'change', 'trend'],
                'efficiency': ['efficiency', 'productivity', 'utilization', 'performance']
            }
            
            detected_kpis = {}
            for kpi_type, indicators in kpi_indicators.items():
                matching_columns = []
                for col in df.columns:
                    if any(indicator in col.lower() for indicator in indicators):
                        matching_columns.append(col)
                
                if matching_columns:
                    detected_kpis[kpi_type] = matching_columns
            
            result["bi_analysis"]["kpi_metrics"] = detected_kpis
            
            # Time dimension analysis
            time_columns = [col for col in df.columns if any(time_term in col.lower() 
                           for time_term in ['date', 'time', 'period', 'month', 'quarter', 'year'])]
            
            if time_columns:
                result["bi_analysis"]["time_analysis"] = {
                    "has_time_dimension": True,
                    "time_columns": time_columns,
                    "data_points": len(df),
                    "time_granularity": "unknown"
                }
                
                # Try to determine time granularity
                if len(df) > 1:
                    if 'daily' in str(time_columns).lower() or len(df) > 300:
                        result["bi_analysis"]["time_analysis"]["time_granularity"] = "daily"
                    elif 'monthly' in str(time_columns).lower() or len(df) < 50:
                        result["bi_analysis"]["time_analysis"]["time_granularity"] = "monthly"
                    else:
                        result["bi_analysis"]["time_analysis"]["time_granularity"] = "weekly"
            
            # Performance indicators calculation
            numeric_cols = df.select_dtypes(include=[np.number])
            if not numeric_cols.empty:
                performance_metrics = {}
                
                for col in numeric_cols.columns:
                    col_data = numeric_cols[col].dropna()
                    if len(col_data) > 1:
                        # Calculate trend (simple linear trend)
                        x = np.arange(len(col_data))
                        trend = np.polyfit(x, col_data, 1)[0]  # Slope of linear fit
                        
                        performance_metrics[col] = {
                            "current_value": float(col_data.iloc[-1]),
                            "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                            "volatility": float(col_data.std() / col_data.mean()) if col_data.mean() != 0 else 0
                        }
                
                result["bi_analysis"]["performance_indicators"] = performance_metrics
        
        return result
        
    except Exception as e:
        logger.error(f"Business intelligence analysis error: {e}")
        return {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = extract_financial_business_metadata(sys.argv[1])
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python financial_business_ultimate.py <business_file>")