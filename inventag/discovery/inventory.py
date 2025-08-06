#!/usr/bin/env python3
"""
AWS Resource Inventory Tool
Discovers and catalogs all AWS resources across services and regions.

Extracted from scripts/aws_resource_inventory.py and enhanced for the unified inventag package.
"""

import json
import yaml
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError


class AWSResourceInventory:
    def __init__(
        self,
        regions: Optional[List[str]] = None,
        session: Optional[boto3.Session] = None,
        services: Optional[List[str]] = None,
        tag_filters: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the AWS Resource Inventory tool."""
        self.session = session or boto3.Session()
        self.resources = []
        self.logger = self._setup_logging()
        self.regions = regions if regions is not None else self._get_available_regions()
        self.services = services  # Specific services to scan, None means all
        self.tag_filters = tag_filters or {}  # Tag filters to apply

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration with fallback handling."""
        try:
            logging.basicConfig(
                level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
            )
            logger = logging.getLogger(__name__)
            logger.info("Logger initialized successfully")
            return logger
        except Exception as e:
            # Fallback to basic logging if setup fails
            fallback_logger = logging.getLogger(__name__)
            fallback_logger.addHandler(logging.StreamHandler())
            fallback_logger.setLevel(logging.INFO)
            fallback_logger.warning(f"Failed to setup logging, using fallback: {e}")
            return fallback_logger

    def _get_available_regions(self) -> List[str]:
        """Get all available AWS regions with fallback."""
        try:
            ec2 = self.session.client("ec2", region_name="us-east-1")
            regions = ec2.describe_regions()["Regions"]
            region_list = [region["RegionName"] for region in regions]
            self.logger.info(f"Successfully retrieved {len(region_list)} AWS regions")
            return region_list
        except Exception as e:
            self.logger.warning(f"Failed to get all regions: {e}")
            self.logger.info(
                "Falling back to default regions: us-east-1, ap-southeast-1"
            )
            return ["us-east-1", "ap-southeast-1"]  # Fallback to key regions

    def discover_resources(self) -> List[Dict[str, Any]]:
        """Discover all AWS resources across regions and services."""
        self.logger.info("Starting comprehensive AWS resource discovery...")

        # Method 1: Use ResourceGroupsTagging API for comprehensive discovery (recommended)
        initial_resource_count = len(self.resources)
        self._discover_via_resource_groups_tagging_api()
        rgt_resource_count = len(self.resources)
        
        # Method 2: Fallback to legacy service-specific discovery if RGT API found few resources
        if rgt_resource_count < 10:  # If RGT API found very few resources, use fallback
            self.logger.warning("ResourceGroupsTagging API found few resources. Using fallback service-specific discovery.")
            self._discover_legacy_service_resources()
        else:
            # Method 2a: Enhance existing resources with service-specific details
            self._discover_service_specific_resources()
        
        # Method 3: Remove duplicates based on ARN
        self._deduplicate_resources()

        self.logger.info(f"Comprehensive discovery complete. Found {len(self.resources)} unique resources.")
        return self.resources

    def _discover_via_resource_groups_tagging_api(self):
        """Use Resource Groups Tagging API to discover all taggable resources."""
        self.logger.info("Discovering resources via ResourceGroupsTagging API...")
        
        for region in self.regions:
            try:
                rgt_client = self.session.client("resourcegroupstaggingapi", region_name=region)
                
                # Get all resources (paginated)
                paginator = rgt_client.get_paginator("get_resources")
                region_resources = 0
                
                for page in paginator.paginate():
                    for resource in page.get("ResourceTagMappingList", []):
                        try:
                            # Parse ARN to extract service and resource info
                            arn = resource["ResourceARN"]
                            arn_parts = arn.split(":")
                            
                            if len(arn_parts) >= 6:
                                service = arn_parts[2]
                                region_from_arn = arn_parts[3] or region
                                account_id = arn_parts[4]
                                resource_part = arn_parts[5]
                                
                                # Extract resource type and ID
                                if "/" in resource_part:
                                    resource_type, resource_id = resource_part.split("/", 1)
                                else:
                                    resource_type = resource_part
                                    resource_id = resource_part
                                
                                # Convert tag list to dictionary
                                tags = {
                                    tag["Key"]: tag["Value"] 
                                    for tag in resource.get("Tags", [])
                                }
                                
                                # Create resource entry
                                resource_entry = {
                                    "service": service.upper(),
                                    "type": self._normalize_resource_type(service, resource_type),
                                    "region": region_from_arn,
                                    "id": resource_id,
                                    "name": tags.get("Name", ""),
                                    "arn": arn,
                                    "account_id": account_id,
                                    "tags": tags,
                                    "discovered_via": "ResourceGroupsTaggingAPI",
                                    "discovered_at": datetime.utcnow().isoformat(),
                                }
                                
                                # Apply service filters if specified
                                if self.services and service.upper() not in [s.upper() for s in self.services]:
                                    continue
                                    
                                # Apply tag filters if specified
                                if self.tag_filters and not self._matches_tag_filters(tags):
                                    continue
                                
                                self.resources.append(resource_entry)
                                region_resources += 1
                                
                        except Exception as e:
                            self.logger.warning(f"Failed to process resource {resource.get('ResourceARN', 'unknown')}: {e}")
                            continue
                
                self.logger.info(f"Found {region_resources} resources in region {region} via ResourceGroupsTagging API")
                
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code == "UnauthorizedOperation":
                    self.logger.warning(f"No permission for ResourceGroupsTagging API in region {region}")
                else:
                    self.logger.warning(f"ResourceGroupsTagging API failed in region {region}: {e}")
            except Exception as e:
                self.logger.warning(f"ResourceGroupsTagging API failed in region {region}: {e}")

    def _normalize_resource_type(self, service: str, resource_type: str) -> str:
        """Normalize resource type names for consistent display."""
        # Common normalizations
        normalizations = {
            # EC2 normalizations
            "instance": "Instance",
            "volume": "EBS Volume", 
            "security-group": "Security Group",
            "snapshot": "EBS Snapshot",
            "image": "AMI",
            "key-pair": "Key Pair",
            "network-interface": "Network Interface",
            "vpc": "VPC",
            "subnet": "Subnet",
            "internet-gateway": "Internet Gateway",
            "nat-gateway": "NAT Gateway",
            "route-table": "Route Table",
            "network-acl": "Network ACL",
            "vpc-endpoint": "VPC Endpoint",
            
            # S3 normalizations
            "bucket": "Bucket",
            "object": "Object",
            
            # Lambda normalizations  
            "function": "Function",
            "layer": "Layer",
            
            # RDS normalizations
            "db": "DB Instance",
            "cluster": "DB Cluster",
            "db-subnet-group": "DB Subnet Group",
            "db-parameter-group": "DB Parameter Group",
            
            # IAM normalizations
            "role": "Role",
            "user": "User", 
            "group": "Group",
            "policy": "Policy",
            
            # CloudFormation
            "stack": "Stack",
            
            # ECS
            "cluster": "Cluster",
            "service": "Service",
            "task-definition": "Task Definition",
            
            # EKS
            "cluster": "Cluster",
            "nodegroup": "Node Group",
        }
        
        resource_type_lower = resource_type.lower()
        if resource_type_lower in normalizations:
            return normalizations[resource_type_lower]
        
        # Capitalize first letter as fallback
        return resource_type.replace("-", " ").replace("_", " ").title()

    def _matches_tag_filters(self, tags: Dict[str, str]) -> bool:
        """Check if resource tags match the specified tag filters."""
        if not self.tag_filters:
            return True
            
        for filter_key, filter_value in self.tag_filters.items():
            if filter_key not in tags:
                return False
            if isinstance(filter_value, str) and tags[filter_key] != filter_value:
                return False
            elif isinstance(filter_value, list) and tags[filter_key] not in filter_value:
                return False
                
        return True

    def _discover_legacy_service_resources(self):
        """Fallback to original hardcoded service discovery if ResourceGroupsTagging API fails."""
        self.logger.info("Using legacy service-specific discovery as fallback...")
        
        for region in self.regions:
            self.logger.info(f"Legacy scanning region: {region}")
            self._discover_ec2_resources_legacy(region)
            self._discover_s3_resources_legacy(region)
            self._discover_rds_resources_legacy(region)
            self._discover_lambda_resources_legacy(region)
            self._discover_iam_resources_legacy(region)
            self._discover_vpc_resources_legacy(region)
            self._discover_cloudformation_resources_legacy(region)
            self._discover_ecs_resources_legacy(region)
            self._discover_eks_resources_legacy(region)
            self._discover_cloudwatch_resources_legacy(region)

    def _discover_service_specific_resources(self):
        """Discover additional resources using service-specific APIs for enhanced details."""
        self.logger.info("Running service-specific discovery for enhanced resource details...")
        
        # Get existing services from ResourceGroupsTagging discovery
        discovered_services = set(r.get("service", "").upper() for r in self.resources)
        
        for region in self.regions:
            self.logger.info(f"Enhanced scanning region: {region}")
            
            # Only run service-specific discovery for services we found via RGT API
            if "EC2" in discovered_services:
                self._enhance_ec2_resources(region)
                self._enhance_vpc_resources(region)  # VPC resources are part of EC2 service
            if "S3" in discovered_services and region == "us-east-1":  # S3 is global
                self._enhance_s3_resources(region)
            if "RDS" in discovered_services:
                self._enhance_rds_resources(region)
            if "LAMBDA" in discovered_services:
                self._enhance_lambda_resources(region)
            if "IAM" in discovered_services and region == "us-east-1":  # IAM is global
                self._enhance_iam_resources(region)
            if "CLOUDFORMATION" in discovered_services:
                self._enhance_cloudformation_resources(region)
            if "ECS" in discovered_services:
                self._enhance_ecs_resources(region)
            if "EKS" in discovered_services:
                self._enhance_eks_resources(region)
            if "CLOUDWATCH" in discovered_services:
                self._enhance_cloudwatch_resources(region)

    def _deduplicate_resources(self):
        """Remove duplicate resources based on ARN."""
        seen_arns = set()
        deduplicated = []
        
        for resource in self.resources:
            arn = resource.get("arn", "")
            # Create a unique key for resources without ARNs
            unique_key = arn or f"{resource.get('service', '')}-{resource.get('type', '')}-{resource.get('id', '')}-{resource.get('region', '')}"
            
            if unique_key not in seen_arns:
                seen_arns.add(unique_key)
                deduplicated.append(resource)
        
        removed_count = len(self.resources) - len(deduplicated)
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} duplicate resources")
            
        self.resources = deduplicated

    # Legacy discovery methods (fallback when ResourceGroupsTagging API fails)
    def _discover_ec2_resources_legacy(self, region: str):
        """Legacy EC2 resource discovery method."""
        return self._enhance_ec2_resources(region)
    
    def _discover_s3_resources_legacy(self, region: str):
        """Legacy S3 resource discovery method."""
        return self._enhance_s3_resources(region)
        
    def _discover_rds_resources_legacy(self, region: str):
        """Legacy RDS resource discovery method."""
        return self._enhance_rds_resources(region)
        
    def _discover_lambda_resources_legacy(self, region: str):
        """Legacy Lambda resource discovery method."""
        return self._enhance_lambda_resources(region)
        
    def _discover_iam_resources_legacy(self, region: str):
        """Legacy IAM resource discovery method."""
        return self._enhance_iam_resources(region)
        
    def _discover_vpc_resources_legacy(self, region: str):
        """Legacy VPC resource discovery method.""" 
        return self._enhance_vpc_resources(region)
        
    def _discover_cloudformation_resources_legacy(self, region: str):
        """Legacy CloudFormation resource discovery method."""
        return self._enhance_cloudformation_resources(region)
        
    def _discover_ecs_resources_legacy(self, region: str):
        """Legacy ECS resource discovery method."""
        return self._enhance_ecs_resources(region)
        
    def _discover_eks_resources_legacy(self, region: str):
        """Legacy EKS resource discovery method."""
        return self._enhance_eks_resources(region)
        
    def _discover_cloudwatch_resources_legacy(self, region: str):
        """Legacy CloudWatch resource discovery method."""
        return self._enhance_cloudwatch_resources(region)

    def _enhance_ec2_resources(self, region: str):
        """Enhance EC2 resources with additional details from EC2 API."""
        try:
            ec2 = self.session.client("ec2", region_name=region)

            # EC2 Instances
            instances = ec2.describe_instances()
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    self.resources.append(
                        {
                            "service": "EC2",
                            "type": "Instance",
                            "region": region,
                            "id": instance["InstanceId"],
                            "name": self._get_tag_value(
                                instance.get("Tags", []), "Name"
                            ),
                            "state": instance["State"]["Name"],
                            "instance_type": instance["InstanceType"],
                            "vpc_id": instance.get("VpcId"),
                            "subnet_id": instance.get("SubnetId"),
                            "launch_time": (
                                instance["LaunchTime"].isoformat()
                                if "LaunchTime" in instance
                                else None
                            ),
                            "tags": {
                                tag["Key"]: tag["Value"]
                                for tag in instance.get("Tags", [])
                            },
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )

            # EBS Volumes
            volumes = ec2.describe_volumes()
            for volume in volumes["Volumes"]:
                self.resources.append(
                    {
                        "service": "EC2",
                        "type": "EBS Volume",
                        "region": region,
                        "id": volume["VolumeId"],
                        "name": self._get_tag_value(volume.get("Tags", []), "Name"),
                        "state": volume["State"],
                        "size": volume["Size"],
                        "volume_type": volume["VolumeType"],
                        "availability_zone": volume["AvailabilityZone"],
                        "encrypted": volume["Encrypted"],
                        "tags": {
                            tag["Key"]: tag["Value"] for tag in volume.get("Tags", [])
                        },
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

            # Security Groups
            security_groups = ec2.describe_security_groups()
            for sg in security_groups["SecurityGroups"]:
                self.resources.append(
                    {
                        "service": "EC2",
                        "type": "Security Group",
                        "region": region,
                        "id": sg["GroupId"],
                        "name": sg["GroupName"],
                        "description": sg["Description"],
                        "vpc_id": sg.get("VpcId"),
                        "tags": {
                            tag["Key"]: tag["Value"] for tag in sg.get("Tags", [])
                        },
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover EC2 resources in {region}: {e}")

    def _enhance_s3_resources(self, region: str):
        """Enhance S3 resources with additional details from S3 API."""
        try:
            s3 = self.session.client("s3", region_name=region)

            # S3 Buckets (global service, only check once)
            if region == "us-east-1":  # Only check from one region
                buckets = s3.list_buckets()
                for bucket in buckets["Buckets"]:
                    try:
                        bucket_region = s3.get_bucket_location(Bucket=bucket["Name"])[
                            "LocationConstraint"
                        ]
                        bucket_region = bucket_region or "us-east-1"

                        # Get bucket tags
                        try:
                            tags_response = s3.get_bucket_tagging(Bucket=bucket["Name"])
                            tags = {
                                tag["Key"]: tag["Value"]
                                for tag in tags_response.get("TagSet", [])
                            }
                        except ClientError:
                            tags = {}

                        self.resources.append(
                            {
                                "service": "S3",
                                "type": "Bucket",
                                "region": bucket_region,
                                "id": bucket["Name"],
                                "name": bucket["Name"],
                                "creation_date": bucket["CreationDate"].isoformat(),
                                "tags": tags,
                                "discovered_at": datetime.utcnow().isoformat(),
                            }
                        )
                    except ClientError as e:
                        self.logger.warning(
                            f"Failed to get details for S3 bucket {bucket['Name']}: {e}"
                        )

        except ClientError as e:
            self.logger.warning(f"Failed to discover S3 resources: {e}")

    def _enhance_rds_resources(self, region: str):
        """Enhance RDS resources with additional details from RDS API."""
        try:
            rds = self.session.client("rds", region_name=region)

            # RDS Instances
            instances = rds.describe_db_instances()
            for instance in instances["DBInstances"]:
                # Get tags
                try:
                    tags_response = rds.list_tags_for_resource(
                        ResourceName=instance["DBInstanceArn"]
                    )
                    tags = {
                        tag["Key"]: tag["Value"]
                        for tag in tags_response.get("TagList", [])
                    }
                except ClientError:
                    tags = {}

                self.resources.append(
                    {
                        "service": "RDS",
                        "type": "DB Instance",
                        "region": region,
                        "id": instance["DBInstanceIdentifier"],
                        "name": instance["DBInstanceIdentifier"],
                        "engine": instance["Engine"],
                        "engine_version": instance["EngineVersion"],
                        "instance_class": instance["DBInstanceClass"],
                        "status": instance["DBInstanceStatus"],
                        "allocated_storage": instance.get("AllocatedStorage"),
                        "vpc_id": instance.get("DbSubnetGroup", {}).get("VpcId"),
                        "tags": tags,
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover RDS resources in {region}: {e}")

    def _enhance_lambda_resources(self, region: str):
        """Enhance Lambda resources with additional details from Lambda API."""
        try:
            lambda_client = self.session.client("lambda", region_name=region)

            functions = lambda_client.list_functions()
            for function in functions["Functions"]:
                # Get tags
                try:
                    tags_response = lambda_client.list_tags(
                        Resource=function["FunctionArn"]
                    )
                    tags = tags_response.get("Tags", {})
                except ClientError:
                    tags = {}

                self.resources.append(
                    {
                        "service": "Lambda",
                        "type": "Function",
                        "region": region,
                        "id": function["FunctionName"],
                        "name": function["FunctionName"],
                        "runtime": function["Runtime"],
                        "memory_size": function["MemorySize"],
                        "timeout": function["Timeout"],
                        "last_modified": function["LastModified"],
                        "tags": tags,
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover Lambda resources in {region}: {e}")

    def _enhance_iam_resources(self, region: str):
        """Enhance IAM resources with additional details from IAM API (global service, only check once)."""
        if region != "us-east-1":  # IAM is global, only check from one region
            return

        try:
            iam = self.session.client("iam")

            # IAM Roles
            roles = iam.list_roles()
            for role in roles["Roles"]:
                # Get tags
                try:
                    tags_response = iam.list_role_tags(RoleName=role["RoleName"])
                    tags = {
                        tag["Key"]: tag["Value"]
                        for tag in tags_response.get("Tags", [])
                    }
                except ClientError:
                    tags = {}

                self.resources.append(
                    {
                        "service": "IAM",
                        "type": "Role",
                        "region": "global",
                        "id": role["RoleName"],
                        "name": role["RoleName"],
                        "path": role["Path"],
                        "create_date": role["CreateDate"].isoformat(),
                        "tags": tags,
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

            # IAM Users
            users = iam.list_users()
            for user in users["Users"]:
                # Get tags
                try:
                    tags_response = iam.list_user_tags(UserName=user["UserName"])
                    tags = {
                        tag["Key"]: tag["Value"]
                        for tag in tags_response.get("Tags", [])
                    }
                except ClientError:
                    tags = {}

                self.resources.append(
                    {
                        "service": "IAM",
                        "type": "User",
                        "region": "global",
                        "id": user["UserName"],
                        "name": user["UserName"],
                        "path": user["Path"],
                        "create_date": user["CreateDate"].isoformat(),
                        "tags": tags,
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover IAM resources: {e}")

    def _enhance_vpc_resources(self, region: str):
        """Enhance VPC resources with additional details from VPC API."""
        try:
            ec2 = self.session.client("ec2", region_name=region)

            # VPCs
            vpcs = ec2.describe_vpcs()
            for vpc in vpcs["Vpcs"]:
                self.resources.append(
                    {
                        "service": "VPC",
                        "type": "VPC",
                        "region": region,
                        "id": vpc["VpcId"],
                        "name": self._get_tag_value(vpc.get("Tags", []), "Name"),
                        "cidr_block": vpc["CidrBlock"],
                        "state": vpc["State"],
                        "is_default": vpc["IsDefault"],
                        "tags": {
                            tag["Key"]: tag["Value"] for tag in vpc.get("Tags", [])
                        },
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

            # Subnets
            subnets = ec2.describe_subnets()
            for subnet in subnets["Subnets"]:
                self.resources.append(
                    {
                        "service": "VPC",
                        "type": "Subnet",
                        "region": region,
                        "id": subnet["SubnetId"],
                        "name": self._get_tag_value(subnet.get("Tags", []), "Name"),
                        "vpc_id": subnet["VpcId"],
                        "cidr_block": subnet["CidrBlock"],
                        "availability_zone": subnet["AvailabilityZone"],
                        "available_ip_count": subnet["AvailableIpAddressCount"],
                        "tags": {
                            tag["Key"]: tag["Value"] for tag in subnet.get("Tags", [])
                        },
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover VPC resources in {region}: {e}")

    def _enhance_cloudformation_resources(self, region: str):
        """Enhance CloudFormation resources with additional details from CloudFormation API."""
        try:
            cf = self.session.client("cloudformation", region_name=region)

            stacks = cf.list_stacks(
                StackStatusFilter=[
                    "CREATE_COMPLETE",
                    "UPDATE_COMPLETE",
                    "ROLLBACK_COMPLETE",
                ]
            )
            for stack in stacks["StackSummaries"]:
                # Get stack tags
                try:
                    stack_details = cf.describe_stacks(StackName=stack["StackName"])
                    tags = {
                        tag["Key"]: tag["Value"]
                        for tag in stack_details["Stacks"][0].get("Tags", [])
                    }
                except ClientError:
                    tags = {}

                self.resources.append(
                    {
                        "service": "CloudFormation",
                        "type": "Stack",
                        "region": region,
                        "id": stack["StackName"],
                        "name": stack["StackName"],
                        "status": stack["StackStatus"],
                        "creation_time": stack["CreationTime"].isoformat(),
                        "tags": tags,
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(
                f"Failed to discover CloudFormation resources in {region}: {e}"
            )

    def _enhance_ecs_resources(self, region: str):
        """Enhance ECS resources with additional details from ECS API."""
        try:
            ecs = self.session.client("ecs", region_name=region)

            # ECS Clusters
            clusters = ecs.list_clusters()
            for cluster_arn in clusters["clusterArns"]:
                cluster_details = ecs.describe_clusters(clusters=[cluster_arn])
                for cluster in cluster_details["clusters"]:
                    # Get tags
                    try:
                        tags_response = ecs.list_tags_for_resource(
                            resourceArn=cluster_arn
                        )
                        tags = {
                            tag["key"]: tag["value"]
                            for tag in tags_response.get("tags", [])
                        }
                    except ClientError:
                        tags = {}

                    self.resources.append(
                        {
                            "service": "ECS",
                            "type": "Cluster",
                            "region": region,
                            "id": cluster["clusterName"],
                            "name": cluster["clusterName"],
                            "status": cluster["status"],
                            "running_tasks": cluster["runningTasksCount"],
                            "pending_tasks": cluster["pendingTasksCount"],
                            "active_services": cluster["activeServicesCount"],
                            "tags": tags,
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )

        except ClientError as e:
            self.logger.warning(f"Failed to discover ECS resources in {region}: {e}")

    def _enhance_eks_resources(self, region: str):
        """Enhance EKS resources with additional details from EKS API."""
        try:
            eks = self.session.client("eks", region_name=region)

            clusters = eks.list_clusters()
            for cluster_name in clusters["clusters"]:
                cluster_details = eks.describe_cluster(name=cluster_name)
                cluster = cluster_details["cluster"]

                self.resources.append(
                    {
                        "service": "EKS",
                        "type": "Cluster",
                        "region": region,
                        "id": cluster["name"],
                        "name": cluster["name"],
                        "status": cluster["status"],
                        "version": cluster["version"],
                        "endpoint": cluster.get("endpoint"),
                        "created_at": (
                            cluster["createdAt"].isoformat()
                            if "createdAt" in cluster
                            else None
                        ),
                        "tags": cluster.get("tags", {}),
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Failed to discover EKS resources in {region}: {e}")

    def _enhance_cloudwatch_resources(self, region: str):
        """Enhance CloudWatch resources with additional details from CloudWatch API."""
        try:
            cw = self.session.client("cloudwatch", region_name=region)

            # CloudWatch Alarms
            alarms = cw.describe_alarms()
            for alarm in alarms["MetricAlarms"]:
                self.resources.append(
                    {
                        "service": "CloudWatch",
                        "type": "Alarm",
                        "region": region,
                        "id": alarm["AlarmName"],
                        "name": alarm["AlarmName"],
                        "description": alarm.get("AlarmDescription"),
                        "state": alarm["StateValue"],
                        "metric_name": alarm["MetricName"],
                        "namespace": alarm["Namespace"],
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(
                f"Failed to discover CloudWatch resources in {region}: {e}"
            )

    def _get_tag_value(self, tags: List[Dict], key: str) -> Optional[str]:
        """Get tag value by key."""
        for tag in tags:
            if tag["Key"] == key:
                return tag["Value"]
        return None

    def save_to_file(self, filename: str, format_type: str = "json"):
        """Save resources to file."""
        if format_type.lower() == "json":
            with open(filename, "w") as f:
                json.dump(self.resources, f, indent=2, default=str)
        elif format_type.lower() == "yaml":
            with open(filename, "w") as f:
                yaml.dump(
                    self.resources,
                    f,
                    default_flow_style=False,
                    default_style="",
                    allow_unicode=True,
                )
        else:
            raise ValueError("Format must be 'json' or 'yaml'")

        self.logger.info(f"Resources saved to {filename}")

    def upload_to_s3(self, bucket_name: str, key: str, format_type: str = "json"):
        """Upload resources to S3."""
        try:
            s3 = self.session.client("s3")

            if format_type.lower() == "json":
                content = json.dumps(self.resources, indent=2, default=str)
                content_type = "application/json"
            elif format_type.lower() == "yaml":
                content = yaml.dump(
                    self.resources,
                    default_flow_style=False,
                    default_style="",
                    allow_unicode=True,
                )
                content_type = "text/yaml"
            else:
                raise ValueError("Format must be 'json' or 'yaml'")

            s3.put_object(
                Bucket=bucket_name, Key=key, Body=content, ContentType=content_type
            )

            self.logger.info(f"Resources uploaded to s3://{bucket_name}/{key}")

        except ClientError as e:
            self.logger.error(f"Failed to upload to S3: {e}")
            raise

    def discover_all_resources(self) -> List[Dict[str, Any]]:
        """Alias for discover_resources() for backward compatibility."""
        return self.discover_resources()
