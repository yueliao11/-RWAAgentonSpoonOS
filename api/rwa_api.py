"""
RWA Yield Optimizer API - FastAPI服务端点
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
import logging
import os

from spoon_ai.agents import RWAYieldAgent, PortfolioOptimizerAgent
from spoon_ai.chat import ChatBot
from spoon_ai.services.rwa_data_aggregator import RWADataAggregator
from spoon_ai.tools import (
    RWAProtocolDataTool,
    YieldStandardizationTool,
    RWAPortfolioAnalysisTool,
    ToolManager
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RWA Yield Optimizer API",
    description="API for analyzing and optimizing RWA yields across DeFi protocols",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局对象
data_aggregator = RWADataAggregator()

# Pydantic模型定义
class YieldAnalysisRequest(BaseModel):
    """收益分析请求"""
    protocols: List[str] = Field(..., description="要分析的协议列表")
    asset_types: Optional[List[str]] = Field(None, description="资产类型过滤")
    timeframe: str = Field("30d", description="时间范围")
    include_forecast: bool = Field(False, description="是否包含预测")

class PortfolioOptimizationRequest(BaseModel):
    """投资组合优化请求"""
    investment_amount: float = Field(..., gt=0, description="投资金额")
    risk_tolerance: str = Field(..., regex="^(low|medium|high)$", description="风险承受度")
    target_protocols: Optional[List[str]] = Field(None, description="目标协议")
    constraints: Optional[Dict[str, Any]] = Field(None, description="投资约束")
    optimization_goal: str = Field("balanced", regex="^(max_yield|min_risk|balanced)$")

class CompareYieldsRequest(BaseModel):
    """收益率比较请求"""
    protocols: List[str] = Field(..., min_items=2, description="要比较的协议")
    asset_type: Optional[str] = Field(None, description="资产类型")
    metrics: List[str] = Field(["apy", "risk", "liquidity"], description="比较指标")

class YieldForecastRequest(BaseModel):
    """收益预测请求"""
    protocol: str = Field(..., description="协议名称")
    asset_type: str = Field(..., description="资产类型")
    forecast_period: str = Field("90d", description="预测期限")
    include_scenarios: bool = Field(True, description="是否包含情景分析")

# 依赖注入
async def get_yield_agent() -> RWAYieldAgent:
    """获取收益分析Agent实例"""
    agent = RWAYieldAgent(
        llm=ChatBot(llm_provider="openai"),
        available_tools=ToolManager([
            RWAProtocolDataTool(),
            YieldStandardizationTool(),
            RWAPortfolioAnalysisTool()
        ])
    )
    return agent

async def get_portfolio_agent() -> PortfolioOptimizerAgent:
    """获取投资组合优化Agent实例"""
    agent = PortfolioOptimizerAgent(llm=ChatBot(llm_provider="openai"))
    await agent.initialize()
    return agent

# API端点
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "RWA Yield Optimizer API",
        "version": "1.0.0",
        "endpoints": {
            "yields": "/api/v1/yields",
            "portfolio": "/api/v1/portfolio",
            "protocols": "/api/v1/protocols",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/protocols")
async def list_protocols():
    """获取支持的协议列表"""
    return {
        "protocols": [
            {
                "id": "centrifuge",
                "name": "Centrifuge",
                "description": "Real-world asset tokenization platform",
                "asset_types": ["real_estate", "invoices", "carbon_credits"]
            },
            {
                "id": "goldfinch",
                "name": "Goldfinch",
                "description": "Decentralized credit protocol",
                "asset_types": ["private_credit"]
            },
            {
                "id": "maple",
                "name": "Maple Finance",
                "description": "Institutional capital marketplace",
                "asset_types": ["private_credit", "bonds"]
            },
            {
                "id": "credix",
                "name": "Credix",
                "description": "Credit ecosystem for emerging markets",
                "asset_types": ["private_credit", "invoices"]
            }
        ]
    }

@app.post("/api/v1/yields/analyze")
async def analyze_yields(
    request: YieldAnalysisRequest,
    agent: RWAYieldAgent = Depends(get_yield_agent)
):
    """分析RWA收益率"""
    try:
        # 获取聚合数据
        protocol_data = await data_aggregator.fetch_all_yields()
        
        # 过滤请求的协议
        filtered_data = {
            p: data for p, data in protocol_data.items() 
            if p in request.protocols
        }
        
        # 使用Agent进行深度分析
        analysis_result = await agent.compare_yields(
            protocols=request.protocols,
            asset_type=request.asset_types[0] if request.asset_types else None
        )
        
        # 组合响应
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "protocols_analyzed": len(filtered_data),
            "timeframe": request.timeframe,
            "data": {
                protocol: {
                    "current_apy": data.apy,
                    "tvl": data.tvl,
                    "risk_score": data.risk_score,
                    "pools": data.pools
                } for protocol, data in filtered_data.items()
            },
            "analysis": analysis_result
        }
        
        # 添加预测（如果请求）
        if request.include_forecast:
            forecast_tasks = []
            for protocol in request.protocols[:3]:  # 限制预测数量
                forecast_tasks.append(
                    agent.forecast_yields(
                        protocol=protocol,
                        asset_type=request.asset_types[0] if request.asset_types else "mixed",
                        forecast_period=request.timeframe
                    )
                )
            forecasts = await asyncio.gather(*forecast_tasks)
            response["forecasts"] = forecasts
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing yields: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/optimize")
async def optimize_portfolio(
    request: PortfolioOptimizationRequest,
    background_tasks: BackgroundTasks,
    agent: PortfolioOptimizerAgent = Depends(get_portfolio_agent)
):
    """优化投资组合"""
    try:
        # 准备初始状态
        initial_state = {
            "investment_amount": request.investment_amount,
            "risk_tolerance": request.risk_tolerance,
            "target_protocols": request.target_protocols or ["centrifuge", "goldfinch", "maple"],
            "constraints": request.constraints or {},
            "user_preferences": {
                "optimization_goal": request.optimization_goal
            },
            "messages": [],
            "completed": False
        }
        
        # 运行优化工作流
        result = await agent.run_workflow(initial_state)
        
        # 提取关键结果
        optimized_portfolio = result.get("optimized_portfolio", {})
        
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "investment_amount": request.investment_amount,
            "risk_tolerance": request.risk_tolerance,
            "portfolio": optimized_portfolio,
            "metrics": {
                "expected_annual_return": result.get("expected_returns", 0),
                "portfolio_risk": result.get("portfolio_risk", 0),
                "sharpe_ratio": result.get("sharpe_ratio", 0)
            },
            "recommendations": result.get("recommendations", []),
            "risk_warnings": result.get("risk_warnings", []),
            "rebalancing_schedule": result.get("rebalancing_schedule", [])
        }
        
        # 添加后台任务记录优化历史
        background_tasks.add_task(log_optimization, request.dict(), response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/yields/compare")
async def compare_yields(
    request: CompareYieldsRequest,
    agent: RWAYieldAgent = Depends(get_yield_agent)
):
    """比较不同协议的收益率"""
    try:
        comparison = await agent.compare_yields(
            protocols=request.protocols,
            asset_type=request.asset_type
        )
        
        # 获取详细数据
        protocol_data = await data_aggregator.fetch_all_yields()
        
        # 构建比较矩阵
        comparison_matrix = {}
        for protocol in request.protocols:
            if protocol in protocol_data:
                data = protocol_data[protocol]
                comparison_matrix[protocol] = {
                    "apy": data.apy if "apy" in request.metrics else None,
                    "risk_score": data.risk_score if "risk" in request.metrics else None,
                    "tvl": data.tvl if "liquidity" in request.metrics else None,
                    "pools_count": len(data.pools)
                }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "protocols": request.protocols,
            "asset_type": request.asset_type,
            "comparison_matrix": comparison_matrix,
            "analysis": comparison,
            "best_by_metric": {
                "highest_apy": max(comparison_matrix.items(), key=lambda x: x[1].get("apy", 0))[0] if "apy" in request.metrics else None,
                "lowest_risk": min(comparison_matrix.items(), key=lambda x: x[1].get("risk_score", 1))[0] if "risk" in request.metrics else None,
                "highest_liquidity": max(comparison_matrix.items(), key=lambda x: x[1].get("tvl", 0))[0] if "liquidity" in request.metrics else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing yields: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/yields/forecast")
async def forecast_yields(
    request: YieldForecastRequest,
    agent: RWAYieldAgent = Depends(get_yield_agent)
):
    """预测收益率"""
    try:
        forecast = await agent.forecast_yields(
            protocol=request.protocol,
            asset_type=request.asset_type,
            forecast_period=request.forecast_period
        )
        
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "protocol": request.protocol,
            "asset_type": request.asset_type,
            "forecast_period": request.forecast_period,
            "forecast": forecast
        }
        
        # 添加情景分析
        if request.include_scenarios:
            scenarios = {
                "bull_market": {
                    "description": "牛市情景 - 整体市场上涨",
                    "impact": "+20% to +50% APY",
                    "probability": 0.25
                },
                "bear_market": {
                    "description": "熊市情景 - 市场下跌",
                    "impact": "-30% to -10% APY",
                    "probability": 0.25
                },
                "stable_market": {
                    "description": "稳定市场 - 小幅波动",
                    "impact": "-5% to +5% APY",
                    "probability": 0.5
                }
            }
            response["scenarios"] = scenarios
        
        return response
        
    except Exception as e:
        logger.error(f"Error forecasting yields: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/yields/top-pools")
async def get_top_pools(
    criteria: str = "apy",
    limit: int = 10
):
    """获取顶级资产池"""
    try:
        top_pools = await data_aggregator.get_top_pools(criteria=criteria, limit=limit)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "criteria": criteria,
            "limit": limit,
            "pools": top_pools
        }
        
    except Exception as e:
        logger.error(f"Error getting top pools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats/aggregate")
async def get_aggregate_stats():
    """获取聚合统计数据"""
    try:
        stats = await data_aggregator.get_aggregated_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting aggregate stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alerts/yield-changes")
async def get_yield_change_alerts(threshold: float = 0.5):
    """获取收益率变化警报"""
    try:
        alerts = await data_aggregator.monitor_yield_changes(threshold=threshold)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "threshold": threshold,
            "alerts": alerts,
            "alert_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error getting yield alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 辅助函数
async def log_optimization(request_data: Dict, response_data: Dict):
    """记录优化历史（后台任务）"""
    # 这里可以保存到数据库或日志文件
    logger.info(f"Portfolio optimization completed: {request_data['investment_amount']} USD")

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("RWA Yield Optimizer API starting up...")
    # 预热缓存
    try:
        await data_aggregator.fetch_all_yields()
        logger.info("Data cache warmed up successfully")
    except Exception as e:
        logger.error(f"Failed to warm up cache: {e}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("RWA Yield Optimizer API shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    # 获取配置
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    
    # 运行服务器
    uvicorn.run(
        "api.rwa_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )