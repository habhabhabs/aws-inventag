#!/usr/bin/env python3
"""
AWS Resource Inventory Tool
Discovers and catalogs all AWS resources across services and regions.
"""

import argparse
import json
import yaml
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import sys
import os


class AWSResourceInventory:
    def __init__(self, regions: Optional[List[str]] = None):
        """Initialize the AWS Resource Inventory tool."""
        self.session = boto3.Session()
        self.regions = regions or self._get_available_regions()
        self.resources = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _get_available_regions(self) -> List[str]:
        """Get all available AWS regions."""
        try:
            ec2 = self.session.client('ec2', region_name='us-east-1')
            regions = ec2.describe_regions()['Regions']
            return [region['RegionName'] for region in regions]
        except Exception as e:
            self.logger.error(f"Failed to get regions: {e}")
            return ['us-east-1']  # Fallback to default region
    
    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover all AWS resources across regions and services."""
        self.logger.info("Starting AWS resource discovery...")
        
        for region in self.regions:
            self.logger.info(f"Scanning region: {region}")
            self._discover_ec2_resources(region)
            self._discover_s3_resources(region)
            self._discover_rds_resources(region)
            self._discover_lambda_resources(region)
            self._discover_iam_resources(region)
            self._discover_vpc_resources(region)
            self._discover_cloudformation_resources(region)
            self._discover_ecs_resources(region)
            self._discover_eks_resources(region)
            self._discover_cloudwatch_resources(region)
        
        self.logger.info(f"Discovery complete. Found {len(self.resources)} resources.")
        return self.resources
    
    def _discover_ec2_resources(self, region: str):
        """Discover EC2 resources."""
        try:
            ec2 = self.session.client('ec2', region_name=region)
            
            # EC2 Instances
            instances = ec2.describe_instances()
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    self.resources.append({
                        'service': 'EC2',
                        'type': 'Instance',
                        'region': region,
                        'id': instance['InstanceId'],
                        'name': self._get_tag_value(instance.get('Tags', []), 'Name'),
                        'state': instance['State']['Name'],
                        'instance_type': instance['InstanceType'],
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'launch_time': instance['LaunchTime'].isoformat() if 'LaunchTime' in instance else None,
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                        'discovered_at': datetime.utcnow().isoformat()
                    })
            
            # EBS Volumes
            volumes = ec2.describe_volumes()
            for volume in volumes['Volumes']:
                self.resources.append({
                    'service': 'EC2',
                    'type': 'EBS Volume',
                    'region': region,
                    'id': volume['VolumeId'],
                    'name': self._get_tag_value(volume.get('Tags', []), 'Name'),
                    'state': volume['State'],
                    'size': volume['Size'],
                    'volume_type': volume['VolumeType'],
                    'availability_zone': volume['AvailabilityZone'],
                    'encrypted': volume['Encrypted'],
                    'tags': {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])},
                    'discovered_at': datetime.utcnow().isoformat()
                })
            
            # Security Groups
            security_groups = ec2.describe_security_groups()
            for sg in security_groups['SecurityGroups']:
                self.resources.append({
                    'service': 'EC2',
                    'type': 'Security Group',
                    'region': region,
                    'id': sg['GroupId'],
                    'name': sg['GroupName'],
                    'description': sg['Description'],
                    'vpc_id': sg.get('VpcId'),
                    'tags': {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])},
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover EC2 resources in {region}: {e}")
    
    def _discover_s3_resources(self, region: str):
        """Discover S3 resources."""
        try:
            s3 = self.session.client('s3', region_name=region)
            
            # S3 Buckets (global service, only check once)
            if region == 'us-east-1':  # Only check from one region
                buckets = s3.list_buckets()
                for bucket in buckets['Buckets']:
                    try:
                        bucket_region = s3.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
                        bucket_region = bucket_region or 'us-east-1'
                        
                        # Get bucket tags
                        try:
                            tags_response = s3.get_bucket_tagging(Bucket=bucket['Name'])
                            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagSet', [])}
                        except ClientError:
                            tags = {}
                        
                        self.resources.append({
                            'service': 'S3',
                            'type': 'Bucket',
                            'region': bucket_region,
                            'id': bucket['Name'],
                            'name': bucket['Name'],
                            'creation_date': bucket['CreationDate'].isoformat(),
                            'tags': tags,
                            'discovered_at': datetime.utcnow().isoformat()
                        })
                    except ClientError as e:
                        self.logger.warning(f"Failed to get details for S3 bucket {bucket['Name']}: {e}")
                        
        except ClientError as e:
            self.logger.warning(f"Failed to discover S3 resources: {e}")
    
    def _discover_rds_resources(self, region: str):
        """Discover RDS resources."""
        try:
            rds = self.session.client('rds', region_name=region)
            
            # RDS Instances
            instances = rds.describe_db_instances()
            for instance in instances['DBInstances']:
                # Get tags
                try:
                    tags_response = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
                    tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
                except ClientError:
                    tags = {}
                
                self.resources.append({
                    'service': 'RDS',
                    'type': 'DB Instance',
                    'region': region,
                    'id': instance['DBInstanceIdentifier'],
                    'name': instance['DBInstanceIdentifier'],
                    'engine': instance['Engine'],
                    'engine_version': instance['EngineVersion'],
                    'instance_class': instance['DBInstanceClass'],
                    'status': instance['DBInstanceStatus'],
                    'allocated_storage': instance.get('AllocatedStorage'),
                    'vpc_id': instance.get('DbSubnetGroup', {}).get('VpcId'),
                    'tags': tags,
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover RDS resources in {region}: {e}")
    
    def _discover_lambda_resources(self, region: str):
        """Discover Lambda resources."""
        try:
            lambda_client = self.session.client('lambda', region_name=region)
            
            functions = lambda_client.list_functions()
            for function in functions['Functions']:
                # Get tags
                try:
                    tags_response = lambda_client.list_tags(Resource=function['FunctionArn'])
                    tags = tags_response.get('Tags', {})
                except ClientError:
                    tags = {}
                
                self.resources.append({
                    'service': 'Lambda',
                    'type': 'Function',
                    'region': region,
                    'id': function['FunctionName'],
                    'name': function['FunctionName'],
                    'runtime': function['Runtime'],
                    'memory_size': function['MemorySize'],
                    'timeout': function['Timeout'],
                    'last_modified': function['LastModified'],
                    'tags': tags,
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover Lambda resources in {region}: {e}")
    
    def _discover_iam_resources(self, region: str):
        """Discover IAM resources (global service, only check once)."""
        if region != 'us-east-1':  # IAM is global, only check from one region
            return
            
        try:
            iam = self.session.client('iam')
            
            # IAM Roles
            roles = iam.list_roles()
            for role in roles['Roles']:
                # Get tags
                try:
                    tags_response = iam.list_role_tags(RoleName=role['RoleName'])
                    tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                except ClientError:
                    tags = {}
                
                self.resources.append({
                    'service': 'IAM',
                    'type': 'Role',
                    'region': 'global',
                    'id': role['RoleName'],
                    'name': role['RoleName'],
                    'path': role['Path'],
                    'create_date': role['CreateDate'].isoformat(),
                    'tags': tags,
                    'discovered_at': datetime.utcnow().isoformat()
                })
            
            # IAM Users
            users = iam.list_users()
            for user in users['Users']:
                # Get tags
                try:
                    tags_response = iam.list_user_tags(UserName=user['UserName'])
                    tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                except ClientError:
                    tags = {}
                
                self.resources.append({
                    'service': 'IAM',
                    'type': 'User',
                    'region': 'global',
                    'id': user['UserName'],
                    'name': user['UserName'],
                    'path': user['Path'],
                    'create_date': user['CreateDate'].isoformat(),
                    'tags': tags,
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover IAM resources: {e}")
    
    def _discover_vpc_resources(self, region: str):
        """Discover VPC resources."""
        try:
            ec2 = self.session.client('ec2', region_name=region)
            
            # VPCs
            vpcs = ec2.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                self.resources.append({
                    'service': 'VPC',
                    'type': 'VPC',
                    'region': region,
                    'id': vpc['VpcId'],
                    'name': self._get_tag_value(vpc.get('Tags', []), 'Name'),
                    'cidr_block': vpc['CidrBlock'],
                    'state': vpc['State'],
                    'is_default': vpc['IsDefault'],
                    'tags': {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])},
                    'discovered_at': datetime.utcnow().isoformat()
                })
            
            # Subnets
            subnets = ec2.describe_subnets()
            for subnet in subnets['Subnets']:
                self.resources.append({
                    'service': 'VPC',
                    'type': 'Subnet',
                    'region': region,
                    'id': subnet['SubnetId'],
                    'name': self._get_tag_value(subnet.get('Tags', []), 'Name'),
                    'vpc_id': subnet['VpcId'],
                    'cidr_block': subnet['CidrBlock'],
                    'availability_zone': subnet['AvailabilityZone'],
                    'available_ip_count': subnet['AvailableIpAddressCount'],
                    'tags': {tag['Key']: tag['Value'] for tag in subnet.get('Tags', [])},
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover VPC resources in {region}: {e}")
    
    def _discover_cloudformation_resources(self, region: str):
        """Discover CloudFormation resources."""
        try:
            cf = self.session.client('cloudformation', region_name=region)
            
            stacks = cf.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE'])
            for stack in stacks['StackSummaries']:
                # Get stack tags
                try:
                    stack_details = cf.describe_stacks(StackName=stack['StackName'])
                    tags = {tag['Key']: tag['Value'] for tag in stack_details['Stacks'][0].get('Tags', [])}
                except ClientError:
                    tags = {}
                
                self.resources.append({
                    'service': 'CloudFormation',
                    'type': 'Stack',
                    'region': region,
                    'id': stack['StackName'],
                    'name': stack['StackName'],
                    'status': stack['StackStatus'],
                    'creation_time': stack['CreationTime'].isoformat(),
                    'tags': tags,
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover CloudFormation resources in {region}: {e}")
    
    def _discover_ecs_resources(self, region: str):
        """Discover ECS resources."""
        try:
            ecs = self.session.client('ecs', region_name=region)
            
            # ECS Clusters
            clusters = ecs.list_clusters()
            for cluster_arn in clusters['clusterArns']:
                cluster_details = ecs.describe_clusters(clusters=[cluster_arn])
                for cluster in cluster_details['clusters']:
                    # Get tags
                    try:
                        tags_response = ecs.list_tags_for_resource(resourceArn=cluster_arn)
                        tags = {tag['key']: tag['value'] for tag in tags_response.get('tags', [])}
                    except ClientError:
                        tags = {}
                    
                    self.resources.append({
                        'service': 'ECS',
                        'type': 'Cluster',
                        'region': region,
                        'id': cluster['clusterName'],
                        'name': cluster['clusterName'],
                        'status': cluster['status'],
                        'running_tasks': cluster['runningTasksCount'],
                        'pending_tasks': cluster['pendingTasksCount'],
                        'active_services': cluster['activeServicesCount'],
                        'tags': tags,
                        'discovered_at': datetime.utcnow().isoformat()
                    })
                    
        except ClientError as e:
            self.logger.warning(f"Failed to discover ECS resources in {region}: {e}")
    
    def _discover_eks_resources(self, region: str):
        """Discover EKS resources."""
        try:
            eks = self.session.client('eks', region_name=region)
            
            clusters = eks.list_clusters()
            for cluster_name in clusters['clusters']:
                cluster_details = eks.describe_cluster(name=cluster_name)
                cluster = cluster_details['cluster']
                
                self.resources.append({
                    'service': 'EKS',
                    'type': 'Cluster',
                    'region': region,
                    'id': cluster['name'],
                    'name': cluster['name'],
                    'status': cluster['status'],
                    'version': cluster['version'],
                    'endpoint': cluster.get('endpoint'),
                    'created_at': cluster['createdAt'].isoformat() if 'createdAt' in cluster else None,
                    'tags': cluster.get('tags', {}),
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover EKS resources in {region}: {e}")
    
    def _discover_cloudwatch_resources(self, region: str):
        """Discover CloudWatch resources."""
        try:
            cw = self.session.client('cloudwatch', region_name=region)
            
            # CloudWatch Alarms
            alarms = cw.describe_alarms()
            for alarm in alarms['MetricAlarms']:
                self.resources.append({
                    'service': 'CloudWatch',
                    'type': 'Alarm',
                    'region': region,
                    'id': alarm['AlarmName'],
                    'name': alarm['AlarmName'],
                    'description': alarm.get('AlarmDescription'),
                    'state': alarm['StateValue'],
                    'metric_name': alarm['MetricName'],
                    'namespace': alarm['Namespace'],
                    'discovered_at': datetime.utcnow().isoformat()
                })
                
        except ClientError as e:
            self.logger.warning(f"Failed to discover CloudWatch resources in {region}: {e}")
    
    def _get_tag_value(self, tags: List[Dict], key: str) -> Optional[str]:
        """Get tag value by key."""
        for tag in tags:
            if tag['Key'] == key:
                return tag['Value']
        return None
    
    def save_to_file(self, filename: str, format_type: str = 'json'):
        """Save resources to file."""
        if format_type.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(self.resources, f, indent=2, default=str)
        elif format_type.lower() == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(self.resources, f, default_flow_style=False, default_style='', allow_unicode=True)
        else:
            raise ValueError("Format must be 'json' or 'yaml'")
        
        self.logger.info(f"Resources saved to {filename}")
    
    def upload_to_s3(self, bucket_name: str, key: str, format_type: str = 'json'):
        """Upload resources to S3."""
        try:
            s3 = self.session.client('s3')
            
            if format_type.lower() == 'json':
                content = json.dumps(self.resources, indent=2, default=str)
                content_type = 'application/json'
            elif format_type.lower() == 'yaml':
                content = yaml.dump(self.resources, default_flow_style=False, default_style='', allow_unicode=True)
                content_type = 'text/yaml'
            else:
                raise ValueError("Format must be 'json' or 'yaml'")
            
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type
            )
            
            self.logger.info(f"Resources uploaded to s3://{bucket_name}/{key}")
            
        except ClientError as e:
            self.logger.error(f"Failed to upload to S3: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description='AWS Resource Inventory Tool')
    parser.add_argument('--regions', nargs='+', help='AWS regions to scan (default: all regions)')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json', 
                       help='Output format (default: json)')
    parser.add_argument('--output', '-o', default='aws_resources', 
                       help='Output filename (without extension)')
    parser.add_argument('--s3-bucket', help='S3 bucket to upload results')
    parser.add_argument('--s3-key', help='S3 key for uploaded file')
    parser.add_argument('--export-excel', action='store_true', 
                       help='Also export to Excel/CSV using the converter utility')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize inventory tool
        inventory = AWSResourceInventory(regions=args.regions)
        
        # Discover resources
        resources = inventory.discover_resources()
        
        if not resources:
            print("No resources found.")
            return
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{args.output}_{timestamp}.{args.format}"
        
        # Save to local file
        inventory.save_to_file(filename, args.format)
        print(f"Inventory saved to {filename}")
        print(f"Total resources discovered: {len(resources)}")
        
        # Upload to S3 if requested
        if args.s3_bucket:
            s3_key = args.s3_key or f"aws-inventory/{filename}"
            inventory.upload_to_s3(args.s3_bucket, s3_key, args.format)
            print(f"Inventory uploaded to s3://{args.s3_bucket}/{s3_key}")
        
        # Export to Excel/CSV if requested
        if args.export_excel:
            print("Exporting to Excel/CSV format...")
            excel_filename = f"{args.output}_{timestamp}.xlsx"
            os.system(f"python bom_converter.py --input {filename} --output {excel_filename} --format excel")
            print(f"Excel export saved to {excel_filename}")
        
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your AWS credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()