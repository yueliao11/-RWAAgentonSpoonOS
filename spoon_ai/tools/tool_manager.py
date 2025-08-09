import os
from typing import Any, Dict, Iterator, List

from openai import OpenAI
import pinecone

from spoon_ai.tools.base import BaseTool, ToolFailure, ToolResult


class ToolManager:
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
        self.indexed = False
        
    
    def _lazy_init_pinecone(self):
        if not hasattr(self, "pc"):
            pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))
            index_name = "dex-tools"
            
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=3072,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(index_name)
            self.embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def __getitem__(self, name: str) -> BaseTool:
        return self.tool_map[name]
    
    def __iter__(self) -> Iterator[BaseTool]:
        return iter(self.tools)
    
    def __len__(self) -> int:
        return len(self.tools)
    
    def to_params(self) -> List[Dict[str, Any]]:
        return [tool.to_param() for tool in self.tools]
    
    async def execute(self, * ,name: str, tool_input: Dict[str, Any] =None) -> ToolResult:
        tool = self.tool_map[name]
        if not tool:
            return ToolFailure(error=f"Tool {name} not found")
    
        try:
            result = await tool(**tool_input)
            return result
        except Exception as e:
            return ToolFailure(error=str(e))
        
    def get_tool(self, name: str) -> BaseTool:
        tool = self.tool_map.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool
    
    def add_tool(self, tool: BaseTool) -> None:
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        
    def add_tools(self, *tools: BaseTool) -> None:
        for tool in tools:
            self.add_tool(tool)
            
    def remove_tool(self, name: str) -> None:
        self.tools = [tool for tool in self.tools if tool.name != name]
        del self.tool_map[name]       

    def index_tools(self):
        self._lazy_init_pinecone()
        vectors = []
        for tool in self.tools:
            embedding_vector = self.embedding_client.embeddings.create(
                input=tool.description,
                model="text-embedding-3-large"
            )
            vectors.append(
                {
                    "id": tool.name,
                    "values": embedding_vector.data[0].embedding,
                    "metadata": {
                        "name": tool.name,
                        "description": tool.description
                    }
                }
            )
        self.index.upsert(vectors=vectors, namespace="dex-tools-test")
        self.indexed = True
        
    def query_tools(self, query: str, top_k: int = 5, rerank_k: int = 20) -> List[BaseTool]:
        if not self.indexed:
            self.index_tools()
        embedding_vector = self.embedding_client.embeddings.create(
            input=query,
            model="text-embedding-3-large"
        )
        results = self.index.query(
            namespace="dex-tools-test",
            top_k=rerank_k,
            include_metadata=True,
            include_values=False,
            vector=embedding_vector.data[0].embedding
        )
        print(results)
        doc_to_tool = {}
        for match in results["matches"]:
            doc_to_tool[match["metadata"]["description"]] = match["id"]
        
        result_tool_names = []
        for match in results["matches"][:top_k]:
            result_tool_names.append(match["id"])
        return result_tool_names