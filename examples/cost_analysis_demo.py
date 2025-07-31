#!/usr/bin/env python3
"""
Cost Analysis Demo

Demonstrates the cost analysis capabilities of the InvenTag system including:
- Resource cost estimation using AWS Pricing API
- Expensive resource identification with configurable thresholds
- Forgotten resource detection based on activity patterns
- Cost trend analysis and alerting functionality
- Cost optimization recommendations based on resource utilization

This demo shows how to use the CostAnalyzer as both a standalone component
and integrated with the BOMDataProcessor.
"""

import sys
import os
import json
import logging
from decimal import Decimal
from datetime import datetime, timezone

# Add the parent directory to the path so we can import inventag
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventag.discovery.cost_analyzer import (
    CostAnalyzer, 
    CostThresholds,
    ResourceCostEstimate,
    ForgottenResourceAnalysis,
    CostOptimizationRecommendation
)
from inventag.reporting.bom_processor import BOMDataProcessor, BOMProcessingConfig


def setup_logging():
    """Set up logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_sample_resources():
    """Create sample resource data for demonstration."""
    return [
        {
            'id': 'i-1234567890abcdef0',
            'service': 'EC2',
            'type': 'Instance',
            'region': 'us-east-1',
            'arn': 'arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0',
            'instance_type': 't3.large',
            'tags': {'Name': 'Web Server', 'Environment': 'Production'}
        },
        {
            'id': 'i-0987654321fedcba0',
            'service': 'EC2',
            'type': 'Instance',
            'region': 'us-east-1',
            'arn': 'arn:aws:ec2:us-east-1:123456789012:instance/i-0987654321fedcba0',
            'instance_type': 't3.micro',
            'tags': {'Name': 'Test Server', 'Environment': 'Development'}
        },
        {
            'id': 'database-prod-1',
            'service': 'RDS',
            'type': 'DBInstance',
            'region': 'us-east-1',
            'arn': 'arn:aws:rds:us-east-1:123456789012:db:database-prod-1',
            'db_instance_class': 'db.r5.xlarge',
            'engine': 'postgresql',
            'tags': {'Name': 'Production Database', 'Environment': 'Production'}
        },
        {
            'id': 'my-data-bucket',
            'service': 'S3',
            'type': 'Bucket',
            'region': 'us-east-1',
            'arn': 'arn:aws:s3:::my-data-bucket',
            'storage_class': 'Standard',
            'size_gb': 500,
            'tags': {'Name': 'Data Bucket', 'Environment': 'Production'}
        },
        {
            'id': 'old-test-instance',
            'service': 'EC2',
            'type': 'Instance',
            'region': 'us-west-2',
            'arn': 'arn:aws:ec2:us-west-2:123456789012:instance/old-test-instance',
            'instance_type': 'm5.large',
            'tags': {'Name': 'Old Test Instance', 'Environment': 'Development'}
        },
        {
            'id': 'my-lambda-function',
            'service': 'LAMBDA',
            'type': 'Function',
            'region': 'us-east-1',
            'arn': 'arn:aws:lambda:us-east-1:123456789012:function:my-lambda-function',
            'runtime': 'python3.9',
            'memory_size': 512,
            'tags': {'Name': 'Data Processor', 'Environment': 'Production'}
        }
    ]


def demo_standalone_cost_analyzer():
    """Demonstrate standalone cost analyzer functionality."""
    print("\n" + "="*60)
    print("STANDALONE COST ANALYZER DEMO")
    print("="*60)
    
    # Create custom thresholds
    thresholds = CostThresholds(
        expensive_resource_monthly_threshold=Decimal('50.00'),
        forgotten_resource_days_threshold=30,
        high_cost_alert_threshold=Decimal('500.00'),
        cost_trend_alert_percentage=25.0
    )
    
    # Initialize cost analyzer
    print("\n1. Initializing Cost Analyzer...")
    print("   Note: In demo mode, AWS clients are mocked to avoid requiring credentials")
    
    try:
        # Create a mock session to avoid AWS credential requirements
        from unittest.mock import Mock
        mock_session = Mock()
        cost_analyzer = CostAnalyzer(session=mock_session, thresholds=thresholds)
        print(f"   - Expensive resource threshold: ${thresholds.expensive_resource_monthly_threshold}")
        print(f"   - Forgotten resource threshold: {thresholds.forgotten_resource_days_threshold} days")
    except Exception as e:
        print(f"   - Cost analyzer initialization failed (expected in demo): {e}")
        print("   - Proceeding with demonstration of data structures...")
    
    # Create sample resources
    resources = create_sample_resources()
    print(f"\n2. Analyzing {len(resources)} sample resources...")
    
    # Note: In a real environment, these methods would make actual AWS API calls
    # For demo purposes, we'll show the structure and simulate some results
    
    try:
        # Demonstrate cost estimation (would normally call AWS Pricing API)
        print("\n3. Cost Estimation Results:")
        print("   Note: This demo shows the structure - actual AWS API calls would be made in production")
        
        # Create sample cost estimates to demonstrate the data structure
        sample_estimates = [
            ResourceCostEstimate(
                resource_id='i-1234567890abcdef0',
                resource_type='Instance',
                service='EC2',
                region='us-east-1',
                estimated_monthly_cost=Decimal('67.32'),
                cost_breakdown={'compute': Decimal('67.32')},
                pricing_model='on-demand',
                confidence_level='high'
            ),
            ResourceCostEstimate(
                resource_id='database-prod-1',
                resource_type='DBInstance',
                service='RDS',
                region='us-east-1',
                estimated_monthly_cost=Decimal('245.60'),
                cost_breakdown={'database': Decimal('245.60')},
                pricing_model='on-demand',
                confidence_level='high'
            ),
            ResourceCostEstimate(
                resource_id='my-data-bucket',
                resource_type='Bucket',
                service='S3',
                region='us-east-1',
                estimated_monthly_cost=Decimal('11.50'),
                cost_breakdown={'storage': Decimal('11.50')},
                pricing_model='on-demand',
                confidence_level='medium'
            )
        ]
        
        for estimate in sample_estimates:
            print(f"   - {estimate.resource_id} ({estimate.service}): ${estimate.estimated_monthly_cost}/month")
            print(f"     Confidence: {estimate.confidence_level}, Model: {estimate.pricing_model}")
        
        # Demonstrate expensive resource identification
        print("\n4. Expensive Resource Analysis:")
        expensive_resources = cost_analyzer.identify_expensive_resources(sample_estimates)
        
        if expensive_resources:
            print(f"   Found {len(expensive_resources)} expensive resources:")
            for resource in expensive_resources:
                print(f"   - {resource.resource_id}: ${resource.estimated_monthly_cost}/month")
        else:
            print("   No expensive resources found above threshold")
        
        # Demonstrate forgotten resource analysis structure
        print("\n5. Forgotten Resource Analysis:")
        print("   Note: This would analyze CloudWatch metrics in production")
        
        # Create sample forgotten resource analysis
        sample_forgotten = ForgottenResourceAnalysis(
            resource_id='old-test-instance',
            resource_type='Instance',
            service='EC2',
            days_since_last_activity=45,
            estimated_monthly_cost=Decimal('73.44'),
            activity_indicators={'cpu_utilization': [], 'network_activity': []},
            risk_level='high',
            recommendations=[
                'Consider terminating this resource as it has been inactive for over 90 days',
                'High cost resource - prioritize review and potential termination',
                'Consider stopping the instance if not needed, or downsizing if underutilized'
            ]
        )
        
        print(f"   - {sample_forgotten.resource_id}: {sample_forgotten.days_since_last_activity} days inactive")
        print(f"     Risk Level: {sample_forgotten.risk_level}")
        print(f"     Estimated Cost: ${sample_forgotten.estimated_monthly_cost}/month")
        print("     Recommendations:")
        for rec in sample_forgotten.recommendations:
            print(f"       • {rec}")
        
        # Demonstrate optimization recommendations
        print("\n6. Cost Optimization Recommendations:")
        
        sample_recommendation = CostOptimizationRecommendation(
            resource_id='database-prod-1',
            resource_type='DBInstance',
            service='RDS',
            recommendation_type='rightsizing',
            current_monthly_cost=Decimal('245.60'),
            potential_monthly_savings=Decimal('61.40'),
            confidence_level='medium',
            implementation_effort='medium',
            description='Consider optimizing this RDS instance configuration',
            action_items=[
                'Review database performance metrics',
                'Consider using Aurora Serverless for variable workloads',
                'Evaluate Reserved Instance pricing'
            ]
        )
        
        print(f"   - {sample_recommendation.resource_id} ({sample_recommendation.recommendation_type}):")
        print(f"     Current Cost: ${sample_recommendation.current_monthly_cost}/month")
        print(f"     Potential Savings: ${sample_recommendation.potential_monthly_savings}/month")
        print(f"     Confidence: {sample_recommendation.confidence_level}")
        print(f"     Description: {sample_recommendation.description}")
        print("     Action Items:")
        for item in sample_recommendation.action_items:
            print(f"       • {item}")
        
        # Demonstrate cost analysis summary
        print("\n7. Cost Analysis Summary:")
        
        total_cost = sum(est.estimated_monthly_cost for est in sample_estimates)
        total_savings = sample_recommendation.potential_monthly_savings
        
        print(f"   - Total Estimated Monthly Cost: ${total_cost}")
        print(f"   - Expensive Resources: {len(expensive_resources)}")
        print(f"   - Forgotten Resources: 1")
        print(f"   - Total Potential Savings: ${total_savings}")
        print(f"   - Optimization Opportunities: 1")
        
        cost_by_service = {}
        for est in sample_estimates:
            cost_by_service[est.service] = cost_by_service.get(est.service, Decimal('0')) + est.estimated_monthly_cost
        
        print("   - Cost by Service:")
        for service, cost in cost_by_service.items():
            print(f"     • {service}: ${cost}")
        
    except Exception as e:
        print(f"   Error during cost analysis: {e}")
        print("   Note: This is expected in demo mode without actual AWS credentials")


def demo_integrated_cost_analysis():
    """Demonstrate cost analysis integrated with BOM processor."""
    print("\n" + "="*60)
    print("INTEGRATED BOM PROCESSOR WITH COST ANALYSIS DEMO")
    print("="*60)
    
    # Create BOM processing configuration with cost analysis enabled
    config = BOMProcessingConfig(
        enable_network_analysis=False,  # Disable for demo
        enable_security_analysis=False,  # Disable for demo
        enable_service_enrichment=False,  # Disable for demo
        enable_service_descriptions=False,  # Disable for demo
        enable_tag_mapping=False,  # Disable for demo
        enable_cost_analysis=True,  # Enable cost analysis
        enable_parallel_processing=False,  # Disable for demo
        cost_thresholds=CostThresholds(
            expensive_resource_monthly_threshold=Decimal('75.00'),
            forgotten_resource_days_threshold=20
        )
    )
    
    print("\n1. Initializing BOM Processor with Cost Analysis...")
    print(f"   - Cost analysis enabled: {config.enable_cost_analysis}")
    print(f"   - Expensive resource threshold: ${config.cost_thresholds.expensive_resource_monthly_threshold}")
    
    try:
        # Initialize BOM processor
        bom_processor = BOMDataProcessor(config)
        print("   - BOM Processor initialized successfully")
        
        # Create sample inventory data
        inventory_data = create_sample_resources()
        print(f"\n2. Processing {len(inventory_data)} resources with cost analysis...")
        
        # Process the inventory data
        # Note: This would normally make AWS API calls for cost analysis
        print("   Note: Cost analysis would make actual AWS API calls in production")
        
        # In demo mode, we'll show what the structure would look like
        print("\n3. Expected BOM Data Structure with Cost Analysis:")
        print("   {")
        print("     'resources': [...],  # Enriched with cost information")
        print("     'cost_analysis': {")
        print("       'cost_estimates': [...],")
        print("       'expensive_resources': [...],")
        print("       'forgotten_resources': [...],")
        print("       'cost_trends': [...],")
        print("       'optimization_recommendations': [...],")
        print("       'summary': {")
        print("         'total_estimated_monthly_cost': 324.42,")
        print("         'expensive_resources_count': 2,")
        print("         'forgotten_resources_count': 1,")
        print("         'total_potential_savings': 97.33,")
        print("         'cost_by_service': {'EC2': 140.76, 'RDS': 245.60, 'S3': 11.50},")
        print("         'optimization_opportunities': 3")
        print("       }")
        print("     }")
        print("   }")
        
        print("\n4. Resource Enrichment with Cost Information:")
        print("   Each resource would be enriched with:")
        print("   - estimated_monthly_cost")
        print("   - cost_breakdown")
        print("   - is_expensive flag")
        print("   - forgotten_analysis (if applicable)")
        print("   - optimization_recommendations")
        
    except Exception as e:
        print(f"   Error during BOM processing: {e}")
        print("   Note: This is expected in demo mode without actual AWS credentials")


def demo_cost_thresholds_configuration():
    """Demonstrate different cost threshold configurations."""
    print("\n" + "="*60)
    print("COST THRESHOLDS CONFIGURATION DEMO")
    print("="*60)
    
    print("\n1. Default Thresholds:")
    default_thresholds = CostThresholds()
    print(f"   - Expensive resource threshold: ${default_thresholds.expensive_resource_monthly_threshold}")
    print(f"   - Forgotten resource days: {default_thresholds.forgotten_resource_days_threshold}")
    print(f"   - High cost alert threshold: ${default_thresholds.high_cost_alert_threshold}")
    print(f"   - Cost trend alert percentage: {default_thresholds.cost_trend_alert_percentage}%")
    print(f"   - Unused resource utilization: {default_thresholds.unused_resource_utilization_threshold}%")
    
    print("\n2. Conservative Thresholds (Lower sensitivity):")
    conservative_thresholds = CostThresholds(
        expensive_resource_monthly_threshold=Decimal('200.00'),
        forgotten_resource_days_threshold=60,
        high_cost_alert_threshold=Decimal('2000.00'),
        cost_trend_alert_percentage=75.0,
        unused_resource_utilization_threshold=2.0
    )
    print(f"   - Expensive resource threshold: ${conservative_thresholds.expensive_resource_monthly_threshold}")
    print(f"   - Forgotten resource days: {conservative_thresholds.forgotten_resource_days_threshold}")
    print(f"   - High cost alert threshold: ${conservative_thresholds.high_cost_alert_threshold}")
    print(f"   - Cost trend alert percentage: {conservative_thresholds.cost_trend_alert_percentage}%")
    print(f"   - Unused resource utilization: {conservative_thresholds.unused_resource_utilization_threshold}%")
    
    print("\n3. Aggressive Thresholds (Higher sensitivity):")
    aggressive_thresholds = CostThresholds(
        expensive_resource_monthly_threshold=Decimal('25.00'),
        forgotten_resource_days_threshold=7,
        high_cost_alert_threshold=Decimal('100.00'),
        cost_trend_alert_percentage=10.0,
        unused_resource_utilization_threshold=10.0
    )
    print(f"   - Expensive resource threshold: ${aggressive_thresholds.expensive_resource_monthly_threshold}")
    print(f"   - Forgotten resource days: {aggressive_thresholds.forgotten_resource_days_threshold}")
    print(f"   - High cost alert threshold: ${aggressive_thresholds.high_cost_alert_threshold}")
    print(f"   - Cost trend alert percentage: {aggressive_thresholds.cost_trend_alert_percentage}%")
    print(f"   - Unused resource utilization: {aggressive_thresholds.unused_resource_utilization_threshold}%")
    
    print("\n4. Use Case Recommendations:")
    print("   - Default: Good for most organizations")
    print("   - Conservative: Large enterprises with established infrastructure")
    print("   - Aggressive: Cost-conscious startups or development environments")


def main():
    """Main demo function."""
    setup_logging()
    
    print("InvenTag Cost Analysis Demo")
    print("=" * 60)
    print("This demo showcases the cost analysis capabilities including:")
    print("- Resource cost estimation using AWS Pricing API")
    print("- Expensive resource identification")
    print("- Forgotten resource detection")
    print("- Cost optimization recommendations")
    print("- Integration with BOM data processing")
    
    try:
        # Run demo sections
        demo_cost_thresholds_configuration()
        demo_standalone_cost_analyzer()
        demo_integrated_cost_analysis()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nNext Steps:")
        print("1. Configure AWS credentials for actual cost analysis")
        print("2. Adjust cost thresholds based on your organization's needs")
        print("3. Enable cost analysis in your BOM processing configuration")
        print("4. Review and implement cost optimization recommendations")
        print("\nFor production use:")
        print("- Ensure AWS Pricing API access (us-east-1 region)")
        print("- Configure CloudWatch metrics for activity analysis")
        print("- Set up Cost Explorer for trend analysis")
        print("- Implement automated cost alerting based on recommendations")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())