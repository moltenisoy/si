#!/usr/bin/env python3
"""
Test script to verify the enhanced optimizer classes are functioning correctly.
This script tests the basic functionality of the newly activated optimizer classes.
"""

import sys
import time

# Mock the handle cache for testing
class MockHandleCache:
    def get_handle(self, pid, access):
        return None

def test_memory_scrubbing_optimizer():
    """Test MemoryScrubbingOptimizer functionality"""
    print("\n=== Testing MemoryScrubbingOptimizer ===")
    try:
        from optimusprime import MemoryScrubbingOptimizer
        
        mso = MemoryScrubbingOptimizer()
        print("✓ Instantiated MemoryScrubbingOptimizer")
        
        # Test enable
        mso.enable()
        assert mso.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test interval setting
        mso.set_scrubbing_interval(30)
        assert mso.scrubbing_interval == 30, "Set interval failed"
        print("✓ Set scrubbing interval works")
        
        # Test metrics
        metrics = mso.get_metrics()
        assert 'enabled' in metrics, "Metrics missing 'enabled'"
        assert metrics['enabled'] == True, "Metrics show wrong enabled state"
        print(f"✓ Metrics: {metrics}")
        
        # Test disable
        mso.disable()
        assert mso.enabled == False, "Disable failed"
        print("✓ Disable method works")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_coherency_optimizer():
    """Test CacheCoherencyOptimizer functionality"""
    print("\n=== Testing CacheCoherencyOptimizer ===")
    try:
        from optimusprime import CacheCoherencyOptimizer
        
        cco = CacheCoherencyOptimizer()
        print("✓ Instantiated CacheCoherencyOptimizer")
        
        # Test enable
        cco.enable()
        assert cco.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test protocol setting
        cco.set_coherency_protocol('MESI')
        assert cco.coherency_protocol == 'MESI', "Protocol setting failed"
        print("✓ Set coherency protocol works")
        
        # Test cache line initialization
        cco.initialize_cache_lines()
        assert 'modified' in cco.cache_lines, "MESI cache lines not initialized"
        print(f"✓ Cache lines initialized: {list(cco.cache_lines.keys())}")
        
        # Test metrics
        metrics = cco.get_metrics()
        assert metrics['enabled'] == True, "Metrics show wrong enabled state"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_bandwidth_manager():
    """Test MemoryBandwidthManager functionality"""
    print("\n=== Testing MemoryBandwidthManager ===")
    try:
        from optimusprime import MemoryBandwidthManager
        
        mbm = MemoryBandwidthManager(MockHandleCache())
        print("✓ Instantiated MemoryBandwidthManager")
        
        # Test enable
        mbm.enable()
        assert mbm.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test bandwidth limit setting
        mbm.set_bandwidth_limit(80)
        assert mbm.bandwidth_limit == 80, "Bandwidth limit setting failed"
        print("✓ Set bandwidth limit works")
        
        # Test QoS configuration
        mbm.configure_qos_policies()
        assert 'high_priority' in mbm.qos_policies, "QoS policies not configured"
        print(f"✓ QoS policies configured: {list(mbm.qos_policies.keys())}")
        
        # Test metrics
        metrics = mbm.get_metrics()
        assert metrics['bandwidth_limit'] == 80, "Metrics show wrong bandwidth limit"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_aggressive_write_cache():
    """Test AggressiveWriteCache functionality"""
    print("\n=== Testing AggressiveWriteCache ===")
    try:
        from optimusprime import AggressiveWriteCache
        
        awc = AggressiveWriteCache()
        print("✓ Instantiated AggressiveWriteCache")
        
        # Test enable
        awc.enable()
        assert awc.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test cache size setting
        cache_size = 512 * 1024 * 1024  # 512MB
        awc.set_cache_size(cache_size)
        assert awc.cache_size == cache_size, "Cache size setting failed"
        print(f"✓ Set cache size works: {awc.cache_size / (1024*1024):.0f}MB")
        
        # Test write policy setting
        awc.set_write_policy('write-back')
        assert awc.write_policy == 'write-back', "Write policy setting failed"
        print("✓ Set write policy works")
        
        # Test metrics
        metrics = awc.get_metrics()
        assert metrics['write_policy'] == 'write-back', "Metrics show wrong write policy"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_custom_io_scheduler():
    """Test CustomIOScheduler functionality"""
    print("\n=== Testing CustomIOScheduler ===")
    try:
        from optimusprime import CustomIOScheduler
        
        cios = CustomIOScheduler()
        print("✓ Instantiated CustomIOScheduler")
        
        # Test enable
        cios.enable()
        assert cios.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test algorithm setting
        cios.set_scheduling_algorithm('deadline')
        assert cios.scheduling_algorithm == 'deadline', "Algorithm setting failed"
        print("✓ Set scheduling algorithm works")
        
        # Test queue depth setting
        cios.set_queue_depth(256)
        assert cios.queue_depth == 256, "Queue depth setting failed"
        print("✓ Set queue depth works")
        
        # Test metrics
        metrics = cios.get_metrics()
        assert metrics['algorithm'] == 'deadline', "Metrics show wrong algorithm"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_io_priority_inheritance():
    """Test IOPriorityInheritance functionality"""
    print("\n=== Testing IOPriorityInheritance ===")
    try:
        from optimusprime import IOPriorityInheritance
        
        ipi = IOPriorityInheritance(MockHandleCache())
        print("✓ Instantiated IOPriorityInheritance")
        
        # Test enable
        ipi.enable()
        assert ipi.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test priority levels setting
        ipi.set_priority_levels(5)
        assert ipi.priority_levels == 5, "Priority levels setting failed"
        print("✓ Set priority levels works")
        
        # Test priority boosting
        ipi.enable_priority_boosting()
        assert ipi.priority_boosting == True, "Priority boosting failed"
        print("✓ Enable priority boosting works")
        
        # Test inheritance chain configuration
        ipi.configure_inheritance_chain()
        assert len(ipi.inheritance_chain) == 5, "Inheritance chain configuration failed"
        print(f"✓ Configure inheritance chain works: {len(ipi.inheritance_chain)} levels")
        
        # Test metrics
        metrics = ipi.get_metrics()
        assert metrics['priority_boosting'] == True, "Metrics show wrong boosting state"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_optimizer():
    """Test MetadataOptimizer functionality"""
    print("\n=== Testing MetadataOptimizer ===")
    try:
        from optimusprime import MetadataOptimizer
        
        mo = MetadataOptimizer()
        print("✓ Instantiated MetadataOptimizer")
        
        # Test enable
        mo.enable()
        assert mo.enabled == True, "Enable failed"
        print("✓ Enable method works")
        
        # Test optimization level setting
        mo.set_optimization_level('aggressive')
        assert mo.optimization_level == 'aggressive', "Optimization level setting failed"
        print("✓ Set optimization level works")
        
        # Test metadata caching
        mo.enable_metadata_caching()
        assert isinstance(mo.metadata_cache, dict), "Metadata caching failed"
        print("✓ Enable metadata caching works")
        
        # Test metrics
        metrics = mo.get_metrics()
        assert metrics['optimization_level'] == 'aggressive', "Metrics show wrong optimization level"
        print(f"✓ Metrics: {metrics}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("OPTIMIZER ACTIVATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_memory_scrubbing_optimizer,
        test_cache_coherency_optimizer,
        test_memory_bandwidth_manager,
        test_aggressive_write_cache,
        test_custom_io_scheduler,
        test_io_priority_inheritance,
        test_metadata_optimizer
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(0.1)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
