
"""
Artifact Indexing System with SQL-like Querying
===============================================

Provides full-text search indexing using SQLite FTS5 with ranking capabilities.
Supports SQL-like queries for heterogeneous artifact collections.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ArtifactIndexer:
    """
    Enhanced artifact indexer with FTS5 and SQL-like querying capabilities
    """
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with FTS5 tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create main artifacts table
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    file_size INTEGER,
                    modified_time REAL,
                    indexed_time REAL,
                    content_hash TEXT,
                    metadata TEXT,
                    priority INTEGER DEFAULT 0,
                    processing_status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Create FTS5 virtual table for full-text search
            self.conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(
                    file_path,
                    file_name,
                    artifact_type,
                    content,
                    metadata_text,
                    tokenize='porter unicode61'
                )
            ''')
            
            # Create indexes for performance
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_artifact_type ON artifacts(artifact_type)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_priority ON artifacts(priority DESC)')
            self.conn.execute('CREATE INDEX IF NOT EXISTS idx_modified_time ON artifacts(modified_time DESC)')
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def index_artifact(self, file_path: str, artifact_type: str, 
                      metadata: Dict[str, Any], content: str = "") -> bool:
        """
        Index a single artifact with metadata and content
        
        Args:
            file_path: Path to the artifact file
            artifact_type: Type of artifact (ZIP, WORD, etc.)
            metadata: Artifact metadata dictionary
            content: Extracted text content
            
        Returns:
            True if indexing successful
        """
        try:
            path = Path(file_path)
            
            # Calculate content hash
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Prepare metadata as JSON
            metadata_json = json.dumps(metadata, default=str)
            metadata_text = self._extract_searchable_metadata(metadata)
            
            # Insert or update artifact
            self.conn.execute('''
                INSERT OR REPLACE INTO artifacts 
                (file_path, file_name, artifact_type, file_size, modified_time, 
                 indexed_time, content_hash, metadata, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(path.absolute()),
                path.name,
                artifact_type,
                metadata.get('file_size', 0),
                metadata.get('modified_time', 0),
                datetime.now().timestamp(),
                content_hash,
                metadata_json,
                metadata.get('priority', 0)
            ))
            
            # Insert into FTS table
            self.conn.execute('''
                INSERT OR REPLACE INTO artifacts_fts 
                (file_path, file_name, artifact_type, content, metadata_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(path.absolute()), path.name, artifact_type, content, metadata_text))
            
            self.conn.commit()
            logger.debug(f"Indexed artifact: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing artifact {file_path}: {e}")
            return False
    
    def search(self, query: str, artifact_types: Optional[List[str]] = None,
              limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search artifacts using FTS5 with ranking
        
        Args:
            query: Search query (supports FTS5 syntax)
            artifact_types: Filter by artifact types
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            List of matching artifacts with relevance scores
        """
        try:
            # Build query with filters
            where_clauses = []
            params = [query]
            
            if artifact_types:
                placeholders = ','.join(['?' for _ in artifact_types])
                where_clauses.append(f"a.artifact_type IN ({placeholders})")
                params.extend(artifact_types)
            
            where_clause = ""
            if where_clauses:
                where_clause = "AND " + " AND ".join(where_clauses)
            
            sql = f'''
                SELECT 
                    a.*,
                    bm25(artifacts_fts) as relevance_score,
                    highlight(artifacts_fts, 3, '<mark>', '</mark>') as highlighted_content
                FROM artifacts_fts
                JOIN artifacts a ON a.file_path = artifacts_fts.file_path
                WHERE artifacts_fts MATCH ?
                {where_clause}
                ORDER BY bm25(artifacts_fts), a.priority DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            
            cursor = self.conn.execute(sql, params)
            results = []
            
            for row in cursor.fetchall():
                result = dict(row)
                # Parse metadata JSON
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching artifacts: {e}")
            return []
    
    def sql_query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute custom SQL query on artifacts
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            cursor = self.conn.execute(sql, params or ())
            results = []
            
            for row in cursor.fetchall():
                result = dict(row)
                # Parse metadata if present
                if 'metadata' in result and result['metadata']:
                    try:
                        result['metadata'] = json.loads(result['metadata'])
                    except:
                        pass
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            stats = {}
            
            # Total artifacts
            cursor = self.conn.execute('SELECT COUNT(*) as total FROM artifacts')
            stats['total_artifacts'] = cursor.fetchone()['total']
            
            # By artifact type
            cursor = self.conn.execute('''
                SELECT artifact_type, COUNT(*) as count 
                FROM artifacts 
                GROUP BY artifact_type
                ORDER BY count DESC
            ''')
            stats['by_type'] = {row['artifact_type']: row['count'] for row in cursor.fetchall()}
            
            # By priority
            cursor = self.conn.execute('''
                SELECT priority, COUNT(*) as count 
                FROM artifacts 
                GROUP BY priority
                ORDER BY priority
            ''')
            stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
            
            # Total size
            cursor = self.conn.execute('SELECT SUM(file_size) as total_size FROM artifacts')
            stats['total_size'] = cursor.fetchone()['total_size'] or 0
            
            # Recent activity
            cursor = self.conn.execute('''
                SELECT COUNT(*) as recent_count 
                FROM artifacts 
                WHERE indexed_time > ?
            ''', (datetime.now().timestamp() - 86400,))  # Last 24 hours
            stats['indexed_last_24h'] = cursor.fetchone()['recent_count']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_artifact_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get artifact by file path"""
        try:
            cursor = self.conn.execute('''
                SELECT * FROM artifacts WHERE file_path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting artifact by path: {e}")
            return None
    
    def update_processing_status(self, file_path: str, status: str) -> bool:
        """Update processing status for an artifact"""
        try:
            self.conn.execute('''
                UPDATE artifacts 
                SET processing_status = ?
                WHERE file_path = ?
            ''', (status, file_path))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating processing status: {e}")
            return False
    
    def _extract_searchable_metadata(self, metadata: Dict[str, Any]) -> str:
        """Extract searchable text from metadata"""
        searchable_parts = []
        
        # Add common searchable fields
        for key in ['title', 'author', 'subject', 'keywords', 'description']:
            if key in metadata and metadata[key]:
                searchable_parts.append(str(metadata[key]))
        
        # Add file-specific metadata
        if 'python_files' in metadata:
            searchable_parts.extend(metadata['python_files'])
        
        if 'markdown_files' in metadata:
            searchable_parts.extend(metadata['markdown_files'])
        
        return " ".join(searchable_parts)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
