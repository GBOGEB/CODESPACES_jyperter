"""
Basic functionality tests for DMAIC Measure Phase
"""

import pytest
import tempfile
import os
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from measure_phase import ArtifactClassifier, ArtifactIndexer, ArtifactRanker, PriorityCache

class TestBasicFunctionality:
    """Test basic functionality of the DMAIC Measure Phase system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = {}
        
        # Create test files
        test_content = {
            'test.md': '# Test Markdown\nThis is a test markdown file.',
            'test.txt': 'This is a plain text file for testing.',
            'README.md': '# Project README\nThis is the main documentation.'
        }
        
        for filename, content in test_content.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            self.test_files[filename] = file_path
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_artifact_classifier(self):
        """Test artifact classification"""
        classifier = ArtifactClassifier()
        
        # Test single file classification
        md_file = self.test_files['test.md']
        artifact_type, metadata = classifier.classify_file(md_file)
        
        assert artifact_type.name == 'MARKDOWN'
        assert metadata['file_name'] == 'test.md'
        assert metadata['extension'] == '.md'
        assert metadata['priority'] == 2  # MARKDOWN priority
    
    def test_artifact_indexer(self):
        """Test artifact indexing"""
        indexer = ArtifactIndexer(':memory:')
        
        try:
            # Test indexing
            success = indexer.index_artifact(
                self.test_files['test.md'],
                'MARKDOWN',
                {'file_name': 'test.md', 'file_size': 100},
                'Test markdown content'
            )
            
            assert success == True
            
            # Test search
            results = indexer.search('test')
            assert len(results) > 0
            
            # Test statistics
            stats = indexer.get_statistics()
            assert stats['total_artifacts'] == 1
            
        finally:
            indexer.close()
    
    def test_artifact_ranker(self):
        """Test artifact ranking"""
        ranker = ArtifactRanker()
        
        # Create test artifacts
        artifacts = [
            {
                'file_path': self.test_files['test.md'],
                'artifact_type': 'MARKDOWN',
                'file_size': 100,
                'metadata': {'word_count': 50}
            },
            {
                'file_path': self.test_files['README.md'],
                'artifact_type': 'MARKDOWN', 
                'file_size': 200,
                'metadata': {'word_count': 100}
            }
        ]
        
        # Test ranking
        ranked = ranker.rank_all_dimensions(artifacts)
        
        assert len(ranked) == 2
        assert all('total_rank' in artifact for artifact in ranked)
        assert all('self_rank' in artifact for artifact in ranked)
    
    def test_priority_cache(self):
        """Test priority cache functionality"""
        cache = PriorityCache(max_size=10)
        
        # Test put and get
        test_data = {'test': 'data'}
        success = cache.put('test_key', test_data, priority=50)
        assert success == True
        
        retrieved = cache.get('test_key')
        assert retrieved == test_data
        
        # Test cache miss
        missing = cache.get('nonexistent_key')
        assert missing is None
        
        # Test statistics
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1

if __name__ == '__main__':
    pytest.main([__file__])
