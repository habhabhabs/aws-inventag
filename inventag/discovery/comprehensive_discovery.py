#!/usr/bin/env python3
"""
Comprehensive AWS Resource Discovery System

This module implements a comprehensive discovery strategy that ensures ALL resources
are discovered, regardless of whether they are tagged or not.

Discovery Strategy:
1. Service-specific API discovery for ALL resources (primary)
2. ResourceGroupsTagging API for tag enrichment (secondary)
3. Billing validation for service confirmation (validation)

This ensures resources like VPCs, subnets, security groups, etc. are always discovered.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError


class ComprehensiveAWSDiscovery:
    """
    Comprehensive AWS resource discovery that finds ALL resources regardless of tags.

    Uses service-specific APIs as primary discovery method, then enriches with tags
    and validates against billing data.
    """

    def __init__(self, session: boto3.Session = None, regions: List[str] = None):
        self.session = session or boto3.Session()
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False  # Prevent duplicate logging
        self.regions = regions or ["us-east-1"]

        # Resource storage
        self.resources = []
        self.discovered_services = set()

        # Billing data for validation
        self.billing_services = set()
        self.billing_spend = {}

        # Comprehensive service discovery patterns
        self.service_discovery_patterns = {
            # Network & Foundation Services (often untagged)
            "ec2": {
                "operations": [
                    ("describe_vpcs", "Vpcs", "VPC"),
                    ("describe_subnets", "Subnets", "Subnet"),
                    ("describe_security_groups", "SecurityGroups", "SecurityGroup"),
                    ("describe_instances", "Reservations", "Instance"),
                    ("describe_volumes", "Volumes", "Volume"),
                    (
                        "describe_snapshots",
                        "Snapshots",
                        "Snapshot",
                        {"OwnerIds": ["self"]},
                    ),
                    ("describe_key_pairs", "KeyPairs", "KeyPair"),
                    (
                        "describe_internet_gateways",
                        "InternetGateways",
                        "InternetGateway",
                    ),
                    ("describe_nat_gateways", "NatGateways", "NatGateway"),
                    ("describe_route_tables", "RouteTables", "RouteTable"),
                    ("describe_network_acls", "NetworkAcls", "NetworkAcl"),
                    ("describe_addresses", "Addresses", "ElasticIP"),
                ],
                "regional": True,
                "critical": True,  # Always discover these
            },
            # Storage Services
            "s3": {
                "operations": [
                    ("list_buckets", "Buckets", "Bucket"),
                ],
                "regional": False,  # Global service
                "critical": True,
                "post_process": "enhance_s3_buckets",  # Get bucket regions/details
            },
            # Database Services
            "rds": {
                "operations": [
                    ("describe_db_instances", "DBInstances", "DBInstance"),
                    ("describe_db_clusters", "DBClusters", "DBCluster"),
                    (
                        "describe_db_snapshots",
                        "DBSnapshots",
                        "DBSnapshot",
                        {"SnapshotType": "manual"},
                    ),
                    ("describe_db_subnet_groups", "DBSubnetGroups", "DBSubnetGroup"),
                    (
                        "describe_db_parameter_groups",
                        "DBParameterGroups",
                        "DBParameterGroup",
                    ),
                ],
                "regional": True,
                "critical": True,
            },
            # Compute Services
            "lambda": {
                "operations": [
                    ("list_functions", "Functions", "Function"),
                    ("list_layers", "Layers", "Layer"),
                ],
                "regional": True,
                "critical": True,
            },
            # Application Services (Classic ELB)
            "elb": {
                "operations": [
                    (
                        "describe_load_balancers",
                        "LoadBalancerDescriptions",
                        "LoadBalancer",
                    ),
                ],
                "regional": True,
                "critical": True,
            },
            "elbv2": {
                "operations": [
                    ("describe_load_balancers", "LoadBalancers", "LoadBalancerV2"),
                    ("describe_target_groups", "TargetGroups", "TargetGroup"),
                ],
                "regional": True,
                "critical": True,
            },
            # Identity & Security (Global)
            "iam": {
                "operations": [
                    ("list_users", "Users", "User"),
                    ("list_roles", "Roles", "Role"),
                    ("list_policies", "Policies", "Policy", {"Scope": "Local"}),
                    ("list_groups", "Groups", "Group"),
                    ("list_instance_profiles", "InstanceProfiles", "InstanceProfile"),
                ],
                "regional": False,  # Global service
                "critical": True,
            },
            # CDN & DNS (Global)
            "cloudfront": {
                "operations": [
                    ("list_distributions", "DistributionList.Items", "Distribution"),
                ],
                "regional": False,
                "critical": True,
            },
            "route53": {
                "operations": [
                    ("list_hosted_zones", "HostedZones", "HostedZone"),
                ],
                "regional": False,
                "critical": True,
            },
            # Security Services
            "kms": {
                "operations": [
                    ("list_keys", "Keys", "Key"),
                    ("list_aliases", "Aliases", "Alias"),
                ],
                "regional": True,
                "critical": False,
            },
            # Monitoring
            "cloudwatch": {
                "operations": [
                    ("describe_alarms", "MetricAlarms", "Alarm"),
                    ("list_dashboards", "DashboardEntries", "Dashboard"),
                ],
                "regional": True,
                "critical": False,
            },
            # Container Services
            "ecs": {
                "operations": [
                    ("list_clusters", "clusterArns", "Cluster"),
                    ("list_services", "serviceArns", "Service"),
                ],
                "regional": True,
                "critical": False,
            },
            "eks": {
                "operations": [
                    ("list_clusters", "clusters", "Cluster"),
                ],
                "regional": True,
                "critical": False,
            },
            # Message Queuing
            "sns": {
                "operations": [
                    ("list_topics", "Topics", "Topic"),
                ],
                "regional": True,
                "critical": False,
            },
            "sqs": {
                "operations": [
                    ("list_queues", "QueueUrls", "Queue"),
                ],
                "regional": True,
                "critical": False,
            },
            # NoSQL Database
            "dynamodb": {
                "operations": [
                    ("list_tables", "TableNames", "Table"),
                ],
                "regional": True,
                "critical": False,
            },
            # API Gateway
            "apigateway": {
                "operations": [
                    ("get_rest_apis", "items", "RestApi"),
                ],
                "regional": True,
                "critical": False,
            },
        }

        # Global services that should only be called from us-east-1
        self.global_services = {"s3", "iam", "cloudfront", "route53"}

    def discover_all_resources(self, max_workers: int = 15) -> List[Dict[str, Any]]:
        """
        Comprehensive discovery of ALL AWS resources regardless of tags.

        Returns:
            List of discovered resources with complete metadata
        """
        self.logger.info("🔍 Starting comprehensive AWS resource discovery")
        self.logger.info(
            "Strategy: Service-specific APIs → Tag enrichment → Billing validation"
        )

        start_time = time.time()

        # Step 1: Discover billing services for validation
        self._discover_billing_services()

        # Step 2: Comprehensive service-specific discovery (PRIMARY)
        self._discover_all_service_resources(max_workers)

        # Step 3: Enrich with ResourceGroupsTagging API (SECONDARY)
        self._enrich_with_tagging_api()

        # Step 4: Validate against billing data
        self._validate_with_billing()

        # Step 5: Post-process and enhance
        self._post_process_resources()

        execution_time = time.time() - start_time

        self.logger.info(
            f"✅ Comprehensive discovery complete: {len(self.resources)} resources "
            f"from {len(self.discovered_services)} services in {execution_time:.1f}s"
        )

        return self.resources

    def _discover_billing_services(self):
        """Discover services with billing usage for validation."""
        try:
            ce_client = self.session.client("ce", region_name="us-east-1")

            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    "Start": (
                        datetime.now().replace(day=1) - timedelta(days=30)
                    ).strftime("%Y-%m-%d"),
                    "End": datetime.now().strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["BlendedCost", "UsageQuantity"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            for result in response.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    service_name = group.get("Keys", [""])[0]
                    cost = float(
                        group.get("Metrics", {})
                        .get("BlendedCost", {})
                        .get("Amount", "0")
                    )
                    usage = float(
                        group.get("Metrics", {})
                        .get("UsageQuantity", {})
                        .get("Amount", "0")
                    )

                    if cost > 0 or usage > 0:
                        normalized_service = self._normalize_billing_service_name(
                            service_name
                        )
                        self.billing_services.add(normalized_service)
                        self.billing_spend[normalized_service] = cost

            self.logger.info(
                f"💰 Found {len(self.billing_services)} services with billing usage"
            )

        except Exception as e:
            self.logger.warning(f"Billing discovery failed: {e}")

    def _discover_all_service_resources(self, max_workers: int):
        """Discover ALL resources using service-specific APIs (PRIMARY METHOD)."""
        self.logger.info("🚀 Starting comprehensive service-specific discovery")

        # Prepare discovery tasks
        discovery_tasks = []

        for service_name, config in self.service_discovery_patterns.items():
            if config.get("regional", True):
                # Regional service - discover in all regions
                for region in self.regions:
                    discovery_tasks.append(
                        {
                            "service": service_name,
                            "region": region,
                            "config": config,
                            "priority": 1 if config.get("critical", False) else 2,
                        }
                    )
            else:
                # Global service - discover from us-east-1 only
                if "us-east-1" in self.regions:
                    discovery_tasks.append(
                        {
                            "service": service_name,
                            "region": "us-east-1",
                            "config": config,
                            "priority": 1 if config.get("critical", False) else 2,
                        }
                    )

        # Sort by priority (critical services first)
        discovery_tasks.sort(key=lambda x: x["priority"])

        self.logger.info(
            f"🔍 Executing {len(discovery_tasks)} discovery tasks with {max_workers} workers"
        )

        # Execute parallel discovery
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {}

            for task in discovery_tasks:
                future = executor.submit(self._discover_service_in_region, task)
                future_to_task[future] = task

            # Collect results
            completed = 0
            for future in as_completed(future_to_task, timeout=600):
                task = future_to_task[future]
                try:
                    resources_found = future.result()
                    if resources_found > 0:
                        self.discovered_services.add(task["service"])
                        self.logger.debug(
                            f"✅ {task['service']} in {task['region']}: {resources_found} resources"
                        )
                    completed += 1

                    if completed % 10 == 0:  # Progress logging
                        self.logger.info(
                            f"   Progress: {completed}/{len(discovery_tasks)} tasks completed"
                        )

                except Exception as e:
                    self.logger.warning(
                        f"❌ {task['service']} in {task['region']} failed: {e}"
                    )

    def _discover_service_in_region(self, task: Dict[str, Any]) -> int:
        """Discover resources for a specific service in a specific region."""
        service_name = task["service"]
        region = task["region"]
        config = task["config"]
        resources_found = 0

        try:
            # Create service client
            client = self.session.client(service_name, region_name=region)

            # Execute all operations for this service
            for operation_config in config["operations"]:
                try:
                    resources_found += self._execute_discovery_operation(
                        client, service_name, region, operation_config
                    )
                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "")
                    if error_code in ["AccessDenied", "UnauthorizedOperation"]:
                        # Expected for some operations with limited permissions
                        continue
                    else:
                        self.logger.debug(f"Operation failed for {service_name}: {e}")
                        continue
                except Exception as e:
                    self.logger.debug(f"Operation error for {service_name}: {e}")
                    continue

        except Exception as e:
            self.logger.warning(
                f"Service client creation failed for {service_name}: {e}"
            )

        return resources_found

    def _execute_discovery_operation(
        self, client, service_name: str, region: str, operation_config: Tuple
    ) -> int:
        """Execute a single discovery operation and extract resources."""
        operation_name, response_key, resource_type = operation_config[:3]
        operation_params = operation_config[3] if len(operation_config) > 3 else {}

        try:
            # Get the operation method
            operation = getattr(client, operation_name)

            # Execute with pagination if available
            resources_found = 0

            if hasattr(client, "get_paginator"):
                try:
                    paginator = client.get_paginator(operation_name)
                    pages = paginator.paginate(**operation_params)

                    for page in pages:
                        resources_found += self._extract_resources_from_response(
                            page,
                            response_key,
                            service_name,
                            region,
                            resource_type,
                            operation_name,
                        )

                except Exception:
                    # Fallback to direct call if pagination fails
                    response = operation(**operation_params)
                    resources_found += self._extract_resources_from_response(
                        response,
                        response_key,
                        service_name,
                        region,
                        resource_type,
                        operation_name,
                    )
            else:
                # Direct operation call
                response = operation(**operation_params)
                resources_found += self._extract_resources_from_response(
                    response,
                    response_key,
                    service_name,
                    region,
                    resource_type,
                    operation_name,
                )

            return resources_found

        except Exception as e:
            # Operation-level errors are expected and handled gracefully
            return 0

    def _extract_resources_from_response(
        self,
        response: Dict,
        response_key: str,
        service_name: str,
        region: str,
        resource_type: str,
        operation_name: str,
    ) -> int:
        """Extract resources from AWS API response."""
        try:
            # Handle nested response keys (like 'DistributionList.Items')
            data = response
            for key in response_key.split("."):
                data = data.get(key, [])

            if not isinstance(data, list):
                data = [data] if data else []

            resources_added = 0
            for item in data:
                if isinstance(item, dict):
                    resource = self._normalize_resource(
                        item, service_name, region, resource_type, operation_name
                    )
                    if resource:
                        # Handle EC2 reservations specially
                        if resource_type == "Instance" and "Instances" in item:
                            for instance in item["Instances"]:
                                instance_resource = self._normalize_resource(
                                    instance,
                                    service_name,
                                    region,
                                    resource_type,
                                    operation_name,
                                )
                                if instance_resource:
                                    self.resources.append(instance_resource)
                                    resources_added += 1
                        else:
                            self.resources.append(resource)
                            resources_added += 1
                elif isinstance(item, str):
                    # Handle string responses (like SQS queue URLs)
                    resource = self._create_string_resource(
                        item, service_name, region, resource_type, operation_name
                    )
                    if resource:
                        self.resources.append(resource)
                        resources_added += 1

            return resources_added

        except Exception as e:
            self.logger.debug(f"Resource extraction failed for {service_name}: {e}")
            return 0

    def _normalize_resource(
        self,
        raw_data: Dict,
        service_name: str,
        region: str,
        resource_type: str,
        operation_name: str,
    ) -> Optional[Dict]:
        """Normalize a resource into standard format."""
        try:
            # Extract resource identifier
            resource_id = self._extract_resource_id(raw_data, resource_type)
            if not resource_id:
                return None

            # Extract resource name
            resource_name = self._extract_resource_name(raw_data)

            # Extract ARN if available
            arn = raw_data.get("Arn") or raw_data.get("ARN")
            if not arn:
                arn = self._construct_arn(
                    service_name, region, resource_type, resource_id
                )

            # Extract tags
            tags = self._extract_tags(raw_data)

            # Build normalized resource
            resource = {
                "service": service_name.upper(),
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "arn": arn,
                "region": region,
                "account_id": self._extract_account_id(arn),
                "tags": tags,
                "raw_data": raw_data,
                "discovered_via": f"ServiceAPI:{operation_name}",
                "discovered_at": datetime.utcnow().isoformat(),
                "tagged": bool(tags),
            }

            return resource

        except Exception as e:
            self.logger.debug(f"Resource normalization failed: {e}")
            return None

    def _create_string_resource(
        self,
        value: str,
        service_name: str,
        region: str,
        resource_type: str,
        operation_name: str,
    ) -> Optional[Dict]:
        """Create resource from string value (like SQS queue URLs)."""
        try:
            resource = {
                "service": service_name.upper(),
                "resource_type": resource_type,
                "resource_id": value,
                "resource_name": value.split("/")[-1] if "/" in value else value,
                "arn": value,  # For some services, the URL is the ARN equivalent
                "region": region,
                "account_id": None,
                "tags": {},
                "raw_data": {"url": value},
                "discovered_via": f"ServiceAPI:{operation_name}",
                "discovered_at": datetime.utcnow().isoformat(),
                "tagged": False,
            }

            return resource

        except Exception as e:
            self.logger.debug(f"String resource creation failed: {e}")
            return None

    def _extract_resource_id(self, data: Dict, resource_type: str) -> Optional[str]:
        """Extract resource ID from AWS resource data."""
        # Common ID field patterns
        id_fields = [
            "Id",
            "ResourceId",
            "ARN",
            "Arn",
            f"{resource_type}Id",
            f"{resource_type}Name",
            "Name",
            "Identifier",
        ]

        # Service-specific patterns
        service_patterns = {
            "VPC": ["VpcId"],
            "Subnet": ["SubnetId"],
            "SecurityGroup": ["GroupId"],
            "Instance": ["InstanceId"],
            "Volume": ["VolumeId"],
            "KeyPair": ["KeyName"],
            "Bucket": ["Name"],
            "DBInstance": ["DBInstanceIdentifier"],
            "Function": ["FunctionName"],
            "LoadBalancer": ["LoadBalancerName", "LoadBalancerArn"],
            "User": ["UserName"],
            "Role": ["RoleName"],
            "HostedZone": ["Id"],
            "Distribution": ["Id"],
        }

        # Try service-specific patterns first
        if resource_type in service_patterns:
            for field in service_patterns[resource_type]:
                if field in data and data[field]:
                    return str(data[field])

        # Try common patterns
        for field in id_fields:
            if field in data and data[field]:
                return str(data[field])

        return None

    def _extract_resource_name(self, data: Dict) -> Optional[str]:
        """Extract resource name from AWS resource data."""
        name_fields = ["Name", "ResourceName", "Tags.Name"]

        for field in name_fields:
            if field in data and data[field]:
                return str(data[field])

        # Check tags for Name
        if "Tags" in data:
            tags = data["Tags"]
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, dict) and tag.get("Key") == "Name":
                        return tag.get("Value", "")
            elif isinstance(tags, dict) and "Name" in tags:
                return str(tags["Name"])

        return None

    def _extract_tags(self, data: Dict) -> Dict[str, str]:
        """Extract tags from AWS resource data."""
        tags = {}

        if "Tags" in data:
            tag_data = data["Tags"]
            if isinstance(tag_data, list):
                for tag in tag_data:
                    if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                        tags[tag["Key"]] = tag["Value"]
            elif isinstance(tag_data, dict):
                tags.update(tag_data)

        return tags

    def _extract_account_id(self, arn: str) -> Optional[str]:
        """Extract account ID from ARN."""
        if arn and arn.startswith("arn:aws:"):
            parts = arn.split(":")
            if len(parts) >= 5:
                return parts[4]
        return None

    def _construct_arn(
        self, service: str, region: str, resource_type: str, resource_id: str
    ) -> str:
        """Construct ARN for resources that don't provide one."""
        try:
            # Get account ID from STS if available
            try:
                sts = self.session.client("sts")
                account_id = sts.get_caller_identity()["Account"]
            except:
                account_id = "000000000000"  # Placeholder

            # Handle service-specific ARN formats
            if service == "s3":
                return f"arn:aws:s3:::{resource_id}"
            elif service == "iam":
                return (
                    f"arn:aws:iam::{account_id}:{resource_type.lower()}/{resource_id}"
                )
            elif service in ["cloudfront", "route53"]:
                return f"arn:aws:{service}::{account_id}:{resource_type.lower()}/{resource_id}"
            else:
                return f"arn:aws:{service}:{region}:{account_id}:{resource_type.lower()}/{resource_id}"

        except:
            return f"arn:aws:{service}:{region}:unknown:{resource_type.lower()}/{resource_id}"

    def _enrich_with_tagging_api(self):
        """Enrich discovered resources with additional tag data from ResourceGroupsTagging API."""
        self.logger.info("🏷️ Enriching resources with ResourceGroupsTagging API data")

        # Create ARN lookup for existing resources
        arn_to_resource = {r["arn"]: r for r in self.resources if r.get("arn")}

        enriched_count = 0
        new_resources_found = 0

        for region in self.regions:
            try:
                rgt_client = self.session.client(
                    "resourcegroupstaggingapi", region_name=region
                )
                paginator = rgt_client.get_paginator("get_resources")

                for page in paginator.paginate():
                    for resource in page.get("ResourceTagMappingList", []):
                        arn = resource.get("ResourceARN", "")
                        tags = {
                            tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])
                        }

                        if arn in arn_to_resource:
                            # Enrich existing resource with additional tags
                            existing_resource = arn_to_resource[arn]
                            existing_resource["tags"].update(tags)
                            existing_resource["tagged"] = bool(
                                existing_resource["tags"]
                            )
                            enriched_count += 1
                        else:
                            # This is a resource we missed - add it
                            try:
                                service = self._extract_service_from_arn(arn)
                                if service:
                                    new_resource = {
                                        "service": service.upper(),
                                        "resource_type": "Unknown",
                                        "resource_id": (
                                            arn.split("/")[-1]
                                            if "/" in arn
                                            else arn.split(":")[-1]
                                        ),
                                        "resource_name": tags.get("Name"),
                                        "arn": arn,
                                        "region": region,
                                        "account_id": self._extract_account_id(arn),
                                        "tags": tags,
                                        "raw_data": {"arn": arn},
                                        "discovered_via": "ResourceGroupsTaggingAPI",
                                        "discovered_at": datetime.utcnow().isoformat(),
                                        "tagged": True,
                                    }
                                    self.resources.append(new_resource)
                                    new_resources_found += 1
                            except Exception as e:
                                self.logger.debug(
                                    f"Failed to process tagged resource {arn}: {e}"
                                )

            except Exception as e:
                self.logger.warning(
                    f"ResourceGroupsTagging enrichment failed in {region}: {e}"
                )

        self.logger.info(
            f"🏷️ Tag enrichment complete: enriched {enriched_count} resources, "
            f"found {new_resources_found} additional tagged resources"
        )

    def _extract_service_from_arn(self, arn: str) -> Optional[str]:
        """Extract service name from ARN."""
        if arn and arn.startswith("arn:aws:"):
            parts = arn.split(":")
            if len(parts) >= 3:
                return parts[2]
        return None

    def _validate_with_billing(self):
        """Validate discovered resources against billing data."""
        if not self.billing_services:
            return

        discovered_services = {r["service"].lower() for r in self.resources}

        # Find services with billing but no resources (potential untagged resources)
        missing_services = self.billing_services - discovered_services
        if missing_services:
            self.logger.warning(
                f"💸 Found {len(missing_services)} services with billing usage but no discovered resources: "
                f"{', '.join(sorted(missing_services))} - these may have untagged resources"
            )

        # Find services with resources but no billing (free tier)
        unbilled_services = discovered_services - self.billing_services
        if unbilled_services:
            self.logger.info(
                f"🆓 Found {len(unbilled_services)} services with resources but no billing: "
                f"{', '.join(sorted(unbilled_services))} - likely free tier usage"
            )

    def _post_process_resources(self):
        """Post-process resources for consistency and additional metadata."""
        # Remove duplicates based on ARN
        seen_arns = set()
        deduplicated = []

        for resource in self.resources:
            arn = resource.get("arn")
            if arn not in seen_arns:
                seen_arns.add(arn)
                deduplicated.append(resource)

        self.resources = deduplicated

        # Add billing metadata
        for resource in self.resources:
            service = resource["service"].lower()
            resource["billing_validated"] = service in self.billing_services
            resource["monthly_spend"] = self.billing_spend.get(service, 0.0)

        self.logger.info(
            f"📊 Post-processing complete: {len(self.resources)} unique resources"
        )

    def _normalize_billing_service_name(self, billing_name: str) -> str:
        """Normalize billing service name to match AWS service names."""
        mappings = {
            "Amazon Elastic Compute Cloud - Compute": "ec2",
            "Amazon Simple Storage Service": "s3",
            "Amazon Relational Database Service": "rds",
            "AWS Lambda": "lambda",
            "Amazon CloudFront": "cloudfront",
            "Amazon Route 53": "route53",
            "AWS Identity and Access Management": "iam",
            "Amazon CloudWatch": "cloudwatch",
            "AWS Key Management Service": "kms",
            "Elastic Load Balancing": "elasticloadbalancing",
            "Amazon Virtual Private Cloud": "ec2",
            "Amazon Elastic Container Service": "ecs",
            "Amazon Elastic Kubernetes Service": "eks",
            "Amazon Simple Notification Service": "sns",
            "Amazon Simple Queue Service": "sqs",
            "Amazon DynamoDB": "dynamodb",
            "Amazon API Gateway": "apigateway",
        }

        return mappings.get(
            billing_name, billing_name.lower().replace(" ", "").replace("-", "")
        )
