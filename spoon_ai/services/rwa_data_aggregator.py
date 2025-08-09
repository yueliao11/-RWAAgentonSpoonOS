"""
RWA Data Aggregator Service - 聚合和缓存RWA协议数据
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiohttp
import logging
from functools import lru_cache
import redis.asyncio as redis

logger = logging.getLogger(__name__)

@dataclass
class ProtocolYieldData:
    """协议收益数据结构"""
    protocol: str
    apy: float
    tvl: float
    risk_score: float
    last_updated: datetime
    pools: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolYieldData':
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


class ProtocolConnector:
    """协议连接器基类"""
    
    def __init__(self, protocol_name: str):
        self.protocol_name = protocol_name
        self.api_key = os.getenv(f"{protocol_name.upper()}_API_KEY")
        self.api_url = os.getenv(f"{protocol_name.upper()}_API_URL")
    
    async def fetch_yields(self) -> ProtocolYieldData:
        """获取收益数据（子类需要实现）"""
        raise NotImplementedError


class CentrifugeConnector(ProtocolConnector):
    """Centrifuge协议连接器"""
    
    def __init__(self):
        super().__init__("centrifuge")
    
    async def fetch_yields(self) -> ProtocolYieldData:
        """获取Centrifuge收益数据"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                
                # 实际API调用
                # async with session.get(f"{self.api_url}/pools", headers=headers) as response:
                #     data = await response.json()
                
                # 模拟数据
                pools = [
                    {
                        "id": "centrifuge-pool-1",
                        "name": "Real Estate Income Fund",
                        "apy": 8.5,
                        "tvl": 50000000,
                        "asset_type": "real_estate"
                    },
                    {
                        "id": "centrifuge-pool-2",
                        "name": "Trade Finance Pool",
                        "apy": 9.2,
                        "tvl": 30000000,
                        "asset_type": "invoices"
                    }
                ]
                
                avg_apy = sum(p["apy"] for p in pools) / len(pools)
                total_tvl = sum(p["tvl"] for p in pools)
                
                return ProtocolYieldData(
                    protocol="centrifuge",
                    apy=avg_apy,
                    tvl=total_tvl,
                    risk_score=0.35,
                    last_updated=datetime.utcnow(),
                    pools=pools
                )
                
        except Exception as e:
            logger.error(f"Error fetching Centrifuge data: {e}")
            raise


class GoldfinchConnector(ProtocolConnector):
    """Goldfinch协议连接器"""
    
    def __init__(self):
        super().__init__("goldfinch")
        self.subgraph_url = os.getenv("GOLDFINCH_SUBGRAPH_URL")
    
    async def fetch_yields(self) -> ProtocolYieldData:
        """获取Goldfinch收益数据"""
        try:
            # GraphQL查询
            query = """
            {
                seniorPools(first: 5) {
                    id
                    estimatedApy
                    totalDeposited
                    sharePrice
                }
            }
            """
            
            # 模拟数据（实际应该调用GraphQL）
            pools = [
                {
                    "id": "goldfinch-senior-1",
                    "name": "Senior Pool",
                    "apy": 10.2,
                    "tvl": 120000000,
                    "asset_type": "private_credit"
                },
                {
                    "id": "goldfinch-backer-1",
                    "name": "Almavest Basket #7",
                    "apy": 12.5,
                    "tvl": 15000000,
                    "asset_type": "private_credit"
                }
            ]
            
            avg_apy = sum(p["apy"] for p in pools) / len(pools)
            total_tvl = sum(p["tvl"] for p in pools)
            
            return ProtocolYieldData(
                protocol="goldfinch",
                apy=avg_apy,
                tvl=total_tvl,
                risk_score=0.42,
                last_updated=datetime.utcnow(),
                pools=pools
            )
            
        except Exception as e:
            logger.error(f"Error fetching Goldfinch data: {e}")
            raise


class MapleConnector(ProtocolConnector):
    """Maple Finance协议连接器"""
    
    def __init__(self):
        super().__init__("maple")
    
    async def fetch_yields(self) -> ProtocolYieldData:
        """获取Maple Finance收益数据"""
        try:
            # 模拟数据
            pools = [
                {
                    "id": "maple-pool-1",
                    "name": "Orthogonal Trading USDC",
                    "apy": 9.8,
                    "tvl": 80000000,
                    "asset_type": "private_credit"
                },
                {
                    "id": "maple-pool-2",
                    "name": "Maven 11 USDC",
                    "apy": 8.9,
                    "tvl": 45000000,
                    "asset_type": "private_credit"
                }
            ]
            
            avg_apy = sum(p["apy"] for p in pools) / len(pools)
            total_tvl = sum(p["tvl"] for p in pools)
            
            return ProtocolYieldData(
                protocol="maple",
                apy=avg_apy,
                tvl=total_tvl,
                risk_score=0.38,
                last_updated=datetime.utcnow(),
                pools=pools
            )
            
        except Exception as e:
            logger.error(f"Error fetching Maple data: {e}")
            raise


class RWADataAggregator:
    """RWA数据聚合器"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl  # 缓存时间（秒）
        self.protocols = {
            "centrifuge": CentrifugeConnector(),
            "goldfinch": GoldfinchConnector(),
            "maple": MapleConnector(),
        }
        
        # Redis缓存配置
        self.redis_client = None
        self._init_redis()
        
        # 内存缓存
        self._memory_cache: Dict[str, ProtocolYieldData] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def _init_redis(self):
        """初始化Redis连接"""
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_password = os.getenv("REDIS_PASSWORD")
            
            # 注意：实际使用时需要在异步上下文中初始化
            # self.redis_client = redis.Redis(
            #     host=redis_host,
            #     port=redis_port,
            #     password=redis_password,
            #     decode_responses=True
            # )
        except Exception as e:
            logger.warning(f"Redis initialization failed, using memory cache only: {e}")
    
    async def fetch_all_yields(self, use_cache: bool = True) -> Dict[str, ProtocolYieldData]:
        """获取所有协议的收益数据"""
        results = {}
        
        # 并行获取所有协议数据
        tasks = []
        for protocol_name, connector in self.protocols.items():
            if use_cache:
                task = self._fetch_with_cache(protocol_name, connector)
            else:
                task = connector.fetch_yields()
            tasks.append(task)
        
        protocol_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for protocol_name, data in zip(self.protocols.keys(), protocol_data_list):
            if isinstance(data, Exception):
                logger.error(f"Failed to fetch {protocol_name} data: {data}")
                # 尝试使用缓存数据
                cached = self._get_from_memory_cache(protocol_name)
                if cached:
                    results[protocol_name] = cached
            else:
                results[protocol_name] = data
                # 更新内存缓存
                self._set_memory_cache(protocol_name, data)
        
        return results
    
    async def _fetch_with_cache(self, protocol_name: str, connector: ProtocolConnector) -> ProtocolYieldData:
        """带缓存的数据获取"""
        # 检查内存缓存
        cached_data = self._get_from_memory_cache(protocol_name)
        if cached_data:
            return cached_data
        
        # 检查Redis缓存
        if self.redis_client:
            try:
                cached_json = await self.redis_client.get(f"rwa:yields:{protocol_name}")
                if cached_json:
                    data_dict = json.loads(cached_json)
                    return ProtocolYieldData.from_dict(data_dict)
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")
        
        # 获取新数据
        data = await connector.fetch_yields()
        
        # 更新缓存
        self._set_memory_cache(protocol_name, data)
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"rwa:yields:{protocol_name}",
                    self.cache_ttl,
                    json.dumps(data.to_dict())
                )
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")
        
        return data
    
    def _get_from_memory_cache(self, protocol_name: str) -> Optional[ProtocolYieldData]:
        """从内存缓存获取数据"""
        if protocol_name in self._memory_cache:
            timestamp = self._cache_timestamps.get(protocol_name)
            if timestamp and (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                return self._memory_cache[protocol_name]
        return None
    
    def _set_memory_cache(self, protocol_name: str, data: ProtocolYieldData):
        """设置内存缓存"""
        self._memory_cache[protocol_name] = data
        self._cache_timestamps[protocol_name] = datetime.utcnow()
    
    def standardize_apy(self, raw_data: Dict[str, Any]) -> float:
        """标准化APY计算"""
        rate = raw_data.get("rate", 0)
        frequency = raw_data.get("compound_frequency", "daily")
        
        frequencies = {
            "daily": 365,
            "weekly": 52,
            "monthly": 12,
            "quarterly": 4,
            "annually": 1
        }
        
        n = frequencies.get(frequency, 365)
        # 复利计算: APY = (1 + r/n)^n - 1
        apy = (1 + rate / n) ** n - 1
        return apy * 100  # 转换为百分比
    
    async def get_aggregated_stats(self) -> Dict[str, Any]:
        """获取聚合统计数据"""
        all_data = await self.fetch_all_yields()
        
        total_tvl = sum(data.tvl for data in all_data.values())
        avg_apy = sum(data.apy for data in all_data.values()) / len(all_data) if all_data else 0
        
        # 按TVL加权的平均APY
        weighted_apy = sum(
            data.apy * (data.tvl / total_tvl) 
            for data in all_data.values()
        ) if total_tvl > 0 else 0
        
        # 风险分布
        risk_distribution = {
            "low": 0,  # < 0.3
            "medium": 0,  # 0.3 - 0.6
            "high": 0  # > 0.6
        }
        
        for data in all_data.values():
            if data.risk_score < 0.3:
                risk_distribution["low"] += 1
            elif data.risk_score < 0.6:
                risk_distribution["medium"] += 1
            else:
                risk_distribution["high"] += 1
        
        return {
            "total_tvl": total_tvl,
            "average_apy": round(avg_apy, 2),
            "weighted_average_apy": round(weighted_apy, 2),
            "protocol_count": len(all_data),
            "risk_distribution": risk_distribution,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_top_pools(self, criteria: str = "apy", limit: int = 10) -> List[Dict[str, Any]]:
        """获取排名靠前的资产池"""
        all_data = await self.fetch_all_yields()
        
        all_pools = []
        for protocol_data in all_data.values():
            for pool in protocol_data.pools:
                pool["protocol"] = protocol_data.protocol
                pool["protocol_risk_score"] = protocol_data.risk_score
                all_pools.append(pool)
        
        # 根据标准排序
        if criteria == "apy":
            all_pools.sort(key=lambda x: x.get("apy", 0), reverse=True)
        elif criteria == "tvl":
            all_pools.sort(key=lambda x: x.get("tvl", 0), reverse=True)
        elif criteria == "risk_adjusted":
            # 风险调整后收益排序
            risk_free_rate = 4.5
            all_pools.sort(
                key=lambda x: (x.get("apy", 0) - risk_free_rate) / (x.get("protocol_risk_score", 0.5) + 0.1),
                reverse=True
            )
        
        return all_pools[:limit]
    
    async def monitor_yield_changes(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """监控收益率变化"""
        current_data = await self.fetch_all_yields(use_cache=False)
        alerts = []
        
        for protocol_name, current in current_data.items():
            # 获取历史数据（从缓存）
            historical = self._get_from_memory_cache(protocol_name)
            
            if historical and abs(current.apy - historical.apy) > threshold:
                alerts.append({
                    "protocol": protocol_name,
                    "previous_apy": historical.apy,
                    "current_apy": current.apy,
                    "change": current.apy - historical.apy,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return alerts