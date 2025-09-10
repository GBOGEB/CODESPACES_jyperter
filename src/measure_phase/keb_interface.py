
"""
[KEB] Pipeline Integration Interface
===================================

Provides callable interface for INPUT/OUTPUT analysis with [KEB] pipeline.
Implements artifact-to-[KEB] mapping system and integration workflows.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class KEBInputOutput:
    """Data structure for [KEB] pipeline INPUT/OUTPUT"""
    
    def __init__(self, input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None):
        self.input_data = input_data
        self.output_data = output_data or {}
        self.processing_metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input": self.input_data,
            "output": self.output_data,
            "metadata": self.processing_metadata
        }

class KEBProcessor(ABC):
    """Abstract base class for [KEB] processors"""
    
    @abstractmethod
    def process(self, input_data: KEBInputOutput) -> KEBInputOutput:
        """Process input through [KEB] pipeline"""
        pass
    
    @abstractmethod
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information and capabilities"""
        pass

class ArtifactKEBProcessor(KEBProcessor):
    """Default artifact processor for [KEB] integration"""
    
    def __init__(self, processor_name: str = "ArtifactProcessor"):
        self.processor_name = processor_name
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0
        }
    
    def process(self, input_data: KEBInputOutput) -> KEBInputOutput:
        """Process artifact data through [KEB] pipeline"""
        try:
            # Extract artifact information
            artifact_data = input_data.input_data
            
            # Perform [KEB] processing simulation
            processed_output = self._simulate_keb_processing(artifact_data)
            
            # Create output
            output = KEBInputOutput(
                input_data=artifact_data,
                output_data=processed_output
            )
            
            output.processing_metadata = {
                "processor": self.processor_name,
                "processing_time": 0.1,  # Simulated
                "status": "success"
            }
            
            self.processing_stats["total_processed"] += 1
            self.processing_stats["successful"] += 1
            
            return output
            
        except Exception as e:
            logger.error(f"Error in [KEB] processing: {e}")
            self.processing_stats["total_processed"] += 1
            self.processing_stats["failed"] += 1
            
            error_output = KEBInputOutput(
                input_data=input_data.input_data,
                output_data={"error": str(e)}
            )
            error_output.processing_metadata = {
                "processor": self.processor_name,
                "status": "error",
                "error_message": str(e)
            }
            
            return error_output
    
    def _simulate_keb_processing(self, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate [KEB] pipeline processing"""
        # This would be replaced with actual [KEB] integration
        
        artifact_type = artifact_data.get('artifact_type', 'UNKNOWN')
        metadata = artifact_data.get('metadata', {})
        
        # Simulate different processing based on artifact type
        if artifact_type == 'ZIP':
            return self._process_zip_for_keb(metadata)
        elif artifact_type == 'MARKDOWN':
            return self._process_markdown_for_keb(metadata)
        elif artifact_type == 'WORD':
            return self._process_word_for_keb(metadata)
        elif artifact_type == 'PDF':
            return self._process_pdf_for_keb(metadata)
        elif artifact_type == 'POWERPOINT':
            return self._process_powerpoint_for_keb(metadata)
        elif artifact_type == 'VISIO':
            return self._process_visio_for_keb(metadata)
        else:
            return {"processed": True, "keb_analysis": "Generic processing"}
    
    def _process_zip_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process ZIP artifact for [KEB] pipeline"""
        return {
            "keb_type": "archive_analysis",
            "code_extraction": metadata.get('has_code', False),
            "documentation_extraction": metadata.get('has_docs', False),
            "file_manifest": metadata.get('file_manifest', []),
            "priority_files": self._identify_priority_files(metadata),
            "keb_recommendations": self._generate_zip_recommendations(metadata)
        }
    
    def _process_markdown_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Markdown artifact for [KEB] pipeline"""
        return {
            "keb_type": "documentation_analysis",
            "structure_analysis": metadata.get('structure_score', 0),
            "content_extraction": {
                "headings": len(metadata.get('headings', [])),
                "links": len(metadata.get('links', [])),
                "code_blocks": len(metadata.get('code_blocks', []))
            },
            "keb_recommendations": self._generate_markdown_recommendations(metadata)
        }
    
    def _process_word_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Word artifact for [KEB] pipeline"""
        return {
            "keb_type": "document_analysis",
            "content_metrics": {
                "word_count": metadata.get('word_count', 0),
                "paragraph_count": metadata.get('paragraph_count', 0),
                "table_count": metadata.get('table_count', 0)
            },
            "document_classification": metadata.get('document_type', 'Unknown'),
            "keb_recommendations": self._generate_word_recommendations(metadata)
        }
    
    def _process_pdf_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process PDF artifact for [KEB] pipeline"""
        return {
            "keb_type": "pdf_analysis",
            "content_metrics": {
                "page_count": metadata.get('page_count', 0),
                "word_count": metadata.get('word_count', 0),
                "images_count": metadata.get('images_count', 0)
            },
            "document_classification": metadata.get('document_type', 'Unknown'),
            "keb_recommendations": self._generate_pdf_recommendations(metadata)
        }
    
    def _process_powerpoint_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process PowerPoint artifact for [KEB] pipeline"""
        return {
            "keb_type": "presentation_analysis",
            "content_metrics": {
                "slide_count": metadata.get('slide_count', 0),
                "total_text_shapes": metadata.get('total_text_shapes', 0),
                "total_images": metadata.get('total_images', 0)
            },
            "presentation_classification": metadata.get('presentation_type', 'Unknown'),
            "keb_recommendations": self._generate_powerpoint_recommendations(metadata)
        }
    
    def _process_visio_for_keb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Visio artifact for [KEB] pipeline"""
        return {
            "keb_type": "diagram_analysis",
            "content_metrics": {
                "total_pages": metadata.get('total_pages', 0),
                "total_shapes": metadata.get('total_shapes', 0),
                "total_connections": metadata.get('total_connections', 0)
            },
            "diagram_classification": metadata.get('diagram_type', 'Unknown'),
            "complexity_score": metadata.get('complexity_score', 0),
            "keb_recommendations": self._generate_visio_recommendations(metadata)
        }
    
    def _identify_priority_files(self, metadata: Dict[str, Any]) -> List[str]:
        """Identify priority files for [KEB] processing"""
        priority_files = []
        
        # Add Python files
        priority_files.extend(metadata.get('python_files', [])[:5])  # Top 5
        
        # Add documentation files
        priority_files.extend(metadata.get('markdown_files', [])[:3])  # Top 3
        
        # Add handover documents
        priority_files.extend(metadata.get('handover_documents', []))
        
        return priority_files
    
    def _generate_zip_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for ZIP files"""
        recommendations = []
        
        if metadata.get('has_code', False):
            recommendations.append("Extract and analyze Python code for integration")
            recommendations.append("Set up automated testing pipeline")
        
        if metadata.get('has_docs', False):
            recommendations.append("Process documentation for knowledge base")
            recommendations.append("Create cross-reference links")
        
        if metadata.get('total_files', 0) > 50:
            recommendations.append("Consider batch processing for large archive")
        
        return recommendations
    
    def _generate_markdown_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for Markdown files"""
        recommendations = []
        
        if metadata.get('document_type') == 'README':
            recommendations.append("Process as primary project documentation")
            recommendations.append("Extract setup and usage instructions")
        
        if len(metadata.get('code_blocks', [])) > 0:
            recommendations.append("Extract code examples for testing")
        
        if len(metadata.get('links', [])) > 10:
            recommendations.append("Validate external links")
            recommendations.append("Create link dependency map")
        
        return recommendations
    
    def _generate_word_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for Word documents"""
        recommendations = []
        
        doc_type = metadata.get('document_type', '')
        
        if 'Requirements' in doc_type:
            recommendations.append("Extract requirements for traceability matrix")
            recommendations.append("Create requirement-to-test mapping")
        
        if 'Manual' in doc_type:
            recommendations.append("Convert to interactive documentation")
            recommendations.append("Extract procedures for automation")
        
        return recommendations
    
    def _generate_pdf_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for PDF files"""
        recommendations = []
        
        if metadata.get('page_count', 0) > 20:
            recommendations.append("Consider OCR for better text extraction")
            recommendations.append("Create searchable index")
        
        if metadata.get('images_count', 0) > 0:
            recommendations.append("Extract and catalog images")
        
        return recommendations
    
    def _generate_powerpoint_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for PowerPoint files"""
        recommendations = []
        
        pres_type = metadata.get('presentation_type', '')
        
        if 'Training' in pres_type:
            recommendations.append("Convert to interactive training module")
            recommendations.append("Extract learning objectives")
        
        if metadata.get('total_images', 0) > 10:
            recommendations.append("Create image gallery")
        
        return recommendations
    
    def _generate_visio_recommendations(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate [KEB] recommendations for Visio files"""
        recommendations = []
        
        diagram_type = metadata.get('diagram_type', '')
        
        if 'Process' in diagram_type:
            recommendations.append("Extract process steps for automation")
            recommendations.append("Create process documentation")
        
        if 'Network' in diagram_type:
            recommendations.append("Extract network topology")
            recommendations.append("Create infrastructure inventory")
        
        return recommendations
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information"""
        return {
            "name": self.processor_name,
            "version": "1.0.0",
            "capabilities": [
                "Artifact analysis",
                "Content extraction",
                "Recommendation generation",
                "Priority identification"
            ],
            "supported_types": ["ZIP", "MARKDOWN", "WORD", "PDF", "POWERPOINT", "VISIO"],
            "statistics": self.processing_stats
        }

class KEBAdapter:
    """
    Main adapter class for [KEB] pipeline integration
    """
    
    def __init__(self):
        self.processors = {}
        self.artifact_mappings = {}
        self.processing_history = []
        
        # Register default processor
        self.register_processor("default", ArtifactKEBProcessor())
    
    def register_processor(self, name: str, processor: KEBProcessor):
        """Register a [KEB] processor"""
        self.processors[name] = processor
        logger.info(f"Registered [KEB] processor: {name}")
    
    def create_artifact_mapping(self, artifact_type: str, processor_name: str):
        """Create mapping between artifact type and processor"""
        self.artifact_mappings[artifact_type] = processor_name
        logger.info(f"Mapped {artifact_type} to processor {processor_name}")
    
    def process_artifact(self, artifact_data: Dict[str, Any], 
                        processor_name: Optional[str] = None) -> KEBInputOutput:
        """
        Process artifact through [KEB] pipeline
        
        Args:
            artifact_data: Artifact data dictionary
            processor_name: Specific processor to use (optional)
            
        Returns:
            [KEB] processing results
        """
        # Determine processor
        if not processor_name:
            artifact_type = artifact_data.get('artifact_type', 'UNKNOWN')
            processor_name = self.artifact_mappings.get(artifact_type, 'default')
        
        if processor_name not in self.processors:
            logger.error(f"Processor {processor_name} not found")
            processor_name = 'default'
        
        processor = self.processors[processor_name]
        
        # Create input
        keb_input = KEBInputOutput(input_data=artifact_data)
        
        # Process
        result = processor.process(keb_input)
        
        # Record processing
        self.processing_history.append({
            "artifact_path": artifact_data.get('file_path', 'unknown'),
            "processor": processor_name,
            "timestamp": __import__('time').time(),
            "status": result.processing_metadata.get('status', 'unknown')
        })
        
        return result
    
    def batch_process_artifacts(self, artifacts: List[Dict[str, Any]]) -> List[KEBInputOutput]:
        """
        Process multiple artifacts through [KEB] pipeline
        
        Args:
            artifacts: List of artifact data dictionaries
            
        Returns:
            List of [KEB] processing results
        """
        results = []
        
        for artifact in artifacts:
            try:
                result = self.process_artifact(artifact)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing artifact {artifact.get('file_path', 'unknown')}: {e}")
                error_result = KEBInputOutput(
                    input_data=artifact,
                    output_data={"error": str(e)}
                )
                results.append(error_result)
        
        return results
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = {
            "total_processed": len(self.processing_history),
            "by_processor": {},
            "by_status": {},
            "recent_activity": self.processing_history[-10:]  # Last 10
        }
        
        for record in self.processing_history:
            processor = record['processor']
            status = record['status']
            
            stats["by_processor"][processor] = stats["by_processor"].get(processor, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats
    
    def export_keb_results(self, results: List[KEBInputOutput], 
                          output_path: str) -> bool:
        """
        Export [KEB] processing results to file
        
        Args:
            results: List of [KEB] results
            output_path: Path to output file
            
        Returns:
            True if export successful
        """
        try:
            export_data = {
                "export_timestamp": __import__('time').time(),
                "total_results": len(results),
                "results": [result.to_dict() for result in results]
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported [KEB] results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting [KEB] results: {e}")
            return False
    
    def create_keb_callable_interface(self) -> Callable:
        """
        Create callable interface for [KEB] pipeline integration
        
        Returns:
            Callable function for [KEB] processing
        """
        def keb_callable(input_data: Dict[str, Any], 
                        processor: Optional[str] = None) -> Dict[str, Any]:
            """
            Callable interface for [KEB] pipeline
            
            Args:
                input_data: Input data for processing
                processor: Optional processor name
                
            Returns:
                Processing results
            """
            result = self.process_artifact(input_data, processor)
            return result.to_dict()
        
        return keb_callable
