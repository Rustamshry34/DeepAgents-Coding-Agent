"""
Persistent Memory System for DeepAgents Coding Assistant
This module adds persistent memory capabilities to the coding agent.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
import sqlite3


class PersistentMemoryManager:
    """
    Manages persistent memory for the DeepAgents coding assistant.
    Supports SQLite, PostgreSQL, and in-memory storage options.
    """
    
    def __init__(self, storage_type: str = "sqlite", connection_string: str = None):
        """
        Initialize the persistent memory manager.
        
        Args:
            storage_type: Type of storage ("sqlite", "postgres", or "memory")
            connection_string: Connection string for database storage
        """
        self.storage_type = storage_type
        self.connection_string = connection_string or "./agent_memory.db"
        self.checkpointer = self._initialize_checkpointer()
    
    def _initialize_checkpointer(self):
        """Initialize the appropriate checkpointer based on storage type."""
        if self.storage_type == "sqlite":
            # Ensure the directory exists
            db_dir = os.path.dirname(self.connection_string)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.connection_string)
            return SqliteSaver(conn)
        
        elif self.storage_type == "memory":
            # In-memory checkpointer (not truly persistent but useful for testing)
            return MemorySaver()
        
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def get_checkpointer(self):
        """Return the initialized checkpointer."""
        return self.checkpointer
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        stats = {
            "storage_type": self.storage_type,
            "connection_string": self.connection_string,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add storage-specific stats
        if self.storage_type == "sqlite":
            if os.path.exists(self.connection_string):
                stats["db_size_bytes"] = os.path.getsize(self.connection_string)
                stats["db_exists"] = True
            else:
                stats["db_exists"] = False
        
        return stats


def create_persistent_agent(
    model=None,
    tools=None,
    system_prompt=None,
    middleware=None,
    subagents=None,
    storage_type="sqlite",
    connection_string=None,
    **kwargs
):
    """
    Create a DeepAgent with persistent memory capabilities.
    
    Args:
        model: The LLM model to use
        tools: List of tools to give the agent
        system_prompt: System prompt for the agent
        middleware: Additional middleware
        subagents: Subagents to include
        storage_type: Type of persistent storage ("sqlite", "postgres", or "memory")
        connection_string: Database connection string (if applicable)
        **kwargs: Additional arguments passed to create_deep_agent
    
    Returns:
        A compiled DeepAgent graph with persistent memory
    """
    from deepagents import create_deep_agent
    
    # Create the memory manager
    memory_manager = PersistentMemoryManager(
        storage_type=storage_type,
        connection_string=connection_string
    )
    
    # Add the checkpointer to kwargs
    kwargs['checkpointer'] = memory_manager.get_checkpointer()
    
    # Create the agent with persistent memory
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        middleware=middleware,
        subagents=subagents,
        **kwargs
    )
    
    return agent, memory_manager


# Example usage function
def get_default_persistent_agent(llm, tools, subagents):
    """
    Create a default persistent agent with SQLite memory.
    
    Args:
        llm: The language model to use
        tools: List of tools for the agent
        subagents: List of subagents
    
    Returns:
        Tuple of (agent, memory_manager)
    """
    system_prompt = (
        "You are an advanced coding agent. You may delegate to planner, coder, "
        "and reviewer sub-agents. Always search the web when you lack knowledge. "
        "Keep answers concise and actionable. Your conversations and state are "
        "persistently stored and remembered across sessions."
    )
    
    return create_persistent_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        subagents=subagents,
        storage_type="sqlite",
        connection_string="./agent_memory.db"
    )