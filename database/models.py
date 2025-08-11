#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Database Models for RWA Yield Optimizer
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class ProtocolData:
    """Protocol data model"""
    id: Optional[int] = None
    protocol: str = ""
    current_apy: float = 0.0
    risk_score: float = 0.0
    asset_type: str = ""
    tvl: float = 0.0
    active_pools: int = 0
    min_investment: float = 1000.0
    lock_period: str = "flexible"
    change_1d: float = 0.0
    change_7d: float = 0.0
    timestamp: str = ""

@dataclass
class AIPrediction:
    """AI prediction model"""
    id: Optional[int] = None
    protocol: str = ""
    timeframe: str = "90d"
    predicted_apy: float = 0.0
    confidence: float = 0.0
    model_name: str = ""
    reasoning: str = ""
    risk_factors: str = ""  # JSON string
    timestamp: str = ""

@dataclass
class PortfolioAllocation:
    """Portfolio allocation model"""
    id: Optional[int] = None
    session_id: str = ""
    protocol: str = ""
    allocation_amount: float = 0.0
    allocation_percentage: float = 0.0
    expected_apy: float = 0.0
    risk_score: float = 0.0
    timestamp: str = ""

class DatabaseManager:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = "data/rwa_optimizer.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Protocol data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocol_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol TEXT NOT NULL,
                    current_apy REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    asset_type TEXT NOT NULL,
                    tvl REAL NOT NULL,
                    active_pools INTEGER DEFAULT 0,
                    min_investment REAL DEFAULT 1000.0,
                    lock_period TEXT DEFAULT 'flexible',
                    change_1d REAL DEFAULT 0.0,
                    change_7d REAL DEFAULT 0.0,
                    timestamp TEXT NOT NULL,
                    UNIQUE(protocol, timestamp)
                )
            """)
            
            # AI predictions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    predicted_apy REAL NOT NULL,
                    confidence REAL NOT NULL,
                    model_name TEXT NOT NULL,
                    reasoning TEXT,
                    risk_factors TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Portfolio allocations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    allocation_amount REAL NOT NULL,
                    allocation_percentage REAL NOT NULL,
                    expected_apy REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # User settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def save_protocol_data(self, data: ProtocolData) -> int:
        """Save protocol data"""
        data.timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO protocol_data 
                (protocol, current_apy, risk_score, asset_type, tvl, active_pools, 
                 min_investment, lock_period, change_1d, change_7d, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.protocol, data.current_apy, data.risk_score, data.asset_type,
                data.tvl, data.active_pools, data.min_investment, data.lock_period,
                data.change_1d, data.change_7d, data.timestamp
            ))
            return cursor.lastrowid
    
    def get_protocol_data(self, protocol: str, limit: int = 1) -> List[ProtocolData]:
        """Get protocol data"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM protocol_data 
                WHERE protocol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (protocol, limit))
            
            rows = cursor.fetchall()
            return [ProtocolData(**dict(row)) for row in rows]
    
    def get_all_latest_protocols(self) -> List[ProtocolData]:
        """Get latest data for all protocols"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT p1.* FROM protocol_data p1
                INNER JOIN (
                    SELECT protocol, MAX(timestamp) as max_timestamp
                    FROM protocol_data
                    GROUP BY protocol
                ) p2 ON p1.protocol = p2.protocol AND p1.timestamp = p2.max_timestamp
            """)
            
            rows = cursor.fetchall()
            return [ProtocolData(**dict(row)) for row in rows]
    
    def save_ai_prediction(self, prediction: AIPrediction) -> int:
        """Save AI prediction"""
        prediction.timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO ai_predictions 
                (protocol, timeframe, predicted_apy, confidence, model_name, 
                 reasoning, risk_factors, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.protocol, prediction.timeframe, prediction.predicted_apy,
                prediction.confidence, prediction.model_name, prediction.reasoning,
                prediction.risk_factors, prediction.timestamp
            ))
            return cursor.lastrowid
    
    def get_ai_predictions(self, protocol: str, timeframe: str = None, limit: int = 10) -> List[AIPrediction]:
        """Get AI predictions"""
        query = "SELECT * FROM ai_predictions WHERE protocol = ?"
        params = [protocol]
        
        if timeframe:
            query += " AND timeframe = ?"
            params.append(timeframe)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [AIPrediction(**dict(row)) for row in rows]
    
    def save_portfolio_allocation(self, allocation: PortfolioAllocation) -> int:
        """Save portfolio allocation"""
        allocation.timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO portfolio_allocations 
                (session_id, protocol, allocation_amount, allocation_percentage, 
                 expected_apy, risk_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                allocation.session_id, allocation.protocol, allocation.allocation_amount,
                allocation.allocation_percentage, allocation.expected_apy,
                allocation.risk_score, allocation.timestamp
            ))
            return cursor.lastrowid
    
    def get_portfolio_allocations(self, session_id: str) -> List[PortfolioAllocation]:
        """Get portfolio allocations for session"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM portfolio_allocations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC
            """, (session_id,))
            
            rows = cursor.fetchall()
            return [PortfolioAllocation(**dict(row)) for row in rows]
    
    def save_user_setting(self, key: str, value: str):
        """Save user setting"""
        timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_settings 
                (setting_key, setting_value, timestamp)
                VALUES (?, ?, ?)
            """, (key, value, timestamp))
    
    def get_user_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get user setting"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT setting_value FROM user_settings 
                WHERE setting_key = ?
            """, (key,))
            
            row = cursor.fetchone()
            return row['setting_value'] if row else default
    
    def get_protocol_history(self, protocol: str, days: int = 30) -> List[ProtocolData]:
        """Get protocol historical data"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM protocol_data 
                WHERE protocol = ? 
                AND datetime(timestamp) >= datetime('now', '-{} days')
                ORDER BY timestamp ASC
            """.format(days), (protocol,))
            
            rows = cursor.fetchall()
            return [ProtocolData(**dict(row)) for row in rows]
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        with self.get_connection() as conn:
            # Keep only recent data
            conn.execute("""
                DELETE FROM protocol_data 
                WHERE datetime(timestamp) < datetime('now', '-{} days')
            """.format(days))
            
            conn.execute("""
                DELETE FROM ai_predictions 
                WHERE datetime(timestamp) < datetime('now', '-{} days')
            """.format(days))
            
            conn.execute("""
                DELETE FROM portfolio_allocations 
                WHERE datetime(timestamp) < datetime('now', '-{} days')
            """.format(days))
            
            conn.commit()