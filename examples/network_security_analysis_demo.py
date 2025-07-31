#!/usr/bin/env python3
"""
InvenTag Network and Security Analysis Demo

Demonstrates the new NetworkAnalyzer and SecurityAnalyzer capabilities
for comprehensive VPC and security group analysis.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3
from inventag.discovery import NetworkAnalyzer, SecurityAnalyzer

def demo_network_analysis():
    """Demonstrate network analysis capabilities."""
    print("=== Network Analysis Demo ===")
    
    # Initialize the analyzer
    analyzer = NetworkAnalyzer()
    
    # Sample resource data (would normally come from AWS resource inventory)
    sample_resources = [
        {
            'id': 'i-12345',
            'service': 'EC2',
            'type': 'Instance',
            'region': 'us-east-1',
            'vpc_id': 'vpc-12345',
            'subnet_id': 'subnet-12345'
        },
        {
            'id': 'db-67890',
            'service': 'RDS',
            'type': 'DBInstance',
            'region': 'us-east-1',
            'vpc_id': 'vpc-12345',
            'subnet_id': 'subnet-67890'
        }
    ]
    
    print(f"Sample resources: {len(sample_resources)}")
    print("Features demonstrated:")
    print("- VPC CIDR block analysis and IP utilization calculations")
    print("- Subnet utilization tracking with available IP counting")
    print("- Resource-to-VPC/subnet mapping with intelligent name resolution")
    print("- Network capacity planning and utilization reporting")
    print("- VPC peering and transit gateway relationship mapping")
    
    # Note: In a real scenario, this would connect to AWS and analyze actual VPCs
    print("\nNote: This demo shows the interface. Real analysis requires AWS credentials.")
    
    # Show CIDR calculation capability
    print(f"\nCIDR IP calculation examples:")
    print(f"10.0.1.0/24 has {analyzer._calculate_cidr_ips('10.0.1.0/24')} usable IPs")
    print(f"10.0.0.0/16 has {analyzer._calculate_cidr_ips('10.0.0.0/16')} usable IPs")
    print(f"10.0.1.0/28 has {analyzer._calculate_cidr_ips('10.0.1.0/28')} usable IPs")


def demo_security_analysis():
    """Demonstrate security analysis capabilities."""
    print("\n=== Security Analysis Demo ===")
    
    # Initialize the analyzer
    analyzer = SecurityAnalyzer()
    
    # Sample resource data
    sample_resources = [
        {
            'id': 'i-12345',
            'service': 'EC2',
            'type': 'Instance',
            'region': 'us-east-1',
            'security_groups': [
                {'GroupId': 'sg-web', 'GroupName': 'web-servers'},
                {'GroupId': 'sg-ssh', 'GroupName': 'ssh-access'}
            ]
        }
    ]
    
    print(f"Sample resources: {len(sample_resources)}")
    print("Features demonstrated:")
    print("- Comprehensive security group rule extraction and analysis")
    print("- Overly permissive rule detection (0.0.0.0/0 access) with risk assessment")
    print("- Security group relationship mapping and dependency analysis")
    print("- NACL analysis and unused rule identification")
    print("- Security group reference resolution and circular dependency detection")
    print("- Port and protocol analysis with common service identification")
    
    # Show risk assessment capability
    print(f"\nRisk assessment examples:")
    print(f"SSH from anywhere (0.0.0.0/0:22): {analyzer._assess_rule_risk('0.0.0.0/0', 22, 'tcp')}")
    print(f"HTTP from anywhere (0.0.0.0/0:80): {analyzer._assess_rule_risk('0.0.0.0/0', 80, 'tcp')}")
    print(f"SSH from internal (10.0.0.0/16:22): {analyzer._assess_rule_risk('10.0.0.0/16', 22, 'tcp')}")
    print(f"Custom port from specific IP (192.168.1.100:8080): {analyzer._assess_rule_risk('192.168.1.100/32', 8080, 'tcp')}")
    
    # Show common service identification
    print(f"\nCommon service identification:")
    print(f"Port 22: {analyzer._identify_common_service(22)}")
    print(f"Port 443: {analyzer._identify_common_service(443)}")
    print(f"Port 3306: {analyzer._identify_common_service(3306)}")
    print(f"Port 5432: {analyzer._identify_common_service(5432)}")


def main():
    """Run the network and security analysis demo."""
    print("InvenTag Network and Security Analysis Demo")
    print("=" * 50)
    
    try:
        demo_network_analysis()
        demo_security_analysis()
        
        print("\n=== Integration with BOM Generation ===")
        print("These analyzers integrate with the BOM generation system to provide:")
        print("- Network analysis sections in BOM documents")
        print("- Security assessment summaries")
        print("- Capacity planning recommendations")
        print("- Risk assessment reports")
        print("- Optimization suggestions")
        
        print("\n=== Next Steps ===")
        print("1. Configure AWS credentials")
        print("2. Run aws_resource_inventory.py to collect resource data")
        print("3. Use these analyzers in the BOM generation pipeline")
        print("4. Generate comprehensive network and security reports")
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("This is expected without AWS credentials - the demo shows the interface.")


if __name__ == "__main__":
    main()