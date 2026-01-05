"""
Enhanced Agent with Observability, Cost Tracking, and Debugging Features
This module adds observability/tracing, cost tracking, and replay/debugging capabilities to the coding agent.
"""
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from contextlib import contextmanager

# Import existing modules
from memory_agent import get_default_persistent_agent
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama


class StepType(Enum):
    """Types of steps in the agent workflow"""
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    SEARCH = "search"
    USER_INPUT = "user_input"
    ASSISTANT_RESPONSE = "assistant_response"


@dataclass
class AgentStep:
    """Represents a single step in the agent's execution"""
    step_id: str
    step_type: StepType
    timestamp: float
    input_data: Any
    output_data: Any
    execution_time: float
    cost_estimate: float
    metadata: Dict[str, Any]


class CostTracker:
    """Tracks costs associated with agent operations"""
    
    def __init__(self):
        self.total_cost = 0.0
        self.step_costs = []
        # Cost estimates per operation type (in USD)
        self.cost_per_operation = {
            "llm_call": 0.00001,  # Placeholder cost
            "search": 0.0001,      # Placeholder cost
            "code_execution": 0.001,  # Placeholder cost
            "file_operation": 0.00005  # Placeholder cost
        }
    
    def estimate_cost(self, operation_type: str, input_size: int = 1) -> float:
        """Estimate cost for a specific operation"""
        base_cost = self.cost_per_operation.get(operation_type, 0.0)
        return base_cost * input_size
    
    def record_step_cost(self, operation_type: str, input_size: int = 1) -> float:
        """Record cost for a step and return the cost"""
        cost = self.estimate_cost(operation_type, input_size)
        self.total_cost += cost
        self.step_costs.append({
            "operation_type": operation_type,
            "input_size": input_size,
            "cost": cost,
            "timestamp": time.time()
        })
        return cost


class StepBudget:
    """Manages step budget for agent execution"""
    
    def __init__(self, max_steps: int = 50, max_time: float = 3600.0):  # 1 hour default
        self.max_steps = max_steps
        self.max_time = max_time
        self.current_steps = 0
        self.start_time = time.time()
        self.step_history = []
    
    def add_step(self, step_type: StepType, metadata: Dict[str, Any] = None):
        """Add a step to the budget"""
        self.current_steps += 1
        elapsed_time = time.time() - self.start_time
        
        step_record = {
            "step_number": self.current_steps,
            "step_type": step_type.value,
            "timestamp": time.time(),
            "elapsed_time": elapsed_time,
            "metadata": metadata or {}
        }
        
        self.step_history.append(step_record)
        
        # Check if budget is exceeded
        if self.current_steps > self.max_steps:
            raise Exception(f"Step budget exceeded: {self.current_steps}/{self.max_steps}")
        
        if elapsed_time > self.max_time:
            raise Exception(f"Time budget exceeded: {elapsed_time:.2f}s/{self.max_time}s")
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status"""
        elapsed_time = time.time() - self.start_time
        return {
            "max_steps": self.max_steps,
            "current_steps": self.current_steps,
            "max_time": self.max_time,
            "elapsed_time": elapsed_time,
            "time_remaining": max(0, self.max_time - elapsed_time),
            "steps_remaining": max(0, self.max_steps - self.current_steps),
            "budget_exceeded": (
                self.current_steps > self.max_steps or 
                elapsed_time > self.max_time
            )
        }


class TraceLogger:
    """Handles observability and tracing of agent operations"""
    
    def __init__(self, db_path: str = "./agent_trace.db"):
        self.db_path = db_path
        self._init_db()
        self.trace_id = f"trace_{int(time.time())}_{os.getpid()}"
    
    def _init_db(self):
        """Initialize the trace database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                input_data TEXT,
                output_data TEXT,
                execution_time REAL,
                cost_estimate REAL,
                metadata TEXT,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                start_time REAL NOT NULL,
                end_time REAL,
                total_steps INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_step(self, step: AgentStep, session_id: str):
        """Log a step to the trace database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO traces 
            (trace_id, step_id, step_type, timestamp, input_data, output_data, 
             execution_time, cost_estimate, metadata, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.trace_id,
            step.step_id,
            step.step_type.value,
            step.timestamp,
            json.dumps(step.input_data) if step.input_data else None,
            json.dumps(step.output_data) if step.output_data else None,
            step.execution_time,
            step.cost_estimate,
            json.dumps(step.metadata) if step.metadata else None,
            session_id
        ))
        
        conn.commit()
        conn.close()
    
    def start_session(self, session_id: str, metadata: Dict[str, Any] = None):
        """Start a new tracing session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, start_time, metadata)
            VALUES (?, ?, ?)
        ''', (session_id, time.time(), json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
    
    def end_session(self, session_id: str, total_steps: int, total_cost: float):
        """End a tracing session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, total_steps = ?, total_cost = ?
            WHERE session_id = ?
        ''', (time.time(), total_steps, total_cost, session_id))
        
        conn.commit()
        conn.close()
    
    def get_trace_history(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve trace history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM traces WHERE session_id = ? ORDER BY timestamp
            ''', (session_id,))
        else:
            cursor.execute('''
                SELECT * FROM traces ORDER BY timestamp DESC LIMIT 100
            ''')
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        traces = []
        for row in rows:
            trace_dict = dict(zip(columns, row))
            # Parse JSON fields
            for field in ['input_data', 'output_data', 'metadata']:
                if trace_dict[field]:
                    try:
                        trace_dict[field] = json.loads(trace_dict[field])
                    except:
                        pass  # Keep as string if JSON parsing fails
            traces.append(trace_dict)
        
        conn.close()
        return traces


class ReplayDebugger:
    """Provides replay and debugging capabilities"""
    
    def __init__(self, trace_logger: TraceLogger):
        self.trace_logger = trace_logger
    
    def replay_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Replay a complete session from trace logs"""
        traces = self.trace_logger.get_trace_history(session_id)
        print(f"Replaying session {session_id} with {len(traces)} steps...")
        
        replay_results = []
        for trace in traces:
            print(f"Step: {trace['step_type']} at {datetime.fromtimestamp(trace['timestamp'])}")
            print(f"Input: {trace['input_data']}")
            print(f"Output: {trace['output_data']}")
            print(f"Execution time: {trace['execution_time']}s")
            print("-" * 50)
            
            replay_results.append({
                "step_type": trace['step_type'],
                "input_data": trace['input_data'],
                "output_data": trace['output_data'],
                "execution_time": trace['execution_time']
            })
        
        return replay_results
    
    def debug_step(self, step_id: str) -> Dict[str, Any]:
        """Debug a specific step"""
        conn = sqlite3.connect(self.trace_logger.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM traces WHERE step_id = ?
        ''', (step_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            trace_dict = dict(zip(columns, row))
            # Parse JSON fields
            for field in ['input_data', 'output_data', 'metadata']:
                if trace_dict[field]:
                    try:
                        trace_dict[field] = json.loads(trace_dict[field])
                    except:
                        pass  # Keep as string if JSON parsing fails
        else:
            trace_dict = None
        
        conn.close()
        return trace_dict


class EnhancedAgent:
    """Enhanced agent with observability, cost tracking, and debugging features"""
    
    def __init__(self, llm, tools, subagents, max_steps: int = 50, max_time: float = 3600.0):
        # Initialize the base agent
        self.base_agent, self.memory_manager = get_default_persistent_agent(llm, tools, subagents)
        
        # Initialize enhanced features
        self.trace_logger = TraceLogger()
        self.cost_tracker = CostTracker()
        self.step_budget = StepBudget(max_steps, max_time)
        self.replay_debugger = ReplayDebugger(self.trace_logger)
        
        # Thread-local storage for current session
        self._local = threading.local()
    
    def _get_session_id(self) -> str:
        """Get or create session ID for the current thread"""
        if not hasattr(self._local, 'session_id'):
            self._local.session_id = f"session_{int(time.time())}_{threading.get_ident()}"
            self.trace_logger.start_session(self._local.session_id)
        return self._local.session_id
    
    def _execute_with_monitoring(self, func: Callable, step_type: StepType, input_data: Any, 
                                operation_type: str = "llm_call") -> Any:
        """Execute a function with monitoring and tracing"""
        start_time = time.time()
        session_id = self._get_session_id()
        
        # Check budget before executing
        try:
            self.step_budget.add_step(step_type, {"input_size": len(str(input_data)) if input_data else 0})
        except Exception as e:
            print(f"Budget exceeded: {e}")
            return {"error": str(e)}
        
        # Estimate and record cost
        input_size = len(str(input_data)) if input_data else 1
        cost = self.cost_tracker.record_step_cost(operation_type, input_size)
        
        try:
            # Execute the actual function
            result = func()
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create and log step
            step = AgentStep(
                step_id=f"step_{int(time.time() * 1000000)}",  # microsecond precision
                step_type=step_type,
                timestamp=start_time,
                input_data=input_data,
                output_data=result,
                execution_time=execution_time,
                cost_estimate=cost,
                metadata={
                    "operation_type": operation_type,
                    "input_size": input_size
                }
            )
            
            self.trace_logger.log_step(step, session_id)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {"error": str(e)}
            
            # Log error step
            step = AgentStep(
                step_id=f"step_{int(time.time() * 1000000)}",
                step_type=step_type,
                timestamp=start_time,
                input_data=input_data,
                output_data=error_result,
                execution_time=execution_time,
                cost_estimate=cost,
                metadata={
                    "operation_type": operation_type,
                    "input_size": input_size,
                    "error": str(e)
                }
            )
            
            self.trace_logger.log_step(step, session_id)
            raise e
    
    def invoke(self, input_data: Dict[str, Any], config: Dict[str, Any] = None):
        """Invoke the agent with monitoring"""
        # Ensure config has thread_id for the base agent
        if config is None:
            config = {"configurable": {"thread_id": "default_thread"}}
        elif "configurable" not in config:
            config["configurable"] = {"thread_id": "default_thread"}
        elif "thread_id" not in config["configurable"]:
            config["configurable"]["thread_id"] = "default_thread"
        
        def execute_base_agent():
            return self.base_agent.invoke(input_data, config)
        
        return self._execute_with_monitoring(
            execute_base_agent,
            StepType.ASSISTANT_RESPONSE,
            input_data,
            "llm_call"
        )
    
    def stream(self, input_data: Dict[str, Any], config: Dict[str, Any] = None):
        """Stream the agent response with monitoring"""
        # Ensure config has thread_id for the base agent
        if config is None:
            config = {"configurable": {"thread_id": "default_thread"}}
        elif "configurable" not in config:
            config["configurable"] = {"thread_id": "default_thread"}
        elif "thread_id" not in config["configurable"]:
            config["configurable"]["thread_id"] = "default_thread"
        
        def execute_base_agent():
            return self.base_agent.stream(input_data, config)
        
        return self._execute_with_monitoring(
            execute_base_agent,
            StepType.ASSISTANT_RESPONSE,
            input_data,
            "llm_call"
        )
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status"""
        return self.step_budget.get_budget_status()
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        return {
            "total_cost": self.cost_tracker.total_cost,
            "step_costs": self.cost_tracker.step_costs
        }
    
    def get_trace_history(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Get trace history for debugging"""
        return self.trace_logger.get_trace_history(session_id)
    
    def replay_current_session(self) -> List[Dict[str, Any]]:
        """Replay the current session"""
        session_id = self._get_session_id()
        return self.replay_debugger.replay_session(session_id)
    
    def end_session(self):
        """End the current session and log final stats"""
        if hasattr(self._local, 'session_id'):
            session_id = self._local.session_id
            self.trace_logger.end_session(
                session_id,
                self.step_budget.current_steps,
                self.cost_tracker.total_cost
            )
            # Clean up thread-local storage
            delattr(self._local, 'session_id')


def get_enhanced_agent(llm, tools, subagents, max_steps: int = 50, max_time: float = 3600.0):
    """
    Create an enhanced agent with observability, cost tracking, and debugging features.
    
    Args:
        llm: The language model to use
        tools: List of tools for the agent
        subagents: List of subagents
        max_steps: Maximum number of steps allowed per session
        max_time: Maximum time allowed per session in seconds
    
    Returns:
        EnhancedAgent instance with all requested features
    """
    return EnhancedAgent(llm, tools, subagents, max_steps, max_time)