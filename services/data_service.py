#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Service Layer for RWA Yield Optimizer GUI
Integrates existing backend with SQLite storage
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from database.models import DatabaseManager, ProtocolData, AIPrediction, PortfolioAllocation
from simple_rwa_agent import SimpleRWAAgent

class RWADataService:
    """Data service layer for GUI application"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.agent = SimpleRWAAgent()
        self.session_id = str(uuid.uuid4())
    
    async def refresh_protocol_data(self, protocol: str = None) -> Dict:
        """Refresh protocol data from APIs and save to database"""
        try:
            if protocol:
                protocols = [protocol]
            else:
                protocols = self.agent.supported_protocols
            
            results = {}
            for proto in protocols:
                try:
                    # Get data from agent
                    agent_data = await self.agent.get_protocol_data(proto)
                    
                    if agent_data:
                        # Convert to database model
                        db_data = ProtocolData(
                            protocol=proto,
                            current_apy=agent_data.current_apy,
                            risk_score=agent_data.risk_score,
                            asset_type=agent_data.asset_type,
                            tvl=agent_data.tvl,
                            active_pools=agent_data.active_pools,
                            min_investment=agent_data.min_investment,
                            lock_period=agent_data.lock_period,
                            change_1d=0.0,  # Would be from API
                            change_7d=0.0   # Would be from API
                        )
                        
                        # Save to database
                        self.db.save_protocol_data(db_data)
                        results[proto] = "success"
                    else:
                        results[proto] = "no_data"
                        
                except Exception as e:
                    results[proto] = f"error: {str(e)}"
            
            return results
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_protocol_data(self, protocol: str) -> Optional[ProtocolData]:
        """Get latest protocol data from database"""
        data_list = self.db.get_protocol_data(protocol, limit=1)
        return data_list[0] if data_list else None
    
    def get_all_protocols_data(self) -> List[ProtocolData]:
        """Get latest data for all protocols"""
        return self.db.get_all_latest_protocols()
    
    def get_protocol_history(self, protocol: str, days: int = 30) -> List[ProtocolData]:
        """Get protocol historical data"""
        return self.db.get_protocol_history(protocol, days)
    
    async def get_ai_prediction(self, protocol: str, timeframe: str = "90d") -> Dict:
        """Get AI prediction and save to database"""
        try:
            # Get prediction from agent
            prediction_text = await self.agent.get_ai_yield_prediction(protocol, timeframe)
            
            # Parse prediction (simplified - in real implementation, parse the text)
            # For now, create a mock prediction based on current data
            current_data = self.get_protocol_data(protocol)
            if current_data:
                predicted_apy = current_data.current_apy + 0.5  # Simple prediction
                confidence = 7.5
                reasoning = "AI ensemble analysis suggests moderate yield increase"
                risk_factors = json.dumps(["Market volatility", "Protocol risk", "Regulatory changes"])
                
                # Save to database
                ai_pred = AIPrediction(
                    protocol=protocol,
                    timeframe=timeframe,
                    predicted_apy=predicted_apy,
                    confidence=confidence,
                    model_name="ensemble",
                    reasoning=reasoning,
                    risk_factors=risk_factors
                )
                
                self.db.save_ai_prediction(ai_pred)
                
                return {
                    "success": True,
                    "predicted_apy": predicted_apy,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "risk_factors": json.loads(risk_factors),
                    "full_report": prediction_text
                }
            else:
                return {"success": False, "error": "No protocol data available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_ai_predictions_history(self, protocol: str, timeframe: str = None) -> List[AIPrediction]:
        """Get AI prediction history"""
        return self.db.get_ai_predictions(protocol, timeframe)
    
    async def optimize_portfolio(self, investment_amount: float, risk_tolerance: str = "medium") -> Dict:
        """Optimize portfolio and save allocations"""
        try:
            # Get optimization from agent
            optimization_text = await self.agent.optimize_portfolio(investment_amount, risk_tolerance)
            
            # Parse optimization results (simplified)
            protocols_data = self.get_all_protocols_data()
            if not protocols_data:
                return {"success": False, "error": "No protocol data available"}
            
            # Simple allocation algorithm
            total_weight = sum(p.current_apy / (1 + p.risk_score) for p in protocols_data)
            allocations = []
            
            for protocol_data in protocols_data:
                weight = (protocol_data.current_apy / (1 + protocol_data.risk_score)) / total_weight
                allocation_amount = investment_amount * weight
                
                allocation = PortfolioAllocation(
                    session_id=self.session_id,
                    protocol=protocol_data.protocol,
                    allocation_amount=allocation_amount,
                    allocation_percentage=weight * 100,
                    expected_apy=protocol_data.current_apy,
                    risk_score=protocol_data.risk_score
                )
                
                self.db.save_portfolio_allocation(allocation)
                allocations.append(allocation)
            
            # Calculate portfolio metrics
            weighted_apy = sum(a.expected_apy * a.allocation_percentage / 100 for a in allocations)
            weighted_risk = sum(a.risk_score * a.allocation_percentage / 100 for a in allocations)
            expected_return = investment_amount * weighted_apy / 100
            
            return {
                "success": True,
                "allocations": allocations,
                "portfolio_metrics": {
                    "weighted_apy": weighted_apy,
                    "weighted_risk": weighted_risk,
                    "expected_return": expected_return,
                    "sharpe_ratio": weighted_apy / (weighted_risk * 10) if weighted_risk > 0 else 0,
                    "diversification_score": min(len(allocations) * 2, 10)
                },
                "full_report": optimization_text
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_portfolio_allocations(self) -> List[PortfolioAllocation]:
        """Get current session portfolio allocations"""
        return self.db.get_portfolio_allocations(self.session_id)
    
    def save_user_setting(self, key: str, value: str):
        """Save user setting"""
        self.db.save_user_setting(key, value)
    
    def get_user_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get user setting"""
        return self.db.get_user_setting(key, default)
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary data"""
        protocols = self.get_all_protocols_data()
        
        if not protocols:
            return {
                "total_protocols": 0,
                "avg_apy": 0,
                "total_tvl": 0,
                "protocols": []
            }
        
        total_tvl = sum(p.tvl for p in protocols)
        avg_apy = sum(p.current_apy for p in protocols) / len(protocols)
        
        return {
            "total_protocols": len(protocols),
            "avg_apy": avg_apy,
            "total_tvl": total_tvl,
            "protocols": protocols,
            "last_updated": max(p.timestamp for p in protocols) if protocols else None
        }
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        self.db.cleanup_old_data(days)