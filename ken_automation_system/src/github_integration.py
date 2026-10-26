#!/usr/bin/env python3
"""
GitHub Integration Module for MASTER.docx Automation
Handles PAT authentication, repository operations, PR generation, and sync workflows
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import tempfile
import zipfile

from github import Github, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.ContentFile import ContentFile
import requests

logger = logging.getLogger(__name__)

class GitHubIntegrationError(Exception):
    """Custom exception for GitHub integration errors"""
    pass

class GitHubIntegrator:
    """Handles all GitHub operations for the MASTER automation pipeline"""
    
    def __init__(self, token: str, repo_name: str, base_branch: str = "main"):
        """
        Initialize GitHub integrator
        
        Args:
            token: GitHub Personal Access Token
            repo_name: Repository name in format "owner/repo"
            base_branch: Base branch for operations
        """
        self.token = token
        self.repo_name = repo_name
        self.base_branch = base_branch
        
        try:
            self.github = Github(token)
            self.repo = self.github.get_repo(repo_name)
            logger.info(f"Connected to GitHub repository: {repo_name}")
        except GithubException as e:
            raise GitHubIntegrationError(f"Failed to connect to GitHub: {str(e)}")
    
    async def sync_documents(self, documents: Dict[str, Any], branch_name: str = None) -> Dict[str, Any]:
        """
        Sync documents with GitHub repository
        
        Args:
            documents: Dictionary of documents to sync
            branch_name: Target branch name (auto-generated if None)
        
        Returns:
            Dictionary with sync results
        """
        if not branch_name:
            branch_name = f"master-sync-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        logger.info(f"Syncing documents to branch: {branch_name}")
        
        sync_result = {
            'branch_name': branch_name,
            'files_updated': [],
            'files_created': [],
            'files_deleted': [],
            'commit_sha': None,
            'pull_request': None
        }
        
        try:
            # Create new branch
            base_ref = self.repo.get_git_ref(f"heads/{self.base_branch}")
            self.repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.object.sha)
            
            # Process each document
            for doc_type, doc_data in documents.items():
                if isinstance(doc_data, list):
                    for i, doc in enumerate(doc_data):
                        file_path = f"docs/{doc_type}/{doc_type}_{i}.json"
                        await self._update_file_in_repo(file_path, json.dumps(doc, indent=2), branch_name, sync_result)
                else:
                    file_path = f"docs/{doc_type}/{doc_type}.json"
                    await self._update_file_in_repo(file_path, json.dumps(doc_data, indent=2), branch_name, sync_result)
            
            # Create pull request
            pr = await self._create_pull_request(branch_name, documents)
            sync_result['pull_request'] = {
                'number': pr.number,
                'url': pr.html_url,
                'title': pr.title
            }
            
            logger.info(f"Sync completed. PR created: {pr.html_url}")
            
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            raise GitHubIntegrationError(f"Document sync failed: {str(e)}")
        
        return sync_result
    
    async def _update_file_in_repo(self, file_path: str, content: str, branch_name: str, sync_result: Dict[str, Any]):
        """Update or create file in repository"""
        try:
            # Try to get existing file
            try:
                existing_file = self.repo.get_contents(file_path, ref=branch_name)
                # Update existing file
                self.repo.update_file(
                    path=file_path,
                    message=f"Update {file_path}",
                    content=content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
                sync_result['files_updated'].append(file_path)
                logger.debug(f"Updated file: {file_path}")
                
            except GithubException as e:
                if e.status == 404:
                    # Create new file
                    self.repo.create_file(
                        path=file_path,
                        message=f"Create {file_path}",
                        content=content,
                        branch=branch_name
                    )
                    sync_result['files_created'].append(file_path)
                    logger.debug(f"Created file: {file_path}")
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to update file {file_path}: {str(e)}")
            raise
    
    async def _create_pull_request(self, branch_name: str, documents: Dict[str, Any]) -> PullRequest:
        """Create pull request for document updates"""
        title = f"MASTER Document Sync - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        body = self._generate_pr_description(documents)
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=self.base_branch
            )
            
            # Add labels
            pr.add_to_labels("documentation", "automated", "master-sync")
            
            return pr
            
        except GithubException as e:
            logger.error(f"Failed to create pull request: {str(e)}")
            raise GitHubIntegrationError(f"PR creation failed: {str(e)}")
    
    def _generate_pr_description(self, documents: Dict[str, Any]) -> str:
        """Generate pull request description"""
        description = """# MASTER Document Automation Sync

This PR contains automated updates to the MASTER document system.

## Changes Summary

"""
        
        for doc_type, doc_data in documents.items():
            if isinstance(doc_data, list):
                description += f"- **{doc_type.upper()}**: {len(doc_data)} files updated\n"
            else:
                description += f"- **{doc_type.upper()}**: 1 file updated\n"
        
        description += f"""
## Automation Details

- **Timestamp**: {datetime.now().isoformat()}
- **Pipeline Version**: 1.0
- **Processing Stage**: Automated sync

## Validation

- [ ] Document structure validated
- [ ] Cross-references verified
- [ ] Compliance checks passed
- [ ] DMAIC stage completed

## Next Steps

1. Review changes
2. Run validation tests
3. Merge if approved
4. Deploy to production

---
*This PR was generated automatically by the MASTER Document Automation Pipeline*
"""
        
        return description
    
    async def download_repository_content(self, target_path: str = "temp/repo_content") -> Dict[str, Any]:
        """Download repository content for processing"""
        logger.info("Downloading repository content")
        
        download_result = {
            'target_path': target_path,
            'files_downloaded': [],
            'total_size': 0
        }
        
        try:
            # Create target directory
            Path(target_path).mkdir(parents=True, exist_ok=True)
            
            # Get repository contents recursively
            contents = self.repo.get_contents("")
            
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(self.repo.get_contents(file_content.path))
                else:
                    # Download file
                    file_path = Path(target_path) / file_content.path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Decode and save file content
                    if file_content.encoding == "base64":
                        content = base64.b64decode(file_content.content)
                        with open(file_path, 'wb') as f:
                            f.write(content)
                    else:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(file_content.decoded_content.decode('utf-8'))
                    
                    download_result['files_downloaded'].append(str(file_path))
                    download_result['total_size'] += file_content.size
            
            logger.info(f"Downloaded {len(download_result['files_downloaded'])} files")
            
        except Exception as e:
            logger.error(f"Repository download failed: {str(e)}")
            raise GitHubIntegrationError(f"Download failed: {str(e)}")
        
        return download_result
    
    async def create_release(self, version: str, documents: Dict[str, Any], changelog: str = None) -> Dict[str, Any]:
        """Create a GitHub release with document artifacts"""
        logger.info(f"Creating release: {version}")
        
        release_result = {
            'version': version,
            'tag_name': f"v{version}",
            'release_url': None,
            'assets': []
        }
        
        try:
            # Create release
            release_name = f"MASTER Document Release v{version}"
            release_body = changelog or self._generate_release_notes(documents)
            
            release = self.repo.create_git_release(
                tag=release_result['tag_name'],
                name=release_name,
                message=release_body,
                draft=False,
                prerelease=False
            )
            
            release_result['release_url'] = release.html_url
            
            # Create and upload artifacts
            artifacts = await self._create_release_artifacts(documents)
            
            for artifact_name, artifact_content in artifacts.items():
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as temp_file:
                    temp_file.write(artifact_content)
                    temp_file_path = temp_file.name
                
                try:
                    # Upload asset
                    with open(temp_file_path, 'rb') as asset_file:
                        release.upload_asset(
                            path=temp_file_path,
                            name=artifact_name,
                            content_type='application/zip'
                        )
                    
                    release_result['assets'].append(artifact_name)
                    
                finally:
                    # Clean up temporary file
                    os.unlink(temp_file_path)
            
            logger.info(f"Release created: {release.html_url}")
            
        except Exception as e:
            logger.error(f"Release creation failed: {str(e)}")
            raise GitHubIntegrationError(f"Release creation failed: {str(e)}")
        
        return release_result
    
    def _generate_release_notes(self, documents: Dict[str, Any]) -> str:
        """Generate release notes"""
        notes = f"""# MASTER Document Release

## Release Information

- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Pipeline Version**: 1.0
- **Documents Processed**: {len(documents)}

## Document Summary

"""
        
        for doc_type, doc_data in documents.items():
            if isinstance(doc_data, list):
                notes += f"- **{doc_type.upper()}**: {len(doc_data)} documents\n"
            else:
                notes += f"- **{doc_type.upper()}**: 1 document\n"
        
        notes += """
## Features

- Automated document processing
- Cross-reference validation
- Compliance tracking
- DMAIC methodology integration

## Artifacts

This release includes processed documents and validation reports.

---
*Generated by MASTER Document Automation Pipeline*
"""
        
        return notes
    
    async def _create_release_artifacts(self, documents: Dict[str, Any]) -> Dict[str, str]:
        """Create release artifacts"""
        artifacts = {}
        
        # Create document bundle
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(documents, temp_file, indent=2, default=str)
            temp_file_path = temp_file.name
        
        # Create ZIP archive
        zip_path = temp_file_path.replace('.json', '.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_file_path, 'documents.json')
        
        with open(zip_path, 'r', encoding='latin1') as f:
            artifacts['master_documents.zip'] = f.read()
        
        # Clean up
        os.unlink(temp_file_path)
        os.unlink(zip_path)
        
        return artifacts
    
    async def setup_webhooks(self, webhook_url: str, events: List[str] = None) -> Dict[str, Any]:
        """Setup GitHub webhooks for automation triggers"""
        if not events:
            events = ["push", "pull_request", "release"]
        
        logger.info(f"Setting up webhooks for events: {events}")
        
        webhook_config = {
            "url": webhook_url,
            "content_type": "json",
            "insecure_ssl": "0"
        }
        
        try:
            webhook = self.repo.create_hook(
                name="web",
                config=webhook_config,
                events=events,
                active=True
            )
            
            return {
                'webhook_id': webhook.id,
                'url': webhook_url,
                'events': events,
                'active': webhook.active
            }
            
        except GithubException as e:
            logger.error(f"Webhook setup failed: {str(e)}")
            raise GitHubIntegrationError(f"Webhook setup failed: {str(e)}")
    
    async def get_repository_metrics(self) -> Dict[str, Any]:
        """Get repository metrics for monitoring"""
        try:
            metrics = {
                'repository': {
                    'name': self.repo.name,
                    'full_name': self.repo.full_name,
                    'private': self.repo.private,
                    'size': self.repo.size,
                    'language': self.repo.language
                },
                'activity': {
                    'commits_count': self.repo.get_commits().totalCount,
                    'branches_count': len(list(self.repo.get_branches())),
                    'tags_count': len(list(self.repo.get_tags())),
                    'releases_count': len(list(self.repo.get_releases()))
                },
                'collaboration': {
                    'contributors_count': self.repo.get_contributors().totalCount,
                    'forks_count': self.repo.forks_count,
                    'watchers_count': self.repo.watchers_count,
                    'stars_count': self.repo.stargazers_count
                },
                'issues': {
                    'open_issues': self.repo.open_issues_count,
                    'open_prs': len([pr for pr in self.repo.get_pulls(state='open')])
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get repository metrics: {str(e)}")
            raise GitHubIntegrationError(f"Metrics collection failed: {str(e)}")

class GitHubWorkflowManager:
    """Manages GitHub Actions workflows for automation"""
    
    def __init__(self, integrator: GitHubIntegrator):
        self.integrator = integrator
        self.repo = integrator.repo
    
    async def create_automation_workflow(self) -> str:
        """Create GitHub Actions workflow for MASTER automation"""
        workflow_content = """name: MASTER Document Automation

on:
  push:
    branches: [ main, develop ]
    paths: 
      - 'docs/**'
      - 'master/**'
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM
  workflow_dispatch:

jobs:
  process-documents:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run MASTER automation pipeline
      run: |
        python src/master_automation_pipeline.py
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: automation-results
        path: output/
    
    - name: Create PR if changes
      if: github.event_name == 'schedule'
      run: |
        if [[ -n $(git status --porcelain) ]]; then
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Automated MASTER document updates"
          git push origin HEAD:automated-updates-$(date +%Y%m%d-%H%M%S)
        fi

  validate-compliance:
    needs: process-documents
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download automation results
      uses: actions/download-artifact@v3
      with:
        name: automation-results
        path: output/
    
    - name: Run compliance validation
      run: |
        python src/validate_compliance.py output/
    
    - name: Generate compliance report
      run: |
        python src/generate_compliance_report.py
    
    - name: Upload compliance report
      uses: actions/upload-artifact@v3
      with:
        name: compliance-report
        path: output/compliance_report.pdf
"""
        
        return workflow_content
    
    async def setup_workflow_file(self) -> Dict[str, Any]:
        """Setup the workflow file in the repository"""
        workflow_path = ".github/workflows/master-automation.yml"
        workflow_content = await self.create_automation_workflow()
        
        try:
            # Check if workflow already exists
            try:
                existing_file = self.repo.get_contents(workflow_path)
                # Update existing workflow
                self.repo.update_file(
                    path=workflow_path,
                    message="Update MASTER automation workflow",
                    content=workflow_content,
                    sha=existing_file.sha
                )
                action = "updated"
            except:
                # Create new workflow
                self.repo.create_file(
                    path=workflow_path,
                    message="Add MASTER automation workflow",
                    content=workflow_content
                )
                action = "created"
            
            return {
                'workflow_path': workflow_path,
                'action': action,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Workflow setup failed: {str(e)}")
            raise GitHubIntegrationError(f"Workflow setup failed: {str(e)}")

# Utility functions
def validate_github_token(token: str) -> bool:
    """Validate GitHub token"""
    try:
        g = Github(token)
        g.get_user().login
        return True
    except:
        return False

def setup_github_integration(config: Dict[str, Any]) -> GitHubIntegrator:
    """Setup GitHub integration from configuration"""
    github_config = config.get('github', {})
    
    token = github_config.get('token') or os.getenv('GITHUB_TOKEN')
    repo_name = github_config.get('repo')
    base_branch = github_config.get('branch', 'main')
    
    if not token:
        raise GitHubIntegrationError("GitHub token not provided")
    
    if not repo_name:
        raise GitHubIntegrationError("Repository name not provided")
    
    if not validate_github_token(token):
        raise GitHubIntegrationError("Invalid GitHub token")
    
    return GitHubIntegrator(token, repo_name, base_branch)

async def main():
    """Test GitHub integration"""
    # This would be used for testing the integration
    pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())