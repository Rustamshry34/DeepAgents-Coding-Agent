"""
Test script for the enhanced agent with observability, cost tracking, and debugging features
"""
import os
from enhanced_agent import get_enhanced_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool


# Define some basic tools for testing
@tool
def test_tool(query: str) -> str:
    """A simple test tool"""
    return f"Test tool response for: {query}"


def test_enhanced_agent():
    """Test the enhanced agent features"""
    print("Testing Enhanced Agent with Observability, Cost Tracking, and Debugging...")
    
    # Initialize the LLM
    llm = ChatOllama(
        model="qwen3-coder:30b",
        base_url="http://localhost:11434",
        temperature=0,
    )
    
    # Create enhanced agent
    agent = get_enhanced_agent(
        llm=llm,
        tools=[test_tool],
        subagents=[],
        max_steps=10,
        max_time=300.0  # 5 minutes
    )
    
    print("✓ Enhanced agent created successfully")
    
    # Test basic invocation
    print("\n1. Testing basic invocation...")
    try:
        response = agent.invoke({
            "messages": [{"role": "user", "content": "Hello, what can you do?"}]
        }, config={"configurable": {"thread_id": "test_thread"}})
        print(f"✓ Basic invocation successful: {type(response)}")
    except Exception as e:
        print(f"✗ Basic invocation failed: {e}")
    
    # Test streaming
    print("\n1b. Testing streaming...")
    try:
        for event in agent.stream({
            "messages": [{"role": "user", "content": "Hello, what can you do?"}]
        }, config={"configurable": {"thread_id": "test_thread"}}):
            if "messages" in event:
                msg = event["messages"][-1]
                print(f"✓ Streaming successful: {type(msg)}")
                break
    except Exception as e:
        print(f"✗ Streaming failed: {e}")
    
    # Test budget status
    print("\n2. Testing budget status...")
    try:
        budget_status = agent.get_budget_status()
        print(f"✓ Budget status retrieved: {budget_status}")
    except Exception as e:
        print(f"✗ Budget status failed: {e}")
    
    # Test cost summary
    print("\n3. Testing cost summary...")
    try:
        cost_summary = agent.get_cost_summary()
        print(f"✓ Cost summary retrieved: {cost_summary}")
    except Exception as e:
        print(f"✗ Cost summary failed: {e}")
    
    # Test trace history
    print("\n4. Testing trace history...")
    try:
        trace_history = agent.get_trace_history()
        print(f"✓ Trace history retrieved: {len(trace_history)} steps")
    except Exception as e:
        print(f"✗ Trace history failed: {e}")
    
    # Test replay functionality
    print("\n5. Testing replay functionality...")
    try:
        replay_results = agent.replay_current_session()
        print(f"✓ Replay functionality tested: {len(replay_results)} steps replayed")
    except Exception as e:
        print(f"✗ Replay functionality failed: {e}")
    
    print("\n✓ All tests completed!")
    

if __name__ == "__main__":
    test_enhanced_agent()