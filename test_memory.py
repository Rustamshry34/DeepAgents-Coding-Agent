"""
Test script to verify persistent memory functionality
"""
import os
from memory_agent import PersistentMemoryManager

def test_persistent_memory():
    """Test the persistent memory system."""
    print("Testing Persistent Memory System...")
    
    # Test SQLite memory manager
    memory_manager = PersistentMemoryManager(
        storage_type="sqlite",
        connection_string="./test_memory.db"
    )
    
    # Check memory stats
    stats = memory_manager.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    # Verify the database file was created
    if os.path.exists("./test_memory.db"):
        print("✓ SQLite database created successfully")
    else:
        print("✗ SQLite database not found")
    
    # Get the checkpointer
    checkpointer = memory_manager.get_checkpointer()
    print(f"✓ Checkpointer created: {type(checkpointer)}")
    
    print("Persistent memory system test completed successfully!")

if __name__ == "__main__":
    test_persistent_memory()