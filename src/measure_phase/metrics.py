
"""
Measurement and Metrics Framework
=================================

Establishes KPIs for artifact processing, performance metrics for heterogeneous
pipeline, traceability metrics, and dashboard data generation.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and manages metrics for the DMAIC system"""
    
    def __init__(self):
        self.metrics_data = {
            'processing_metrics': defaultdict(list),
            'performance_metrics': defaultdict(list),
            'traceability_metrics': defaultdict(list),
            'kpi_metrics': defaultdict(list)
        }
        
        # Time-series data with sliding windows
        self.time_series = {
            'processing_times': deque(maxlen=1000),
            'throughput': deque(maxlen=100),
            'error_rates': deque(maxlen=100),
            'cache_hit_rates': deque(maxlen=100)
        }
        
        self.start_time = time.time()
        
    def record_processing_metric(self, artifact_type: str, operation: str, 
                               duration: float, success: bool, **kwargs):
        """Record processing metrics for artifacts"""
        metric = {
            'timestamp': time.time(),
            'artifact_type': artifact_type,
            'operation': operation,
            'duration': duration,
            'success': success,
            'metadata': kwargs
        }
        
        self.metrics_data['processing_metrics'][artifact_type].append(metric)
        self.time_series['processing_times'].append(duration)
        
        logger.debug(f"Recorded processing metric: {artifact_type} {operation} "
                    f"({duration:.3f}s, {'success' if success else 'failed'})")
    
    def record_performance_metric(self, metric_name: str, value: float, 
                                unit: str = "", **kwargs):
        """Record performance metrics"""
        metric = {
            'timestamp': time.time(),
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'metadata': kwargs
        }
        
        self.metrics_data['performance_metrics'][metric_name].append(metric)
        
        # Update time series for specific metrics
        if metric_name == 'throughput':
            self.time_series['throughput'].append(value)
        elif metric_name == 'cache_hit_rate':
            self.time_series['cache_hit_rates'].append(value)
        elif metric_name == 'error_rate':
            self.time_series['error_rates'].append(value)
    
    def record_traceability_metric(self, source_artifact: str, target_artifact: str,
                                 relationship_type: str, confidence: float = 1.0):
        """Record traceability relationships between artifacts"""
        metric = {
            'timestamp': time.time(),
            'source_artifact': source_artifact,
            'target_artifact': target_artifact,
            'relationship_type': relationship_type,
            'confidence': confidence
        }
        
        self.metrics_data['traceability_metrics'][relationship_type].append(metric)
    
    def record_kpi_metric(self, kpi_name: str, value: float, target: Optional[float] = None):
        """Record KPI metrics"""
        metric = {
            'timestamp': time.time(),
            'kpi_name': kpi_name,
            'value': value,
            'target': target,
            'achievement_rate': (value / target * 100) if target and target > 0 else None
        }
        
        self.metrics_data['kpi_metrics'][kpi_name].append(metric)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics by artifact type"""
        stats = {}
        
        for artifact_type, metrics in self.metrics_data['processing_metrics'].items():
            if not metrics:
                continue
                
            durations = [m['duration'] for m in metrics]
            success_count = sum(1 for m in metrics if m['success'])
            
            stats[artifact_type] = {
                'total_processed': len(metrics),
                'success_count': success_count,
                'failure_count': len(metrics) - success_count,
                'success_rate': (success_count / len(metrics)) * 100,
                'avg_processing_time': statistics.mean(durations),
                'min_processing_time': min(durations),
                'max_processing_time': max(durations),
                'median_processing_time': statistics.median(durations)
            }
        
        return stats
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {
            'uptime_seconds': time.time() - self.start_time,
            'total_operations': sum(len(metrics) for metrics in self.metrics_data['processing_metrics'].values()),
            'current_metrics': {}
        }
        
        # Current performance metrics
        for metric_name, metrics in self.metrics_data['performance_metrics'].items():
            if metrics:
                latest = metrics[-1]
                summary['current_metrics'][metric_name] = {
                    'value': latest['value'],
                    'unit': latest['unit'],
                    'timestamp': latest['timestamp']
                }
        
        # Time series statistics
        if self.time_series['processing_times']:
            summary['processing_time_stats'] = {
                'avg': statistics.mean(self.time_series['processing_times']),
                'median': statistics.median(self.time_series['processing_times']),
                'p95': self._percentile(self.time_series['processing_times'], 95)
            }
        
        if self.time_series['throughput']:
            summary['throughput_stats'] = {
                'current': self.time_series['throughput'][-1],
                'avg': statistics.mean(self.time_series['throughput']),
                'max': max(self.time_series['throughput'])
            }
        
        return summary
    
    def get_kpi_dashboard_data(self) -> Dict[str, Any]:
        """Get KPI data for dashboard"""
        dashboard_data = {
            'kpis': {},
            'trends': {},
            'alerts': []
        }
        
        for kpi_name, metrics in self.metrics_data['kpi_metrics'].items():
            if not metrics:
                continue
            
            latest = metrics[-1]
            values = [m['value'] for m in metrics[-10:]]  # Last 10 values
            
            dashboard_data['kpis'][kpi_name] = {
                'current_value': latest['value'],
                'target': latest['target'],
                'achievement_rate': latest['achievement_rate'],
                'trend': self._calculate_trend(values),
                'last_updated': latest['timestamp']
            }
            
            # Generate alerts
            if latest['target'] and latest['achievement_rate']:
                if latest['achievement_rate'] < 80:
                    dashboard_data['alerts'].append({
                        'type': 'warning',
                        'kpi': kpi_name,
                        'message': f"{kpi_name} below target ({latest['achievement_rate']:.1f}%)"
                    })
                elif latest['achievement_rate'] > 120:
                    dashboard_data['alerts'].append({
                        'type': 'info',
                        'kpi': kpi_name,
                        'message': f"{kpi_name} exceeding target ({latest['achievement_rate']:.1f}%)"
                    })
        
        return dashboard_data
    
    def get_traceability_report(self) -> Dict[str, Any]:
        """Get traceability analysis report"""
        report = {
            'total_relationships': 0,
            'by_type': {},
            'confidence_distribution': {},
            'artifact_connections': defaultdict(int)
        }
        
        all_relationships = []
        for rel_type, metrics in self.metrics_data['traceability_metrics'].items():
            all_relationships.extend(metrics)
            report['by_type'][rel_type] = len(metrics)
        
        report['total_relationships'] = len(all_relationships)
        
        # Confidence distribution
        if all_relationships:
            confidences = [r['confidence'] for r in all_relationships]
            report['confidence_distribution'] = {
                'avg': statistics.mean(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'high_confidence_count': sum(1 for c in confidences if c >= 0.8)
            }
            
            # Artifact connections
            for rel in all_relationships:
                report['artifact_connections'][rel['source_artifact']] += 1
                report['artifact_connections'][rel['target_artifact']] += 1
        
        return report
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def export_metrics(self, output_path: str) -> bool:
        """Export all metrics to file"""
        try:
            export_data = {
                'export_timestamp': time.time(),
                'metrics_data': dict(self.metrics_data),
                'summary': {
                    'processing_stats': self.get_processing_statistics(),
                    'performance_summary': self.get_performance_summary(),
                    'kpi_dashboard': self.get_kpi_dashboard_data(),
                    'traceability_report': self.get_traceability_report()
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported metrics to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return False

class KPIManager:
    """Manages Key Performance Indicators for the DMAIC system"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        
        # Define KPIs with targets
        self.kpi_definitions = {
            'artifact_processing_rate': {
                'name': 'Artifact Processing Rate',
                'unit': 'artifacts/hour',
                'target': 100,
                'description': 'Number of artifacts processed per hour'
            },
            'processing_success_rate': {
                'name': 'Processing Success Rate',
                'unit': '%',
                'target': 95,
                'description': 'Percentage of artifacts processed successfully'
            },
            'average_processing_time': {
                'name': 'Average Processing Time',
                'unit': 'seconds',
                'target': 5.0,
                'description': 'Average time to process an artifact'
            },
            'cache_hit_rate': {
                'name': 'Cache Hit Rate',
                'unit': '%',
                'target': 80,
                'description': 'Percentage of cache hits vs misses'
            },
            'index_query_performance': {
                'name': 'Index Query Performance',
                'unit': 'ms',
                'target': 100,
                'description': 'Average time for index queries'
            },
            'pipeline_throughput': {
                'name': 'Pipeline Throughput',
                'unit': 'MB/hour',
                'target': 1000,
                'description': 'Data throughput through the pipeline'
            }
        }
    
    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate current KPI values"""
        kpis = {}
        
        # Get processing statistics
        processing_stats = self.metrics.get_processing_statistics()
        performance_summary = self.metrics.get_performance_summary()
        
        # Calculate artifact processing rate
        uptime_hours = performance_summary['uptime_seconds'] / 3600
        if uptime_hours > 0:
            processing_rate = performance_summary['total_operations'] / uptime_hours
            kpis['artifact_processing_rate'] = processing_rate
            self.metrics.record_kpi_metric('artifact_processing_rate', processing_rate, 
                                         self.kpi_definitions['artifact_processing_rate']['target'])
        
        # Calculate overall success rate
        total_processed = 0
        total_successful = 0
        
        for artifact_type, stats in processing_stats.items():
            total_processed += stats['total_processed']
            total_successful += stats['success_count']
        
        if total_processed > 0:
            success_rate = (total_successful / total_processed) * 100
            kpis['processing_success_rate'] = success_rate
            self.metrics.record_kpi_metric('processing_success_rate', success_rate,
                                         self.kpi_definitions['processing_success_rate']['target'])
        
        # Calculate average processing time
        if 'processing_time_stats' in performance_summary:
            avg_time = performance_summary['processing_time_stats']['avg']
            kpis['average_processing_time'] = avg_time
            self.metrics.record_kpi_metric('average_processing_time', avg_time,
                                         self.kpi_definitions['average_processing_time']['target'])
        
        # Get cache hit rate from current metrics
        current_metrics = performance_summary.get('current_metrics', {})
        if 'cache_hit_rate' in current_metrics:
            hit_rate = current_metrics['cache_hit_rate']['value']
            kpis['cache_hit_rate'] = hit_rate
            self.metrics.record_kpi_metric('cache_hit_rate', hit_rate,
                                         self.kpi_definitions['cache_hit_rate']['target'])
        
        return kpis
    
    def get_kpi_status(self) -> Dict[str, Any]:
        """Get status of all KPIs"""
        current_kpis = self.calculate_kpis()
        dashboard_data = self.metrics.get_kpi_dashboard_data()
        
        status = {
            'kpi_count': len(self.kpi_definitions),
            'measured_kpis': len(current_kpis),
            'kpis_meeting_target': 0,
            'kpis_below_target': 0,
            'overall_health': 'unknown',
            'details': {}
        }
        
        for kpi_name, definition in self.kpi_definitions.items():
            kpi_status = {
                'definition': definition,
                'current_value': current_kpis.get(kpi_name),
                'dashboard_data': dashboard_data['kpis'].get(kpi_name, {})
            }
            
            # Determine status
            if kpi_name in current_kpis and definition['target']:
                current_value = current_kpis[kpi_name]
                target = definition['target']
                
                # For time-based metrics, lower is better
                if definition['unit'] in ['seconds', 'ms']:
                    meeting_target = current_value <= target
                else:
                    meeting_target = current_value >= target
                
                if meeting_target:
                    status['kpis_meeting_target'] += 1
                    kpi_status['status'] = 'meeting_target'
                else:
                    status['kpis_below_target'] += 1
                    kpi_status['status'] = 'below_target'
            else:
                kpi_status['status'] = 'not_measured'
            
            status['details'][kpi_name] = kpi_status
        
        # Calculate overall health
        if status['measured_kpis'] > 0:
            health_ratio = status['kpis_meeting_target'] / status['measured_kpis']
            if health_ratio >= 0.8:
                status['overall_health'] = 'good'
            elif health_ratio >= 0.6:
                status['overall_health'] = 'fair'
            else:
                status['overall_health'] = 'poor'
        
        return status

class DashboardDataGenerator:
    """Generates data for the DMAIC dashboard"""
    
    def __init__(self, metrics_collector: MetricsCollector, kpi_manager: KPIManager):
        self.metrics = metrics_collector
        self.kpi_manager = kpi_manager
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate complete dashboard data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overview': self._generate_overview(),
            'kpis': self._generate_kpi_section(),
            'processing': self._generate_processing_section(),
            'performance': self._generate_performance_section(),
            'traceability': self._generate_traceability_section(),
            'alerts': self._generate_alerts()
        }
    
    def _generate_overview(self) -> Dict[str, Any]:
        """Generate overview section"""
        performance_summary = self.metrics.get_performance_summary()
        processing_stats = self.metrics.get_processing_statistics()
        
        total_artifacts = sum(stats['total_processed'] for stats in processing_stats.values())
        total_successful = sum(stats['success_count'] for stats in processing_stats.values())
        
        return {
            'uptime': performance_summary['uptime_seconds'],
            'total_artifacts_processed': total_artifacts,
            'successful_processing': total_successful,
            'overall_success_rate': (total_successful / total_artifacts * 100) if total_artifacts > 0 else 0,
            'artifact_types_supported': len(processing_stats),
            'current_operations': performance_summary['total_operations']
        }
    
    def _generate_kpi_section(self) -> Dict[str, Any]:
        """Generate KPI section"""
        kpi_status = self.kpi_manager.get_kpi_status()
        dashboard_data = self.metrics.get_kpi_dashboard_data()
        
        return {
            'status_summary': {
                'total_kpis': kpi_status['kpi_count'],
                'measured': kpi_status['measured_kpis'],
                'meeting_target': kpi_status['kpis_meeting_target'],
                'below_target': kpi_status['kpis_below_target'],
                'overall_health': kpi_status['overall_health']
            },
            'kpi_details': kpi_status['details'],
            'trends': dashboard_data.get('trends', {}),
            'alerts': dashboard_data.get('alerts', [])
        }
    
    def _generate_processing_section(self) -> Dict[str, Any]:
        """Generate processing metrics section"""
        processing_stats = self.metrics.get_processing_statistics()
        
        # Calculate totals and averages
        total_processed = sum(stats['total_processed'] for stats in processing_stats.values())
        avg_success_rate = statistics.mean([stats['success_rate'] for stats in processing_stats.values()]) if processing_stats else 0
        avg_processing_time = statistics.mean([stats['avg_processing_time'] for stats in processing_stats.values()]) if processing_stats else 0
        
        return {
            'summary': {
                'total_processed': total_processed,
                'average_success_rate': avg_success_rate,
                'average_processing_time': avg_processing_time,
                'artifact_types': len(processing_stats)
            },
            'by_artifact_type': processing_stats,
            'recent_activity': self._get_recent_processing_activity()
        }
    
    def _generate_performance_section(self) -> Dict[str, Any]:
        """Generate performance metrics section"""
        performance_summary = self.metrics.get_performance_summary()
        
        return {
            'system_performance': performance_summary,
            'time_series_data': {
                'processing_times': list(self.metrics.time_series['processing_times'])[-50:],  # Last 50
                'throughput': list(self.metrics.time_series['throughput'])[-20:],  # Last 20
                'error_rates': list(self.metrics.time_series['error_rates'])[-20:],
                'cache_hit_rates': list(self.metrics.time_series['cache_hit_rates'])[-20:]
            }
        }
    
    def _generate_traceability_section(self) -> Dict[str, Any]:
        """Generate traceability section"""
        traceability_report = self.metrics.get_traceability_report()
        
        return {
            'summary': traceability_report,
            'relationship_graph': self._generate_relationship_graph_data(),
            'top_connected_artifacts': self._get_top_connected_artifacts(traceability_report)
        }
    
    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate system alerts"""
        alerts = []
        
        # Get KPI alerts
        kpi_dashboard = self.metrics.get_kpi_dashboard_data()
        alerts.extend(kpi_dashboard.get('alerts', []))
        
        # Add system alerts
        performance_summary = self.metrics.get_performance_summary()
        
        # High error rate alert
        if self.metrics.time_series['error_rates']:
            recent_error_rate = self.metrics.time_series['error_rates'][-1]
            if recent_error_rate > 10:  # 10% error rate threshold
                alerts.append({
                    'type': 'error',
                    'component': 'processing',
                    'message': f'High error rate detected: {recent_error_rate:.1f}%'
                })
        
        # Low cache hit rate alert
        if self.metrics.time_series['cache_hit_rates']:
            recent_hit_rate = self.metrics.time_series['cache_hit_rates'][-1]
            if recent_hit_rate < 50:  # 50% hit rate threshold
                alerts.append({
                    'type': 'warning',
                    'component': 'cache',
                    'message': f'Low cache hit rate: {recent_hit_rate:.1f}%'
                })
        
        return alerts
    
    def _get_recent_processing_activity(self) -> List[Dict[str, Any]]:
        """Get recent processing activity"""
        recent_activity = []
        
        # Get recent metrics from all artifact types
        all_recent = []
        for artifact_type, metrics in self.metrics.metrics_data['processing_metrics'].items():
            recent_metrics = sorted(metrics, key=lambda x: x['timestamp'], reverse=True)[:5]
            for metric in recent_metrics:
                metric['artifact_type'] = artifact_type
                all_recent.append(metric)
        
        # Sort by timestamp and take top 10
        all_recent.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for metric in all_recent[:10]:
            recent_activity.append({
                'timestamp': metric['timestamp'],
                'artifact_type': metric['artifact_type'],
                'operation': metric['operation'],
                'duration': metric['duration'],
                'success': metric['success']
            })
        
        return recent_activity
    
    def _generate_relationship_graph_data(self) -> Dict[str, Any]:
        """Generate data for relationship graph visualization"""
        # This would generate node/edge data for visualization
        # Simplified version for now
        
        nodes = set()
        edges = []
        
        for rel_type, metrics in self.metrics.metrics_data['traceability_metrics'].items():
            for metric in metrics:
                nodes.add(metric['source_artifact'])
                nodes.add(metric['target_artifact'])
                edges.append({
                    'source': metric['source_artifact'],
                    'target': metric['target_artifact'],
                    'type': rel_type,
                    'confidence': metric['confidence']
                })
        
        return {
            'nodes': [{'id': node, 'label': node.split('/')[-1]} for node in nodes],
            'edges': edges
        }
    
    def _get_top_connected_artifacts(self, traceability_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get most connected artifacts"""
        connections = traceability_report.get('artifact_connections', {})
        
        # Sort by connection count
        sorted_artifacts = sorted(connections.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'artifact': artifact, 'connections': count}
            for artifact, count in sorted_artifacts[:10]
        ]
