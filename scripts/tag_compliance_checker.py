#!/usr/bin/env python3
"""
Comprehensive AWS Tag Compliance Checker
Validates ALL AWS resources against tagging policies using Resource Groups Tagging API.
This version discovers ALL resource types across ALL AWS services.
"""

import argparse
import json
import yaml
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from botocore.exceptions import ClientError, NoCredentialsError
import sys
import os
from colorama import Fore, Style, init
import time

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ComprehensiveTagComplianceChecker:
    def __init__(self, regions: Optional[List[str]] = None, config_file: Optional[str] = None):
        """Initialize the Comprehensive Tag Compliance Checker."""
        self.session = boto3.Session()
        self.regions = regions or self._get_available_regions()
        self.config_file = config_file
        self.tag_policy = self._load_tag_policy()
        self.all_resources = []
        self.compliance_results = {
            'compliant': [],
            'non_compliant': [],
            'untagged': [],
            'summary': {}
        }
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _get_available_regions(self) -> List[str]:
        """Get all available AWS regions with fallback."""
        try:
            ec2 = self.session.client('ec2', region_name='us-east-1')
            regions = ec2.describe_regions()['Regions']
            region_list = [region['RegionName'] for region in regions]
            self.logger.info(f"Successfully retrieved {len(region_list)} AWS regions")
            return region_list
        except Exception as e:
            self.logger.warning(f"Failed to get all regions: {e}")
            self.logger.info("Falling back to default regions: us-east-1, ap-southeast-1")
            return ['us-east-1', 'ap-southeast-1']  # Fallback to key regions
    
    def _load_tag_policy(self) -> Dict[str, Any]:
        """Load tag policy from configuration file."""
        if not self.config_file:
            print(f"{Fore.RED}WARNING: No configuration file specified. Only checking for completely untagged resources.")
            print(f"{Fore.RED}It is recommended to provide a configuration file with at least 1 required tag key.{Style.RESET_ALL}")
            return {"required_tags": []}
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.lower().endswith('.json'):
                    config = json.load(f)
                elif self.config_file.lower().endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f)
                else:
                    # Try to detect format
                    content = f.read()
                    try:
                        config = json.loads(content)
                    except json.JSONDecodeError:
                        config = yaml.safe_load(content)
            
            # Validate configuration structure
            if 'required_tags' not in config:
                raise ValueError("Configuration must contain 'required_tags' section")
            
            if not isinstance(config['required_tags'], list):
                raise ValueError("'required_tags' must be a list")
            
            if len(config['required_tags']) == 0:
                print(f"{Fore.RED}WARNING: Configuration file contains no required tags. Consider adding at least 1 required tag key.{Style.RESET_ALL}")
            
            self.logger.info(f"Loaded tag policy from {self.config_file}")
            self.logger.info(f"Required tags: {len(config['required_tags'])}")
            
            return config
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file {self.config_file} not found")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def discover_all_resources(self) -> List[Dict[str, Any]]:
        """Discover ALL AWS resources using Resource Groups Tagging API and other comprehensive methods."""
        self.logger.info("Starting comprehensive AWS resource discovery across ALL services...")
        
        # Method 1: Use Resource Groups Tagging API for comprehensive discovery
        self._discover_via_resource_groups_tagging_api()
        
        # Method 2: Use AWS Config (if available) for additional resources
        self._discover_via_config_service()
        
        # Method 3: Use CloudTrail to find recently created resources
        self._discover_via_cloudtrail()
        
        # Method 4: Service-specific discovery for resources that might not appear in RGT API
        self._discover_additional_resources()
        
        # Remove duplicates based on ARN
        self._deduplicate_resources()
        
        self.logger.info(f"Comprehensive discovery complete. Found {len(self.all_resources)} unique resources.")
        return self.all_resources
    
    def _discover_via_resource_groups_tagging_api(self):
        """Use Resource Groups Tagging API to discover all taggable resources."""
        self.logger.info("Discovering resources via Resource Groups Tagging API...")
        
        for region in self.regions:
            try:
                rgt_client = self.session.client('resourcegroupstaggingapi', region_name=region)
                
                # Get all resources (paginated)
                paginator = rgt_client.get_paginator('get_resources')
                
                for page in paginator.paginate():
                    for resource in page.get('ResourceTagMappingList', []):
                        try:
                            # Parse ARN to extract service and resource type
                            arn = resource['ResourceARN']
                            arn_parts = arn.split(':')
                            
                            if len(arn_parts) >= 6:
                                service = arn_parts[2]
                                region_from_arn = arn_parts[3]
                                account_id = arn_parts[4]
                                resource_part = arn_parts[5]
                                
                                # Extract resource type and ID
                                if '/' in resource_part:
                                    resource_type, resource_id = resource_part.split('/', 1)
                                else:
                                    resource_type = resource_part
                                    resource_id = resource_part
                                
                                # Convert tag list to dictionary
                                tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                                
                                # Get additional resource details if possible
                                additional_info = self._get_additional_resource_info(service, resource_type, resource_id, region, arn)
                                
                                resource_info = {
                                    'service': service.upper(),
                                    'type': self._normalize_resource_type(service, resource_type),
                                    'region': region_from_arn or region,
                                    'id': resource_id,
                                    'name': self._extract_resource_name(tags, additional_info),
                                    'arn': arn,
                                    'tags': tags,
                                    'account_id': account_id,
                                    'discovered_via': 'ResourceGroupsTaggingAPI',
                                    'discovered_at': datetime.utcnow().isoformat()
                                }
                                
                                # Add additional info if available
                                if additional_info:
                                    resource_info.update(additional_info)
                                
                                self.all_resources.append(resource_info)
                        
                        except Exception as e:
                            self.logger.warning(f"Error processing resource {resource.get('ResourceARN', 'unknown')}: {e}")
                            continue
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'UnauthorizedOperation':
                    self.logger.warning(f"No permission for Resource Groups Tagging API in {region}")
                else:
                    self.logger.warning(f"Failed to discover resources via RGT API in {region}: {e}")
            except Exception as e:
                self.logger.warning(f"Unexpected error in RGT API discovery for {region}: {e}")
    
    def _discover_via_config_service(self):
        """Use AWS Config to discover additional resources."""
        self.logger.info("Discovering resources via AWS Config...")
        
        for region in self.regions:
            try:
                config_client = self.session.client('config', region_name=region)
                
                # Get all resource types tracked by Config
                paginator = config_client.get_paginator('list_discovered_resources')
                
                # Get list of supported resource types
                try:
                    supported_types = config_client.describe_configuration_recorder_status()
                    if not supported_types.get('ConfigurationRecordersStatus'):
                        continue
                except:
                    continue
                
                # List all resource types
                try:
                    resource_types_response = config_client.list_aggregate_discovered_resources(
                        ConfigurationAggregatorName='default',  # Try default aggregator
                        ResourceType='AWS::AllSupported'
                    )
                except:
                    # If no aggregator, get resource types differently
                    try:
                        # Get supported resource types
                        supported_types = [
                            'AWS::EC2::Instance', 'AWS::EC2::Volume', 'AWS::EC2::SecurityGroup',
                            'AWS::S3::Bucket', 'AWS::RDS::DBInstance', 'AWS::Lambda::Function',
                            'AWS::IAM::Role', 'AWS::IAM::User', 'AWS::VPC::VPC', 'AWS::VPC::Subnet',
                            'AWS::CloudFormation::Stack', 'AWS::ECS::Cluster', 'AWS::EKS::Cluster',
                            'AWS::CloudWatch::Alarm', 'AWS::SNS::Topic', 'AWS::SQS::Queue',
                            'AWS::DynamoDB::Table', 'AWS::ElastiCache::CacheCluster',
                            'AWS::Elasticsearch::Domain', 'AWS::KMS::Key', 'AWS::Route53::HostedZone'
                        ]
                        
                        for resource_type in supported_types:
                            try:
                                for page in paginator.paginate(resourceType=resource_type):
                                    for resource in page.get('resourceIdentifiers', []):
                                        # Get detailed resource configuration
                                        try:
                                            config_item = config_client.get_resource_config_history(
                                                resourceType=resource_type,
                                                resourceId=resource['resourceId']
                                            )
                                            
                                            if config_item.get('configurationItems'):
                                                item = config_item['configurationItems'][0]
                                                tags = item.get('tags', {})
                                                
                                                resource_info = {
                                                    'service': resource_type.split('::')[1],
                                                    'type': resource_type.split('::')[2],
                                                    'region': region,
                                                    'id': resource['resourceId'],
                                                    'name': resource.get('resourceName', resource['resourceId']),
                                                    'arn': item.get('arn', f"arn:aws:{resource_type.split('::')[1].lower()}:{region}:{item.get('accountId', '')}:{resource['resourceId']}"),
                                                    'tags': tags,
                                                    'discovered_via': 'AWSConfig',
                                                    'discovered_at': datetime.utcnow().isoformat(),
                                                    'resource_type': resource_type,
                                                    'configuration_state': item.get('configurationItemStatus')
                                                }
                                                
                                                self.all_resources.append(resource_info)
                                        
                                        except Exception as e:
                                            self.logger.debug(f"Could not get config for {resource_type} {resource.get('resourceId')}: {e}")
                                            continue
                            
                            except ClientError as e:
                                if 'ResourceNotDiscoveredException' not in str(e):
                                    self.logger.debug(f"Could not discover {resource_type} in {region}: {e}")
                                continue
                    
                    except Exception as e:
                        self.logger.debug(f"Config discovery failed in {region}: {e}")
                        continue
            
            except ClientError as e:
                if 'NoSuchConfigurationRecorderException' in str(e):
                    self.logger.debug(f"AWS Config not enabled in {region}")
                else:
                    self.logger.debug(f"Failed to use AWS Config in {region}: {e}")
            except Exception as e:
                self.logger.debug(f"Unexpected error in Config discovery for {region}: {e}")
    
    def _discover_via_cloudtrail(self):
        """Use CloudTrail to find recently created resources."""
        self.logger.info("Discovering recently created resources via CloudTrail...")
        
        try:
            cloudtrail = self.session.client('cloudtrail', region_name='us-east-1')  # CloudTrail events are global
            
            # Look for CreateXXX events in the last 7 days
            end_time = datetime.utcnow()
            start_time = end_time.replace(day=end_time.day - 7) if end_time.day > 7 else end_time.replace(month=end_time.month - 1, day=30)
            
            paginator = cloudtrail.get_paginator('lookup_events')
            
            for page in paginator.paginate(
                StartTime=start_time,
                EndTime=end_time,
                MaxItems=1000  # Limit to avoid too many API calls
            ):
                for event in page.get('Events', []):
                    event_name = event.get('EventName', '')
                    if event_name.startswith('Create') or event_name.startswith('Run'):
                        try:
                            # Extract resource information from CloudTrail event
                            resources = event.get('Resources', [])
                            for resource in resources:
                                resource_name = resource.get('ResourceName', '')
                                resource_type = resource.get('ResourceType', '')
                                
                                if resource_name and resource_type:
                                    # Try to construct basic resource info
                                    resource_info = self._construct_resource_from_cloudtrail(event, resource)
                                    if resource_info:
                                        self.all_resources.append(resource_info)
                        
                        except Exception as e:
                            self.logger.debug(f"Could not process CloudTrail event {event_name}: {e}")
                            continue
        
        except ClientError as e:
            self.logger.debug(f"CloudTrail discovery failed: {e}")
        except Exception as e:
            self.logger.debug(f"Unexpected error in CloudTrail discovery: {e}")
    
    def _discover_additional_resources(self):
        """Discover additional resources that might not appear in RGT API."""
        self.logger.info("Discovering additional resources via service-specific APIs...")
        
        # Add service-specific discovery for resources that might not be taggable
        # but still need to be tracked for compliance purposes
        
        for region in self.regions:
            # CloudWatch Logs
            self._discover_cloudwatch_logs(region)
            
            # Route53 (global service)
            if region == 'us-east-1':
                self._discover_route53_resources()
            
            # API Gateway
            self._discover_apigateway_resources(region)
            
            # ElastiCache
            self._discover_elasticache_resources(region)
            
            # DynamoDB
            self._discover_dynamodb_resources(region)
            
            # SNS/SQS
            self._discover_sns_sqs_resources(region)
            
            # KMS
            self._discover_kms_resources(region)
            
            # Elasticsearch/OpenSearch
            self._discover_elasticsearch_resources(region)
    
    def _discover_cloudwatch_logs(self, region: str):
        """Discover CloudWatch Log Groups."""
        try:
            logs_client = self.session.client('logs', region_name=region)
            paginator = logs_client.get_paginator('describe_log_groups')
            
            for page in paginator.paginate():
                for log_group in page.get('logGroups', []):
                    # Get tags
                    try:
                        tags_response = logs_client.list_tags_log_group(logGroupName=log_group['logGroupName'])
                        tags = tags_response.get('tags', {})
                    except:
                        tags = {}
                    
                    resource_info = {
                        'service': 'LOGS',
                        'type': 'LogGroup',
                        'region': region,
                        'id': log_group['logGroupName'],
                        'name': log_group['logGroupName'],
                        'arn': log_group['arn'],
                        'tags': tags,
                        'discovered_via': 'ServiceSpecificAPI',
                        'discovered_at': datetime.utcnow().isoformat(),
                        'retention_days': log_group.get('retentionInDays'),
                        'creation_time': log_group.get('creationTime')
                    }
                    
                    self.all_resources.append(resource_info)
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover CloudWatch Logs in {region}: {e}")
    
    def _discover_route53_resources(self):
        """Discover Route53 resources (global service)."""
        try:
            route53 = self.session.client('route53')
            
            # Hosted Zones
            paginator = route53.get_paginator('list_hosted_zones')
            for page in paginator.paginate():
                for zone in page.get('HostedZones', []):
                    # Get tags
                    try:
                        tags_response = route53.list_tags_for_resource(
                            ResourceType='hostedzone',
                            ResourceId=zone['Id'].split('/')[-1]
                        )
                        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                    except:
                        tags = {}
                    
                    resource_info = {
                        'service': 'ROUTE53',
                        'type': 'HostedZone',
                        'region': 'global',
                        'id': zone['Id'],
                        'name': zone['Name'],
                        'arn': f"arn:aws:route53:::hostedzone/{zone['Id'].split('/')[-1]}",
                        'tags': tags,
                        'discovered_via': 'ServiceSpecificAPI',
                        'discovered_at': datetime.utcnow().isoformat(),
                        'record_count': zone.get('ResourceRecordSetCount')
                    }
                    
                    self.all_resources.append(resource_info)
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover Route53 resources: {e}")
    
    def _discover_apigateway_resources(self, region: str):
        """Discover API Gateway resources."""
        try:
            # API Gateway v1
            apigw = self.session.client('apigateway', region_name=region)
            
            apis = apigw.get_rest_apis()
            for api in apis.get('items', []):
                # Get tags
                try:
                    tags_response = apigw.get_tags(resourceArn=f"arn:aws:apigateway:{region}::/restapis/{api['id']}")
                    tags = tags_response.get('tags', {})
                except:
                    tags = {}
                
                resource_info = {
                    'service': 'APIGATEWAY',
                    'type': 'RestApi',
                    'region': region,
                    'id': api['id'],
                    'name': api.get('name', api['id']),
                    'arn': f"arn:aws:apigateway:{region}::/restapis/{api['id']}",
                    'tags': tags,
                    'discovered_via': 'ServiceSpecificAPI',
                    'discovered_at': datetime.utcnow().isoformat(),
                    'api_version': api.get('version'),
                    'created_date': api.get('createdDate', '').isoformat() if api.get('createdDate') else None
                }
                
                self.all_resources.append(resource_info)
            
            # API Gateway v2
            try:
                apigwv2 = self.session.client('apigatewayv2', region_name=region)
                apis_v2 = apigwv2.get_apis()
                
                for api in apis_v2.get('Items', []):
                    try:
                        tags_response = apigwv2.get_tags(ResourceArn=api['ApiId'])
                        tags = tags_response.get('Tags', {})
                    except:
                        tags = {}
                    
                    resource_info = {
                        'service': 'APIGATEWAY',
                        'type': 'Api',
                        'region': region,
                        'id': api['ApiId'],
                        'name': api.get('Name', api['ApiId']),
                        'arn': f"arn:aws:apigateway:{region}::/apis/{api['ApiId']}",
                        'tags': tags,
                        'discovered_via': 'ServiceSpecificAPI',
                        'discovered_at': datetime.utcnow().isoformat(),
                        'protocol_type': api.get('ProtocolType'),
                        'api_endpoint': api.get('ApiEndpoint')
                    }
                    
                    self.all_resources.append(resource_info)
            except:
                pass  # API Gateway v2 might not be available in all regions
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover API Gateway resources in {region}: {e}")
    
    def _discover_elasticache_resources(self, region: str):
        """Discover ElastiCache resources."""
        try:
            elasticache = self.session.client('elasticache', region_name=region)
            
            # Cache Clusters
            paginator = elasticache.get_paginator('describe_cache_clusters')
            for page in paginator.paginate():
                for cluster in page.get('CacheClusters', []):
                    # Get tags
                    try:
                        tags_response = elasticache.list_tags_for_resource(ResourceName=cluster['CacheClusterArn'])
                        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
                    except:
                        tags = {}
                    
                    resource_info = {
                        'service': 'ELASTICACHE',
                        'type': 'CacheCluster',
                        'region': region,
                        'id': cluster['CacheClusterId'],
                        'name': cluster['CacheClusterId'],
                        'arn': cluster.get('CacheClusterArn', f"arn:aws:elasticache:{region}:{self.session.get_credentials().access_key}:cluster:{cluster['CacheClusterId']}"),
                        'tags': tags,
                        'discovered_via': 'ServiceSpecificAPI',
                        'discovered_at': datetime.utcnow().isoformat(),
                        'engine': cluster.get('Engine'),
                        'status': cluster.get('CacheClusterStatus')
                    }
                    
                    self.all_resources.append(resource_info)
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover ElastiCache resources in {region}: {e}")
    
    def _discover_dynamodb_resources(self, region: str):
        """Discover DynamoDB resources."""
        try:
            dynamodb = self.session.client('dynamodb', region_name=region)
            
            # Tables
            paginator = dynamodb.get_paginator('list_tables')
            for page in paginator.paginate():
                for table_name in page.get('TableNames', []):
                    try:
                        # Get table details
                        table_details = dynamodb.describe_table(TableName=table_name)
                        table = table_details['Table']
                        
                        # Get tags
                        try:
                            tags_response = dynamodb.list_tags_of_resource(ResourceArn=table['TableArn'])
                            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                        except:
                            tags = {}
                        
                        resource_info = {
                            'service': 'DYNAMODB',
                            'type': 'Table',
                            'region': region,
                            'id': table_name,
                            'name': table_name,
                            'arn': table['TableArn'],
                            'tags': tags,
                            'discovered_via': 'ServiceSpecificAPI',
                            'discovered_at': datetime.utcnow().isoformat(),
                            'status': table.get('TableStatus'),
                            'item_count': table.get('ItemCount'),
                            'table_size': table.get('TableSizeBytes')
                        }
                        
                        self.all_resources.append(resource_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Could not get details for DynamoDB table {table_name}: {e}")
                        continue
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover DynamoDB resources in {region}: {e}")
    
    def _discover_sns_sqs_resources(self, region: str):
        """Discover SNS and SQS resources."""
        try:
            # SNS Topics
            sns = self.session.client('sns', region_name=region)
            paginator = sns.get_paginator('list_topics')
            
            for page in paginator.paginate():
                for topic in page.get('Topics', []):
                    topic_arn = topic['TopicArn']
                    
                    # Get tags
                    try:
                        tags_response = sns.list_tags_for_resource(ResourceArn=topic_arn)
                        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                    except:
                        tags = {}
                    
                    resource_info = {
                        'service': 'SNS',
                        'type': 'Topic',
                        'region': region,
                        'id': topic_arn.split(':')[-1],
                        'name': topic_arn.split(':')[-1],
                        'arn': topic_arn,
                        'tags': tags,
                        'discovered_via': 'ServiceSpecificAPI',
                        'discovered_at': datetime.utcnow().isoformat()
                    }
                    
                    self.all_resources.append(resource_info)
            
            # SQS Queues
            sqs = self.session.client('sqs', region_name=region)
            paginator = sqs.get_paginator('list_queues')
            
            for page in paginator.paginate():
                for queue_url in page.get('QueueUrls', []):
                    try:
                        # Get queue attributes
                        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
                        queue_arn = attrs['Attributes'].get('QueueArn')
                        
                        # Get tags
                        try:
                            tags_response = sqs.list_queue_tags(QueueUrl=queue_url)
                            tags = tags_response.get('Tags', {})
                        except:
                            tags = {}
                        
                        queue_name = queue_url.split('/')[-1]
                        
                        resource_info = {
                            'service': 'SQS',
                            'type': 'Queue',
                            'region': region,
                            'id': queue_name,
                            'name': queue_name,
                            'arn': queue_arn,
                            'tags': tags,
                            'discovered_via': 'ServiceSpecificAPI',
                            'discovered_at': datetime.utcnow().isoformat(),
                            'queue_url': queue_url,
                            'message_retention': attrs['Attributes'].get('MessageRetentionPeriod')
                        }
                        
                        self.all_resources.append(resource_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Could not get details for SQS queue {queue_url}: {e}")
                        continue
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover SNS/SQS resources in {region}: {e}")
    
    def _discover_kms_resources(self, region: str):
        """Discover KMS resources."""
        try:
            kms = self.session.client('kms', region_name=region)
            paginator = kms.get_paginator('list_keys')
            
            for page in paginator.paginate():
                for key in page.get('Keys', []):
                    key_id = key['KeyId']
                    
                    try:
                        # Get key details
                        key_details = kms.describe_key(KeyId=key_id)
                        key_metadata = key_details['KeyMetadata']
                        
                        # Skip AWS managed keys
                        if key_metadata.get('KeyManager') == 'AWS':
                            continue
                        
                        # Get tags
                        try:
                            tags_response = kms.list_resource_tags(KeyId=key_id)
                            tags = {tag['TagKey']: tag['TagValue'] for tag in tags_response.get('Tags', [])}
                        except:
                            tags = {}
                        
                        resource_info = {
                            'service': 'KMS',
                            'type': 'Key',
                            'region': region,
                            'id': key_id,
                            'name': key_metadata.get('Description', key_id),
                            'arn': key_metadata['Arn'],
                            'tags': tags,
                            'discovered_via': 'ServiceSpecificAPI',
                            'discovered_at': datetime.utcnow().isoformat(),
                            'key_usage': key_metadata.get('KeyUsage'),
                            'key_state': key_metadata.get('KeyState')
                        }
                        
                        self.all_resources.append(resource_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Could not get details for KMS key {key_id}: {e}")
                        continue
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover KMS resources in {region}: {e}")
    
    def _discover_elasticsearch_resources(self, region: str):
        """Discover Elasticsearch/OpenSearch resources."""
        try:
            # Try OpenSearch first (newer service)
            try:
                opensearch = self.session.client('opensearch', region_name=region)
                domains = opensearch.list_domain_names()
                
                for domain in domains.get('DomainNames', []):
                    domain_name = domain['DomainName']
                    
                    try:
                        # Get domain details
                        domain_details = opensearch.describe_domain(DomainName=domain_name)
                        domain_status = domain_details['DomainStatus']
                        
                        # Get tags
                        try:
                            tags_response = opensearch.list_tags(ARN=domain_status['ARN'])
                            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
                        except:
                            tags = {}
                        
                        resource_info = {
                            'service': 'OPENSEARCH',
                            'type': 'Domain',
                            'region': region,
                            'id': domain_name,
                            'name': domain_name,
                            'arn': domain_status['ARN'],
                            'tags': tags,
                            'discovered_via': 'ServiceSpecificAPI',
                            'discovered_at': datetime.utcnow().isoformat(),
                            'engine_version': domain_status.get('EngineVersion'),
                            'processing': domain_status.get('Processing')
                        }
                        
                        self.all_resources.append(resource_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Could not get details for OpenSearch domain {domain_name}: {e}")
                        continue
            
            except:
                # Fallback to Elasticsearch service
                es = self.session.client('es', region_name=region)
                domains = es.list_domain_names()
                
                for domain in domains.get('DomainNames', []):
                    domain_name = domain['DomainName']
                    
                    try:
                        # Get domain details
                        domain_details = es.describe_elasticsearch_domain(DomainName=domain_name)
                        domain_status = domain_details['DomainStatus']
                        
                        # Get tags
                        try:
                            tags_response = es.list_tags(ARN=domain_status['ARN'])
                            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
                        except:
                            tags = {}
                        
                        resource_info = {
                            'service': 'ELASTICSEARCH',
                            'type': 'Domain',
                            'region': region,
                            'id': domain_name,
                            'name': domain_name,
                            'arn': domain_status['ARN'],
                            'tags': tags,
                            'discovered_via': 'ServiceSpecificAPI',
                            'discovered_at': datetime.utcnow().isoformat(),
                            'elasticsearch_version': domain_status.get('ElasticsearchVersion'),
                            'processing': domain_status.get('Processing')
                        }
                        
                        self.all_resources.append(resource_info)
                    
                    except Exception as e:
                        self.logger.debug(f"Could not get details for Elasticsearch domain {domain_name}: {e}")
                        continue
        
        except ClientError as e:
            self.logger.debug(f"Failed to discover Elasticsearch/OpenSearch resources in {region}: {e}")
    
    def _get_additional_resource_info(self, service: str, resource_type: str, resource_id: str, region: str, arn: str) -> Dict[str, Any]:
        """Get additional information about a resource if possible."""
        try:
            # Add service-specific additional info gathering
            # This is a simplified version - you could expand this significantly
            additional_info = {}
            
            if service == 'ec2':
                if resource_type == 'instance':
                    try:
                        ec2 = self.session.client('ec2', region_name=region)
                        instances = ec2.describe_instances(InstanceIds=[resource_id])
                        if instances['Reservations']:
                            instance = instances['Reservations'][0]['Instances'][0]
                            additional_info.update({
                                'state': instance['State']['Name'],
                                'instance_type': instance['InstanceType'],
                                'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else None
                            })
                    except:
                        pass
            
            return additional_info
        
        except:
            return {}
    
    def _normalize_resource_type(self, service: str, resource_type: str) -> str:
        """Normalize resource type names for consistency."""
        # Normalize common variations
        type_mappings = {
            'instance': 'Instance',
            'volume': 'Volume',
            'security-group': 'SecurityGroup',
            'vpc': 'VPC',
            'subnet': 'Subnet',
            'bucket': 'Bucket',
            'function': 'Function',
            'role': 'Role',
            'user': 'User',
            'stack': 'Stack',
            'cluster': 'Cluster',
            'alarm': 'Alarm',
            'topic': 'Topic',
            'queue': 'Queue',
            'table': 'Table',
            'key': 'Key',
            'domain': 'Domain',
            'log-group': 'LogGroup'
        }
        
        return type_mappings.get(resource_type.lower(), resource_type.title())
    
    def _extract_resource_name(self, tags: Dict[str, str], additional_info: Dict[str, Any]) -> str:
        """Extract a meaningful name for the resource."""
        # Try to get name from tags first
        name = tags.get('Name', '')
        if name:
            return name
        
        # Try common name tags
        for tag_key in ['name', 'Name', 'NAME', 'ResourceName', 'resource-name']:
            if tag_key in tags:
                return tags[tag_key]
        
        # Try to get name from additional info
        if additional_info and 'name' in additional_info:
            return additional_info['name']
        
        return ''
    
    def _construct_resource_from_cloudtrail(self, event: Dict[str, Any], resource: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Construct basic resource info from CloudTrail event."""
        try:
            resource_name = resource.get('ResourceName', '')
            resource_type = resource.get('ResourceType', '')
            
            if not resource_name or not resource_type:
                return None
            
            # Try to extract service from resource type or event
            service = 'UNKNOWN'
            if '::' in resource_type:
                service = resource_type.split('::')[1]
            elif 'ServiceName' in event:
                service = event['ServiceName']
            elif 'EventSource' in event:
                service = event['EventSource'].split('.')[0]
            
            return {
                'service': service.upper(),
                'type': resource_type.split('::')[-1] if '::' in resource_type else resource_type,
                'region': event.get('AwsRegion', 'unknown'),
                'id': resource_name,
                'name': resource_name,
                'arn': resource_name if resource_name.startswith('arn:') else f"arn:aws:{service.lower()}:{event.get('AwsRegion', '')}:{event.get('RecipientAccountId', '')}:{resource_name}",
                'tags': {},  # CloudTrail doesn't provide tag info
                'discovered_via': 'CloudTrail',
                'discovered_at': datetime.utcnow().isoformat(),
                'event_time': event.get('EventTime', '').isoformat() if event.get('EventTime') else None,
                'event_name': event.get('EventName', '')
            }
        
        except Exception as e:
            self.logger.debug(f"Could not construct resource from CloudTrail event: {e}")
            return None
    
    def _deduplicate_resources(self):
        """Remove duplicate resources based on ARN."""
        seen_arns = set()
        unique_resources = []
        
        for resource in self.all_resources:
            arn = resource.get('arn', '')
            if arn and arn not in seen_arns:
                seen_arns.add(arn)
                unique_resources.append(resource)
            elif not arn:
                # If no ARN, use service+type+region+id as unique key
                unique_key = f"{resource.get('service', '')}:{resource.get('type', '')}:{resource.get('region', '')}:{resource.get('id', '')}"
                if unique_key not in seen_arns:
                    seen_arns.add(unique_key)
                    unique_resources.append(resource)
        
        self.all_resources = unique_resources
        self.logger.info(f"After deduplication: {len(self.all_resources)} unique resources")
    
    def check_compliance(self) -> Dict[str, Any]:
        """Check tag compliance for all discovered resources."""
        self.logger.info("Checking tag compliance for all discovered resources...")
        
        for resource in self.all_resources:
            compliance_info = self._check_resource_compliance(resource)
            self._categorize_compliance(compliance_info)
        
        self._generate_summary()
        self.logger.info("Tag compliance check complete.")
        return self.compliance_results
    
    def _check_resource_compliance(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a resource is compliant with the tag policy."""
        resource_tags = resource.get('tags', {})
        compliance_info = {
            'resource': resource,
            'missing_tags': [],
            'incorrect_values': [],
            'is_compliant': True,
            'is_untagged': len(resource_tags) == 0
        }
        
        # If no tags at all, mark as untagged
        if len(resource_tags) == 0:
            compliance_info['is_compliant'] = False
            return compliance_info
        
        # Check required tags if policy is defined
        if self.tag_policy and 'required_tags' in self.tag_policy:
            for tag_requirement in self.tag_policy['required_tags']:
                if isinstance(tag_requirement, str):
                    # Simple required key
                    tag_key = tag_requirement
                    if tag_key not in resource_tags:
                        compliance_info['missing_tags'].append(tag_key)
                        compliance_info['is_compliant'] = False
                
                elif isinstance(tag_requirement, dict):
                    # Key with required/allowed values
                    tag_key = tag_requirement.get('key')
                    required_values = tag_requirement.get('required_values', [])
                    allowed_values = tag_requirement.get('allowed_values', [])
                    
                    if not tag_key:
                        continue
                    
                    if tag_key not in resource_tags:
                        compliance_info['missing_tags'].append(tag_key)
                        compliance_info['is_compliant'] = False
                    else:
                        resource_value = resource_tags[tag_key]
                        
                        # Check required values
                        if required_values and resource_value not in required_values:
                            compliance_info['incorrect_values'].append({
                                'key': tag_key,
                                'current_value': resource_value,
                                'required_values': required_values
                            })
                            compliance_info['is_compliant'] = False
                        
                        # Check allowed values
                        if allowed_values and resource_value not in allowed_values:
                            compliance_info['incorrect_values'].append({
                                'key': tag_key,
                                'current_value': resource_value,
                                'allowed_values': allowed_values
                            })
                            compliance_info['is_compliant'] = False
        
        return compliance_info
    
    def _categorize_compliance(self, compliance: Dict[str, Any]):
        """Categorize compliance results."""
        if compliance['is_untagged']:
            self.compliance_results['untagged'].append(compliance)
        elif compliance['is_compliant']:
            self.compliance_results['compliant'].append(compliance)
        else:
            self.compliance_results['non_compliant'].append(compliance)
    
    def _generate_summary(self):
        """Generate compliance summary."""
        total_resources = (
            len(self.compliance_results['compliant']) + 
            len(self.compliance_results['non_compliant']) + 
            len(self.compliance_results['untagged'])
        )
        
        # Generate service breakdown
        service_breakdown = {}
        for category in ['compliant', 'non_compliant', 'untagged']:
            for item in self.compliance_results[category]:
                service = item['resource']['service']
                if service not in service_breakdown:
                    service_breakdown[service] = {'compliant': 0, 'non_compliant': 0, 'untagged': 0, 'total': 0}
                service_breakdown[service][category] += 1
                service_breakdown[service]['total'] += 1
        
        self.compliance_results['summary'] = {
            'total_resources': total_resources,
            'compliant_count': len(self.compliance_results['compliant']),
            'non_compliant_count': len(self.compliance_results['non_compliant']),
            'untagged_count': len(self.compliance_results['untagged']),
            'compliance_percentage': (len(self.compliance_results['compliant']) / total_resources * 100) if total_resources > 0 else 0,
            'scan_date': datetime.utcnow().isoformat(),
            'regions_scanned': self.regions,
            'tag_policy_file': self.config_file,
            'tag_policy': self.tag_policy,
            'service_breakdown': service_breakdown,
            'discovery_methods': ['ResourceGroupsTaggingAPI', 'AWSConfig', 'CloudTrail', 'ServiceSpecificAPI']
        }
    
    def print_summary(self):
        """Print comprehensive compliance summary to console."""
        summary = self.compliance_results['summary']
        
        print(f"\n{Fore.CYAN}=== COMPREHENSIVE AWS TAG COMPLIANCE REPORT ==={Style.RESET_ALL}")
        print(f"Scan Date: {summary['scan_date']}")
        print(f"Regions Scanned: {', '.join(summary['regions_scanned'])}")
        print(f"Tag Policy File: {summary.get('tag_policy_file', 'None (checking untagged only)')}")
        print(f"Discovery Methods: {', '.join(summary['discovery_methods'])}")
        print()
        
        print(f"Total Resources Discovered: {summary['total_resources']}")
        print(f"{Fore.GREEN}Compliant: {summary['compliant_count']}{Style.RESET_ALL}")
        print(f"{Fore.RED}Non-Compliant: {summary['non_compliant_count']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Untagged: {summary['untagged_count']}{Style.RESET_ALL}")
        print(f"Overall Compliance Rate: {summary['compliance_percentage']:.1f}%")
        print()
        
        # Service breakdown
        if summary.get('service_breakdown'):
            print(f"{Fore.CYAN}COMPLIANCE BY SERVICE:{Style.RESET_ALL}")
            print(f"{'Service':<20} {'Total':<8} {'Compliant':<10} {'Non-Compliant':<15} {'Untagged':<10} {'Rate':<6}")
            print("-" * 75)
            
            for service, stats in sorted(summary['service_breakdown'].items()):
                rate = (stats['compliant'] / stats['total'] * 100) if stats['total'] > 0 else 0
                color = Fore.GREEN if rate > 80 else Fore.YELLOW if rate > 50 else Fore.RED
                print(f"{service:<20} {stats['total']:<8} {stats['compliant']:<10} {stats['non_compliant']:<15} {stats['untagged']:<10} {color}{rate:.1f}%{Style.RESET_ALL}")
            print()
        
        # Show non-compliant resources summary
        if summary['non_compliant_count'] > 0:
            print(f"{Fore.RED}NON-COMPLIANT RESOURCES BY SERVICE:{Style.RESET_ALL}")
            service_counts = {}
            for item in self.compliance_results['non_compliant']:
                service = item['resource']['service']
                service_counts[service] = service_counts.get(service, 0) + 1
            
            for service, count in sorted(service_counts.items()):
                print(f"  {service}: {count} resources")
            print()
        
        # Show untagged resources summary
        if summary['untagged_count'] > 0:
            print(f"{Fore.YELLOW}UNTAGGED RESOURCES BY SERVICE:{Style.RESET_ALL}")
            service_counts = {}
            for item in self.compliance_results['untagged']:
                service = item['resource']['service']
                service_counts[service] = service_counts.get(service, 0) + 1
            
            for service, count in sorted(service_counts.items()):
                print(f"  {service}: {count} resources")
            print()
        
        # Show missing tags summary
        if self.tag_policy and 'required_tags' in self.tag_policy:
            missing_tags = {}
            for item in self.compliance_results['non_compliant']:
                for tag in item.get('missing_tags', []):
                    missing_tags[tag] = missing_tags.get(tag, 0) + 1
            
            if missing_tags:
                print(f"{Fore.RED}MOST COMMONLY MISSING TAGS:{Style.RESET_ALL}")
                for tag, count in sorted(missing_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {tag}: missing from {count} resources")
                print()
    
    def save_report(self, filename: str, format_type: str = 'json'):
        """Save comprehensive compliance report to file."""
        report_data = {
            'summary': self.compliance_results['summary'],
            'compliant_resources': [item['resource'] for item in self.compliance_results['compliant']],
            'non_compliant_resources': self.compliance_results['non_compliant'],
            'untagged_resources': [item['resource'] for item in self.compliance_results['untagged']],
            'all_discovered_resources': self.all_resources
        }
        
        if format_type.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        elif format_type.lower() == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(report_data, f, default_flow_style=False, default_style='', allow_unicode=True)
        else:
            raise ValueError("Format must be 'json' or 'yaml'")
        
        self.logger.info(f"Comprehensive compliance report saved to {filename}")
    
    def upload_to_s3(self, bucket_name: str, key: str, format_type: str = 'json'):
        """Upload comprehensive compliance report to S3."""
        try:
            s3 = self.session.client('s3')
            
            report_data = {
                'summary': self.compliance_results['summary'],
                'compliant_resources': [item['resource'] for item in self.compliance_results['compliant']],
                'non_compliant_resources': self.compliance_results['non_compliant'],
                'untagged_resources': [item['resource'] for item in self.compliance_results['untagged']],
                'all_discovered_resources': self.all_resources
            }
            
            if format_type.lower() == 'json':
                content = json.dumps(report_data, indent=2, default=str)
                content_type = 'application/json'
            elif format_type.lower() == 'yaml':
                content = yaml.dump(report_data, default_flow_style=False, default_style='', allow_unicode=True)
                content_type = 'text/yaml'
            else:
                raise ValueError("Format must be 'json' or 'yaml'")
            
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type
            )
            
            self.logger.info(f"Comprehensive compliance report uploaded to s3://{bucket_name}/{key}")
            
        except ClientError as e:
            self.logger.error(f"Failed to upload to S3: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description='Comprehensive AWS Tag Compliance Checker - Discovers ALL AWS Resources')
    parser.add_argument('--config', '-c', help='Tag policy configuration file (JSON or YAML)')
    parser.add_argument('--regions', nargs='+', help='AWS regions to scan (default: all regions)')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json', 
                       help='Output format (default: json)')
    parser.add_argument('--output', '-o', default='comprehensive_tag_compliance_report', 
                       help='Output filename (without extension)')
    parser.add_argument('--s3-bucket', help='S3 bucket to upload results')
    parser.add_argument('--s3-key', help='S3 key for uploaded file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize comprehensive compliance checker
        print(f"{Fore.CYAN}Initializing Comprehensive AWS Tag Compliance Checker...{Style.RESET_ALL}")
        checker = ComprehensiveTagComplianceChecker(regions=args.regions, config_file=args.config)
        
        # Discover all resources
        print(f"{Fore.CYAN}Discovering ALL AWS resources across your account...{Style.RESET_ALL}")
        all_resources = checker.discover_all_resources()
        
        if not all_resources:
            print(f"{Fore.YELLOW}No resources found.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}Successfully discovered {len(all_resources)} resources{Style.RESET_ALL}")
        
        # Check compliance
        print(f"{Fore.CYAN}Checking tag compliance...{Style.RESET_ALL}")
        results = checker.check_compliance()
        
        # Print summary
        checker.print_summary()
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{args.output}_{timestamp}.{args.format}"
        
        # Save report
        checker.save_report(filename, args.format)
        print(f"Detailed comprehensive compliance report saved to {filename}")
        
        # Upload to S3 if requested
        if args.s3_bucket:
            s3_key = args.s3_key or f"comprehensive-compliance-reports/{filename}"
            checker.upload_to_s3(args.s3_bucket, s3_key, args.format)
            print(f"Report uploaded to s3://{args.s3_bucket}/{s3_key}")
        
        # Exit with error code if non-compliant resources found
        if results['summary']['non_compliant_count'] > 0 or results['summary']['untagged_count'] > 0:
            print(f"\n{Fore.RED}❌ Compliance check failed: {results['summary']['non_compliant_count']} non-compliant and {results['summary']['untagged_count']} untagged resources found{Style.RESET_ALL}")
            sys.exit(1)
        else:
            print(f"\n{Fore.GREEN}✅ All {results['summary']['total_resources']} resources are compliant!{Style.RESET_ALL}")
            sys.exit(0)
        
    except NoCredentialsError:
        print(f"{Fore.RED}Error: AWS credentials not found. Please configure your AWS credentials.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()