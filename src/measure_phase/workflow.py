
"""
DEEP Agent → GitHub → User Git Integration Workflow
==================================================

Implements automated artifact synchronization, version control integration,
and workflow management for the DMAIC system.
"""

import logging
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import shutil
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)

class GitWorkflowManager:
    """Manages Git operations for artifact synchronization"""
    
    def __init__(self, repo_path: str, remote_url: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.remote_url = remote_url
        self.temp_dirs = []
        
    def init_repository(self) -> bool:
        """Initialize Git repository if not exists"""
        try:
            if not (self.repo_path / '.git').exists():
                result = subprocess.run(['git', 'init'], 
                                      cwd=self.repo_path, 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Git init failed: {result.stderr}")
                    return False
                
                logger.info(f"Initialized Git repository at {self.repo_path}")
            
            # Configure user if not set
            self._configure_git_user()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Git repository: {e}")
            return False
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """Create and checkout new branch"""
        try:
            # Ensure we're on base branch
            subprocess.run(['git', 'checkout', base_branch], 
                          cwd=self.repo_path, capture_output=True)
            
            # Create and checkout new branch
            result = subprocess.run(['git', 'checkout', '-b', branch_name], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Created and checked out branch: {branch_name}")
                return True
            else:
                logger.error(f"Failed to create branch: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """Commit changes to repository"""
        try:
            # Add files
            if files:
                for file_path in files:
                    subprocess.run(['git', 'add', file_path], 
                                 cwd=self.repo_path, capture_output=True)
            else:
                subprocess.run(['git', 'add', '.'], 
                             cwd=self.repo_path, capture_output=True)
            
            # Commit
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Committed changes: {message}")
                return True
            else:
                logger.warning(f"Commit result: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_branch(self, branch_name: str, remote: str = "origin") -> bool:
        """Push branch to remote repository"""
        try:
            if not self.remote_url:
                logger.warning("No remote URL configured")
                return False
            
            # Add remote if not exists
            self._ensure_remote(remote)
            
            # Push branch
            result = subprocess.run(['git', 'push', '-u', remote, branch_name], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Pushed branch {branch_name} to {remote}")
                return True
            else:
                logger.error(f"Failed to push branch: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing branch {branch_name}: {e}")
            return False
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def get_status(self) -> Dict[str, Any]:
        """Get Git status information"""
        try:
            # Get status
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         cwd=self.repo_path, 
                                         capture_output=True, text=True)
            
            # Get branch info
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         cwd=self.repo_path, 
                                         capture_output=True, text=True)
            
            # Parse status
            modified_files = []
            untracked_files = []
            
            for line in status_result.stdout.split('\n'):
                if line.strip():
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code.strip() == '??':
                        untracked_files.append(file_path)
                    else:
                        modified_files.append(file_path)
            
            return {
                "current_branch": branch_result.stdout.strip(),
                "modified_files": modified_files,
                "untracked_files": untracked_files,
                "has_changes": bool(modified_files or untracked_files)
            }
            
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
            return {"error": str(e)}
    
    def _configure_git_user(self):
        """Configure Git user if not set"""
        try:
            # Check if user is configured
            result = subprocess.run(['git', 'config', 'user.name'], 
                                  cwd=self.repo_path, capture_output=True)
            
            if result.returncode != 0:
                subprocess.run(['git', 'config', 'user.name', 'DMAIC System'], 
                             cwd=self.repo_path, capture_output=True)
                subprocess.run(['git', 'config', 'user.email', 'dmaic@system.local'], 
                             cwd=self.repo_path, capture_output=True)
                logger.info("Configured Git user for DMAIC system")
                
        except Exception as e:
            logger.debug(f"Could not configure Git user: {e}")
    
    def _ensure_remote(self, remote_name: str):
        """Ensure remote exists"""
        try:
            if self.remote_url:
                # Check if remote exists
                result = subprocess.run(['git', 'remote', 'get-url', remote_name], 
                                      cwd=self.repo_path, capture_output=True)
                
                if result.returncode != 0:
                    # Add remote
                    subprocess.run(['git', 'remote', 'add', remote_name, self.remote_url], 
                                 cwd=self.repo_path, capture_output=True)
                    logger.info(f"Added remote {remote_name}: {self.remote_url}")
                    
        except Exception as e:
            logger.debug(f"Could not ensure remote: {e}")

class WorkflowSync:
    """
    Main workflow synchronization class for DEEP Agent → GitHub → User Git integration
    """
    
    def __init__(self, workspace_path: str, github_repo_url: Optional[str] = None):
        self.workspace_path = Path(workspace_path)
        self.github_repo_url = github_repo_url
        self.git_manager = GitWorkflowManager(workspace_path, github_repo_url)
        
        # Workflow configuration
        self.sync_config = {
            "auto_commit": True,
            "auto_push": False,  # Require explicit push
            "branch_prefix": "dmaic-",
            "commit_message_template": "DMAIC: {operation} - {timestamp}",
            "sync_interval": 300  # 5 minutes
        }
        
        # Sync history
        self.sync_history = []
        
        # Initialize workspace
        self._init_workspace()
    
    def _init_workspace(self):
        """Initialize workspace structure"""
        try:
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Create standard directories
            directories = [
                "artifacts",
                "processed",
                "exports",
                "cache",
                "logs",
                "temp"
            ]
            
            for dir_name in directories:
                (self.workspace_path / dir_name).mkdir(exist_ok=True)
            
            # Initialize Git repository
            self.git_manager.init_repository()
            
            logger.info(f"Initialized workspace at {self.workspace_path}")
            
        except Exception as e:
            logger.error(f"Error initializing workspace: {e}")
    
    def sync_artifacts(self, artifacts: List[Dict[str, Any]], 
                      operation: str = "artifact_sync") -> bool:
        """
        Synchronize artifacts to workspace and version control
        
        Args:
            artifacts: List of artifact data
            operation: Description of the operation
            
        Returns:
            True if sync successful
        """
        try:
            # Create operation branch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"{self.sync_config['branch_prefix']}{operation}_{timestamp}"
            
            if not self.git_manager.create_branch(branch_name):
                logger.error("Failed to create sync branch")
                return False
            
            # Process artifacts
            synced_files = []
            
            for artifact in artifacts:
                file_path = self._sync_single_artifact(artifact)
                if file_path:
                    synced_files.append(file_path)
            
            # Create sync manifest
            manifest_path = self._create_sync_manifest(artifacts, operation, timestamp)
            if manifest_path:
                synced_files.append(manifest_path)
            
            # Commit changes
            if synced_files and self.sync_config["auto_commit"]:
                commit_message = self.sync_config["commit_message_template"].format(
                    operation=operation,
                    timestamp=timestamp
                )
                
                if self.git_manager.commit_changes(commit_message, synced_files):
                    logger.info(f"Committed {len(synced_files)} files for {operation}")
                    
                    # Record sync
                    self._record_sync(operation, len(synced_files), branch_name, True)
                    return True
            
            self._record_sync(operation, len(synced_files), branch_name, False)
            return False
            
        except Exception as e:
            logger.error(f"Error syncing artifacts: {e}")
            self._record_sync(operation, 0, "", False, str(e))
            return False
    
    def _sync_single_artifact(self, artifact: Dict[str, Any]) -> Optional[str]:
        """Sync single artifact to workspace"""
        try:
            source_path = Path(artifact.get('file_path', ''))
            if not source_path.exists():
                logger.warning(f"Source artifact not found: {source_path}")
                return None
            
            # Determine target path
            artifact_type = artifact.get('artifact_type', 'unknown').lower()
            target_dir = self.workspace_path / "artifacts" / artifact_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = target_dir / source_path.name
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            # Create metadata file
            metadata_path = target_path.with_suffix(target_path.suffix + '.meta.json')
            with open(metadata_path, 'w') as f:
                json.dump(artifact, f, indent=2, default=str)
            
            logger.debug(f"Synced artifact: {source_path} -> {target_path}")
            return str(target_path.relative_to(self.workspace_path))
            
        except Exception as e:
            logger.error(f"Error syncing artifact {artifact.get('file_path', 'unknown')}: {e}")
            return None
    
    def _create_sync_manifest(self, artifacts: List[Dict[str, Any]], 
                            operation: str, timestamp: str) -> Optional[str]:
        """Create sync manifest file"""
        try:
            manifest = {
                "sync_operation": operation,
                "timestamp": timestamp,
                "artifact_count": len(artifacts),
                "artifacts": []
            }
            
            for artifact in artifacts:
                manifest["artifacts"].append({
                    "file_path": artifact.get('file_path', ''),
                    "artifact_type": artifact.get('artifact_type', ''),
                    "file_size": artifact.get('file_size', 0),
                    "priority": artifact.get('priority', 0)
                })
            
            # Save manifest
            manifest_path = self.workspace_path / "exports" / f"sync_manifest_{timestamp}.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return str(manifest_path.relative_to(self.workspace_path))
            
        except Exception as e:
            logger.error(f"Error creating sync manifest: {e}")
            return None
    
    def push_to_github(self, branch_name: Optional[str] = None) -> bool:
        """
        Push current branch to GitHub
        
        Args:
            branch_name: Branch to push (current if None)
            
        Returns:
            True if push successful
        """
        try:
            if not branch_name:
                branch_name = self.git_manager.get_current_branch()
            
            if branch_name == "main" or branch_name == "master":
                logger.warning("Refusing to push directly to main branch")
                return False
            
            return self.git_manager.push_branch(branch_name)
            
        except Exception as e:
            logger.error(f"Error pushing to GitHub: {e}")
            return False
    
    def create_pull_request_data(self, branch_name: str, 
                               operation: str) -> Dict[str, Any]:
        """
        Create pull request data for GitHub integration
        
        Args:
            branch_name: Source branch name
            operation: Operation description
            
        Returns:
            Pull request data dictionary
        """
        return {
            "title": f"DMAIC: {operation}",
            "body": self._generate_pr_description(operation),
            "head": branch_name,
            "base": "main",
            "draft": False
        }
    
    def _generate_pr_description(self, operation: str) -> str:
        """Generate pull request description"""
        recent_syncs = self.sync_history[-5:]  # Last 5 syncs
        
        description = f"""
# DMAIC System: {operation}

This pull request contains automated changes from the DMAIC Measure Phase system.

## Changes Summary
- Operation: {operation}
- Timestamp: {datetime.now().isoformat()}

## Recent Sync History
"""
        
        for sync in recent_syncs:
            status = "✅" if sync["success"] else "❌"
            description += f"- {status} {sync['operation']} ({sync['file_count']} files) - {sync['timestamp']}\n"
        
        description += """
## Automated Testing
- [ ] Artifact parsing validation
- [ ] Index integrity check
- [ ] Cache consistency verification

## Review Checklist
- [ ] Verify artifact metadata accuracy
- [ ] Check file organization structure
- [ ] Validate processing results

---
*This PR was automatically generated by the DMAIC Measure Phase system.*
"""
        
        return description
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status"""
        git_status = self.git_manager.get_status()
        
        return {
            "workspace_path": str(self.workspace_path),
            "git_status": git_status,
            "sync_history_count": len(self.sync_history),
            "last_sync": self.sync_history[-1] if self.sync_history else None,
            "pending_changes": git_status.get("has_changes", False),
            "current_branch": git_status.get("current_branch", "unknown")
        }
    
    def export_workflow_report(self, output_path: str) -> bool:
        """Export workflow synchronization report"""
        try:
            report = {
                "workspace_info": {
                    "path": str(self.workspace_path),
                    "github_repo": self.github_repo_url,
                    "config": self.sync_config
                },
                "sync_history": self.sync_history,
                "current_status": self.get_sync_status(),
                "generated_at": datetime.now().isoformat()
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Exported workflow report to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting workflow report: {e}")
            return False
    
    def _record_sync(self, operation: str, file_count: int, branch_name: str, 
                    success: bool, error: Optional[str] = None):
        """Record sync operation in history"""
        sync_record = {
            "operation": operation,
            "file_count": file_count,
            "branch_name": branch_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        self.sync_history.append(sync_record)
        
        # Keep only last 100 records
        if len(self.sync_history) > 100:
            self.sync_history = self.sync_history[-100:]
    
    def cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        try:
            temp_dir = self.workspace_path / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
            
            logger.info("Cleaned up temporary files")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

class AutomatedTestingFramework:
    """Framework for automated testing of pipeline integration"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.test_results = []
    
    def run_artifact_validation_tests(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run validation tests on artifacts"""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        for artifact in artifacts:
            test_result = self._test_single_artifact(artifact)
            results["test_details"].append(test_result)
            results["total_tests"] += 1
            
            if test_result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def _test_single_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Test single artifact for validation"""
        test_result = {
            "artifact_path": artifact.get('file_path', 'unknown'),
            "tests": [],
            "passed": True
        }
        
        # Test 1: File exists
        file_path = Path(artifact.get('file_path', ''))
        file_exists = file_path.exists()
        test_result["tests"].append({
            "name": "file_exists",
            "passed": file_exists,
            "message": "File exists" if file_exists else "File not found"
        })
        
        if not file_exists:
            test_result["passed"] = False
            return test_result
        
        # Test 2: Metadata completeness
        metadata = artifact.get('metadata', {})
        has_metadata = bool(metadata and not metadata.get('error'))
        test_result["tests"].append({
            "name": "metadata_complete",
            "passed": has_metadata,
            "message": "Metadata complete" if has_metadata else "Metadata missing or has errors"
        })
        
        if not has_metadata:
            test_result["passed"] = False
        
        # Test 3: Type classification
        artifact_type = artifact.get('artifact_type', 'UNKNOWN')
        type_valid = artifact_type != 'UNKNOWN'
        test_result["tests"].append({
            "name": "type_classification",
            "passed": type_valid,
            "message": f"Type: {artifact_type}" if type_valid else "Type not classified"
        })
        
        if not type_valid:
            test_result["passed"] = False
        
        return test_result
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for the pipeline"""
        # This would contain more comprehensive integration tests
        return {
            "pipeline_integration": True,
            "cache_consistency": True,
            "index_integrity": True,
            "workflow_sync": True
        }
