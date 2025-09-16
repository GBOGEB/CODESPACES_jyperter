
"""
Priority Cache System for Artifact Processing
=============================================

Implements local priority cache for frequently accessed artifacts
with LRU eviction and performance optimization.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
import pickle
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheEntry:
    """Individual cache entry with metadata"""
    
    def __init__(self, key: str, data: Any, priority: int = 0):
        self.key = key
        self.data = data
        self.priority = priority
        self.created_time = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.size = self._calculate_size(data)
    
    def _calculate_size(self, data: Any) -> int:
        """Estimate memory size of cached data"""
        try:
            return len(pickle.dumps(data))
        except:
            return len(str(data))
    
    def access(self):
        """Record access to this entry"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def age(self) -> float:
        """Get age of entry in seconds"""
        return time.time() - self.created_time
    
    def time_since_access(self) -> float:
        """Get time since last access in seconds"""
        return time.time() - self.last_accessed

class PriorityCache:
    """
    Priority-based cache with LRU eviction and performance optimization
    """
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100, 
                 ttl_seconds: int = 3600):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0,
            'memory_usage': 0
        }
        
        # Priority queues for different access patterns
        self._high_priority = set()
        self._frequent_access = set()
        
        logger.info(f"Initialized priority cache: max_size={max_size}, "
                   f"max_memory={max_memory_mb}MB, ttl={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                # Check TTL
                if entry.age() > self.ttl_seconds:
                    self._remove_entry(key)
                    self._stats['misses'] += 1
                    return None
                
                # Update access info
                entry.access()
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                
                # Update priority tracking
                self._update_priority_tracking(key, entry)
                
                self._stats['hits'] += 1
                return entry.data
            
            self._stats['misses'] += 1
            return None
    
    def put(self, key: str, data: Any, priority: int = 0) -> bool:
        """
        Put item in cache
        
        Args:
            key: Cache key
            data: Data to cache
            priority: Priority level (higher = more important)
            
        Returns:
            True if successfully cached
        """
        with self._lock:
            # Create new entry
            entry = CacheEntry(key, data, priority)
            
            # Check if we need to make space
            if not self._make_space_for_entry(entry):
                logger.warning(f"Could not make space for cache entry: {key}")
                return False
            
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Add new entry
            self._cache[key] = entry
            self._stats['size'] += 1
            self._stats['memory_usage'] += entry.size
            
            # Update priority tracking
            if priority > 50:  # High priority threshold
                self._high_priority.add(key)
            
            logger.debug(f"Cached entry: {key} (priority={priority}, size={entry.size})")
            return True
    
    def remove(self, key: str) -> bool:
        """Remove item from cache"""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._high_priority.clear()
            self._frequent_access.clear()
            self._stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'size': 0,
                'memory_usage': 0
            }
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = 0.0
            total_requests = self._stats['hits'] + self._stats['misses']
            if total_requests > 0:
                hit_rate = self._stats['hits'] / total_requests
            
            return {
                **self._stats,
                'hit_rate': round(hit_rate, 3),
                'memory_usage_mb': round(self._stats['memory_usage'] / (1024 * 1024), 2),
                'high_priority_count': len(self._high_priority),
                'frequent_access_count': len(self._frequent_access)
            }
    
    def get_cache_info(self) -> List[Dict[str, Any]]:
        """Get information about cached entries"""
        with self._lock:
            info = []
            for key, entry in self._cache.items():
                info.append({
                    'key': key,
                    'priority': entry.priority,
                    'size': entry.size,
                    'age': round(entry.age(), 2),
                    'last_accessed': round(entry.time_since_access(), 2),
                    'access_count': entry.access_count,
                    'is_high_priority': key in self._high_priority,
                    'is_frequent': key in self._frequent_access
                })
            
            # Sort by priority and access count
            info.sort(key=lambda x: (x['priority'], x['access_count']), reverse=True)
            return info
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed"""
        with self._lock:
            expired_keys = []
            current_time = time.time()
            
            for key, entry in self._cache.items():
                if current_time - entry.created_time > self.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def _make_space_for_entry(self, new_entry: CacheEntry) -> bool:
        """Make space for new entry by evicting if necessary"""
        # Check size limit
        while len(self._cache) >= self.max_size:
            if not self._evict_lru_entry():
                return False
        
        # Check memory limit
        while (self._stats['memory_usage'] + new_entry.size) > self.max_memory_bytes:
            if not self._evict_lru_entry():
                return False
        
        return True
    
    def _evict_lru_entry(self) -> bool:
        """Evict least recently used entry, considering priority"""
        if not self._cache:
            return False
        
        # Find best candidate for eviction
        eviction_candidate = self._find_eviction_candidate()
        
        if eviction_candidate:
            self._remove_entry(eviction_candidate)
            self._stats['evictions'] += 1
            return True
        
        return False
    
    def _find_eviction_candidate(self) -> Optional[str]:
        """Find best candidate for eviction based on priority and access patterns"""
        candidates = []
        
        for key, entry in self._cache.items():
            # Skip high priority items unless cache is very full
            if key in self._high_priority and len(self._cache) < self.max_size * 0.9:
                continue
            
            # Skip frequently accessed items
            if key in self._frequent_access:
                continue
            
            # Calculate eviction score (lower = better candidate)
            score = self._calculate_eviction_score(entry)
            candidates.append((key, score))
        
        if not candidates:
            # If no candidates, evict oldest entry
            return next(iter(self._cache))
        
        # Sort by eviction score and return best candidate
        candidates.sort(key=lambda x: x[1])
        return candidates[0][0]
    
    def _calculate_eviction_score(self, entry: CacheEntry) -> float:
        """Calculate eviction score for an entry (lower = more likely to evict)"""
        # Base score from priority (higher priority = higher score)
        score = entry.priority
        
        # Boost score based on access frequency
        score += entry.access_count * 10
        
        # Reduce score based on age (older = lower score)
        age_penalty = entry.age() / 3600  # Hours
        score -= age_penalty
        
        # Reduce score based on time since last access
        access_penalty = entry.time_since_access() / 3600  # Hours
        score -= access_penalty * 2
        
        return score
    
    def _remove_entry(self, key: str):
        """Remove entry and update tracking"""
        if key in self._cache:
            entry = self._cache[key]
            del self._cache[key]
            
            self._stats['size'] -= 1
            self._stats['memory_usage'] -= entry.size
            
            # Update priority tracking
            self._high_priority.discard(key)
            self._frequent_access.discard(key)
    
    def _update_priority_tracking(self, key: str, entry: CacheEntry):
        """Update priority tracking based on access patterns"""
        # Mark as frequently accessed if accessed many times
        if entry.access_count > 5:
            self._frequent_access.add(key)
        
        # Remove from frequent access if not accessed recently
        if entry.time_since_access() > 1800:  # 30 minutes
            self._frequent_access.discard(key)
    
    def save_to_disk(self, file_path: str) -> bool:
        """Save cache to disk"""
        try:
            with self._lock:
                cache_data = {
                    'entries': {},
                    'stats': self._stats,
                    'high_priority': list(self._high_priority),
                    'frequent_access': list(self._frequent_access)
                }
                
                # Serialize cache entries
                for key, entry in self._cache.items():
                    cache_data['entries'][key] = {
                        'data': entry.data,
                        'priority': entry.priority,
                        'created_time': entry.created_time,
                        'last_accessed': entry.last_accessed,
                        'access_count': entry.access_count
                    }
                
                with open(file_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                logger.info(f"Cache saved to {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving cache to disk: {e}")
            return False
    
    def load_from_disk(self, file_path: str) -> bool:
        """Load cache from disk"""
        try:
            if not Path(file_path).exists():
                logger.warning(f"Cache file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            with self._lock:
                self.clear()
                
                # Restore entries
                for key, entry_data in cache_data['entries'].items():
                    entry = CacheEntry(key, entry_data['data'], entry_data['priority'])
                    entry.created_time = entry_data['created_time']
                    entry.last_accessed = entry_data['last_accessed']
                    entry.access_count = entry_data['access_count']
                    
                    # Check if entry is still valid (not expired)
                    if entry.age() <= self.ttl_seconds:
                        self._cache[key] = entry
                        self._stats['size'] += 1
                        self._stats['memory_usage'] += entry.size
                
                # Restore priority tracking
                self._high_priority = set(cache_data.get('high_priority', []))
                self._frequent_access = set(cache_data.get('frequent_access', []))
                
                # Update stats (but keep hit/miss counters)
                old_hits = self._stats['hits']
                old_misses = self._stats['misses']
                self._stats.update(cache_data.get('stats', {}))
                self._stats['hits'] = old_hits
                self._stats['misses'] = old_misses
                
                logger.info(f"Cache loaded from {file_path} ({len(self._cache)} entries)")
                return True
                
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")
            return False

class ArtifactCache(PriorityCache):
    """
    Specialized cache for artifact processing with domain-specific optimizations
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Artifact-specific priority mappings
        self.type_priorities = {
            'ZIP': 90,
            'MARKDOWN': 70,
            'WORD': 60,
            'VISIO': 50,
            'PDF': 40,
            'POWERPOINT': 30
        }
    
    def cache_artifact(self, artifact_data: Dict[str, Any]) -> bool:
        """
        Cache artifact with automatic priority assignment
        
        Args:
            artifact_data: Artifact data dictionary
            
        Returns:
            True if successfully cached
        """
        file_path = artifact_data.get('file_path', '')
        artifact_type = artifact_data.get('artifact_type', 'UNKNOWN')
        
        # Calculate priority
        base_priority = self.type_priorities.get(artifact_type, 10)
        
        # Boost priority for certain characteristics
        metadata = artifact_data.get('metadata', {})
        if metadata.get('has_code', False):
            base_priority += 20
        if metadata.get('has_docs', False):
            base_priority += 10
        if 'readme' in file_path.lower():
            base_priority += 15
        
        # Create cache key
        cache_key = self._create_artifact_key(artifact_data)
        
        return self.put(cache_key, artifact_data, base_priority)
    
    def get_artifact(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached artifact by file path"""
        cache_key = f"artifact:{file_path}"
        return self.get(cache_key)
    
    def _create_artifact_key(self, artifact_data: Dict[str, Any]) -> str:
        """Create cache key for artifact"""
        file_path = artifact_data.get('file_path', '')
        return f"artifact:{file_path}"
