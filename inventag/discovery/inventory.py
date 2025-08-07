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
import time
import sys
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from botocore.exceptions import ClientError, NoCredentialsError


class ProgressSpinner:
    """Simple progress spinner for long-running operations."""

    def __init__(self, message="Processing"):
        self.message = message
        self.spinning = False
        self.thread = None
        self.chars = "⣾⣽⣻⢿⡿⣟⣯⣷"

    def start(self):
        """Start the spinner animation."""
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the spinner animation."""
        self.spinning = False
        if self.thread:
            self.thread.join()
        # Clear the line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def _spin(self):
        """Internal spinner animation loop."""
        i = 0
        while self.spinning:
            sys.stdout.write(f"\r{self.message} {self.chars[i % len(self.chars)]} ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def update_message(self, new_message):
        """Update the spinner message."""
        self.message = new_message


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

        # Billing-based discovery state
        self.billing_validated_services: Set[str] = set()
        self.billing_spend_by_service: Dict[str, float] = {}
        self.enable_billing_validation = True

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
        """Discover all AWS resources across regions and services with billing validation."""
        self.logger.info(
            "Starting comprehensive AWS resource discovery with billing validation..."
        )

        # Step 1: Discover services with actual usage via billing data
        if self.enable_billing_validation:
            spinner = ProgressSpinner(
                "🔍 Analyzing billing data to identify services with usage"
            )
            spinner.start()
            try:
                self._discover_services_via_billing()
            finally:
                spinner.stop()

        # Step 2: Use ResourceGroupsTagging API for comprehensive discovery (recommended)
        initial_resource_count = len(self.resources)
        spinner = ProgressSpinner(
            "📋 Discovering resources via ResourceGroupsTagging API"
        )
        spinner.start()
        try:
            self._discover_via_resource_groups_tagging_api()
        finally:
            spinner.stop()
        rgt_resource_count = len(self.resources)

        # Step 3: Cross-validate with billing and enhance discovery
        if self.enable_billing_validation:
            spinner = ProgressSpinner("💰 Cross-validating discovery with billing data")
            spinner.start()
            try:
                self._validate_discovery_with_billing()
            finally:
                spinner.stop()

        # Step 4: Dynamic discovery based on billing validation
        discovered_service_names = set(
            resource.get("service", "").upper() for resource in self.resources
        )

        # For services with billing usage but no discovered resources, try dynamic discovery
        if self.enable_billing_validation and hasattr(self, "billing_spend_by_service"):
            undiscovered_services = (
                set(self.billing_spend_by_service.keys()) - discovered_service_names
            )
            if undiscovered_services:
                self.logger.info(
                    f"Attempting dynamic discovery for {len(undiscovered_services)} services with billing usage"
                )
                spinner = ProgressSpinner(
                    f"🚀 Performing dynamic discovery for {len(undiscovered_services)} services"
                )
                spinner.start()
                try:
                    for i, service_name in enumerate(
                        list(undiscovered_services)[:10]
                    ):  # Limit to avoid too many API calls
                        spinner.update_message(
                            f"🚀 Dynamic discovery: {service_name} ({i+1}/{min(len(undiscovered_services), 10)})"
                        )
                        try:
                            self._discover_service_by_name(service_name)
                        except Exception as e:
                            self.logger.warning(
                                f"Dynamic discovery failed for {service_name}: {e}"
                            )
                finally:
                    spinner.stop()

        # Step 5: If still very few resources, try basic service discovery
        total_resources_after_dynamic = len(self.resources)
        if total_resources_after_dynamic < 10:
            self.logger.warning(
                "Still few resources after dynamic discovery. Trying basic services."
            )
            basic_services = ["EC2", "S3", "RDS", "Lambda", "CloudWatch", "IAM"]
            for service in basic_services:
                try:
                    self._discover_service_by_name(service)
                except Exception as e:
                    self.logger.debug(f"Basic discovery failed for {service}: {e}")

        # Step 6: Remove duplicates based on ARN
        self._deduplicate_resources()

        # Step 7: Add billing metadata to resources
        if self.enable_billing_validation:
            self._add_billing_metadata()

        self.logger.info(
            f"Comprehensive discovery complete. Found {len(self.resources)} unique resources "
            f"across {len(self._get_discovered_services())} services "
            f"({len(self.billing_validated_services)} billing-validated)."
        )
        return self.resources

    def _discover_services_via_billing(self):
        """Discover services with actual usage via AWS Cost Explorer billing data."""
        self.logger.info("Discovering services with actual usage via billing data...")

        try:
            # Cost Explorer is only available in us-east-1
            ce = self.session.client("ce", region_name="us-east-1")

            # Get cost data for the last 30 days to identify active services
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)

            # Query cost and usage data grouped by service
            response = ce.get_cost_and_usage(
                TimePeriod={
                    "Start": start_date.strftime("%Y-%m-%d"),
                    "End": end_date.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["BlendedCost", "UsageQuantity"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            # Process billing data to identify active services
            services_with_usage = {}
            total_spend = 0.0

            for result_by_time in response["ResultsByTime"]:
                for group in result_by_time["Groups"]:
                    service_name = group["Keys"][0] if group["Keys"] else "Unknown"
                    cost_amount = float(group["Metrics"]["BlendedCost"]["Amount"])
                    usage_quantity = float(group["Metrics"]["UsageQuantity"]["Amount"])

                    if (
                        cost_amount > 0.01 or usage_quantity > 0
                    ):  # Services with minimal spend or usage
                        normalized_service = self._normalize_billing_service_name(
                            service_name
                        )
                        services_with_usage[normalized_service] = {
                            "billing_name": service_name,
                            "cost": cost_amount,
                            "usage": usage_quantity,
                            "aws_service_code": normalized_service,
                        }
                        total_spend += cost_amount

            # Store billing-validated services
            self.billing_validated_services = set(services_with_usage.keys())
            self.billing_spend_by_service = {
                svc: data["cost"] for svc, data in services_with_usage.items()
            }

            self.logger.info(
                f"Billing analysis: Found {len(services_with_usage)} services with usage "
                f"(${total_spend:.2f} total spend in last 30 days)"
            )

            # Log top spending services
            top_services = sorted(
                services_with_usage.items(), key=lambda x: x[1]["cost"], reverse=True
            )[:10]

            for service, data in top_services:
                self.logger.info(f"  💰 {service}: ${data['cost']:.2f}")

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "UnauthorizedOperation":
                self.logger.warning(
                    "No permission for Cost Explorer API. Skipping billing validation."
                )
            elif error_code == "OptInRequired":
                self.logger.warning(
                    "Cost Explorer not enabled. Skipping billing validation."
                )
            else:
                self.logger.warning(f"Cost Explorer API failed: {e}")
            self.enable_billing_validation = False
        except Exception as e:
            self.logger.warning(f"Billing discovery failed: {e}")
            self.enable_billing_validation = False

    def _normalize_billing_service_name(self, billing_service_name: str) -> str:
        """Normalize billing service names to AWS service codes."""
        # Mapping of billing service names to standard AWS service codes
        service_mappings = {
            # Compute
            "Amazon Elastic Compute Cloud - Compute": "EC2",
            "Amazon Elastic Container Service": "ECS",
            "Amazon Elastic Kubernetes Service": "EKS",
            "AWS Lambda": "LAMBDA",
            "Amazon Lightsail": "LIGHTSAIL",
            "AWS Batch": "BATCH",
            # Storage
            "Amazon Simple Storage Service": "S3",
            "Amazon Elastic Block Store": "EBS",
            "Amazon Elastic File System": "EFS",
            "Amazon FSx": "FSX",
            "AWS Storage Gateway": "STORAGEGATEWAY",
            # Database
            "Amazon Relational Database Service": "RDS",
            "Amazon DynamoDB": "DYNAMODB",
            "Amazon ElastiCache": "ELASTICACHE",
            "Amazon Redshift": "REDSHIFT",
            "Amazon DocumentDB (with MongoDB compatibility)": "DOCDB",
            "Amazon Neptune": "NEPTUNE",
            # Networking
            "Amazon Virtual Private Cloud": "VPC",
            "Elastic Load Balancing": "ELB",
            "Amazon CloudFront": "CLOUDFRONT",
            "Amazon Route 53": "ROUTE53",
            "AWS Direct Connect": "DIRECTCONNECT",
            "Amazon API Gateway": "APIGATEWAY",
            # Security & Identity
            "AWS Identity and Access Management": "IAM",
            "AWS Certificate Manager": "ACM",
            "Amazon Cognito": "COGNITO",
            "AWS Secrets Manager": "SECRETSMANAGER",
            "AWS Systems Manager": "SSM",
            "AWS WAF": "WAF",
            # Application Integration
            "Amazon Simple Notification Service": "SNS",
            "Amazon Simple Queue Service": "SQS",
            "AWS Step Functions": "STEPFUNCTIONS",
            "Amazon EventBridge": "EVENTS",
            "Amazon MQ": "MQ",
            # Analytics
            "Amazon Kinesis": "KINESIS",
            "Amazon Athena": "ATHENA",
            "AWS Glue": "GLUE",
            "Amazon EMR": "EMR",
            "Amazon QuickSight": "QUICKSIGHT",
            # Machine Learning
            "Amazon SageMaker": "SAGEMAKER",
            "Amazon Rekognition": "REKOGNITION",
            "Amazon Comprehend": "COMPREHEND",
            "Amazon Translate": "TRANSLATE",
            # Management & Governance
            "AWS CloudFormation": "CLOUDFORMATION",
            "Amazon CloudWatch": "CLOUDWATCH",
            "AWS CloudTrail": "CLOUDTRAIL",
            "AWS Config": "CONFIG",
            "AWS Organizations": "ORGANIZATIONS",
            # Developer Tools
            "AWS CodeCommit": "CODECOMMIT",
            "AWS CodeBuild": "CODEBUILD",
            "AWS CodePipeline": "CODEPIPELINE",
            "AWS CodeDeploy": "CODEDEPLOY",
        }

        # Try exact match first
        if billing_service_name in service_mappings:
            return service_mappings[billing_service_name]

        # Try partial matches for services not in the mapping
        billing_lower = billing_service_name.lower()

        # Extract service name from billing strings
        if "amazon" in billing_lower:
            service_part = billing_service_name.replace("Amazon ", "").replace(
                "AWS ", ""
            )
            # Convert to uppercase and replace spaces/hyphens
            return service_part.upper().replace(" ", "").replace("-", "")[:20]
        elif "aws" in billing_lower:
            service_part = billing_service_name.replace("AWS ", "").replace(
                "Amazon ", ""
            )
            return service_part.upper().replace(" ", "").replace("-", "")[:20]

        # Fallback: return cleaned up version
        return billing_service_name.upper().replace(" ", "").replace("-", "")[:20]

    def _validate_discovery_with_billing(self):
        """Cross-validate ResourceGroupsTagging discovery with billing data."""
        if not self.enable_billing_validation:
            return

        discovered_services = self._get_discovered_services()

        # Find services with billing usage but no discovered resources
        missing_services = self.billing_validated_services - discovered_services

        if missing_services:
            self.logger.warning(
                f"Found {len(missing_services)} services with billing usage but no discovered resources:"
            )
            for service in sorted(missing_services):
                spend = self.billing_spend_by_service.get(service, 0)
                self.logger.warning(
                    f"  💸 {service}: ${spend:.2f} (may have untagged resources)"
                )

        # Find services with discovered resources but no billing usage
        unbilled_services = discovered_services - self.billing_validated_services
        if unbilled_services:
            self.logger.info(
                f"Found {len(unbilled_services)} services with discovered resources but no recent billing:"
            )
            for service in sorted(unbilled_services):
                self.logger.info(f"  🆓 {service}: (free tier or no recent usage)")

    def _discover_missing_billing_services(self):
        """Attempt to discover resources for services that have billing usage but no discovered resources."""
        if not self.enable_billing_validation:
            return

        discovered_services = self._get_discovered_services()
        missing_services = self.billing_validated_services - discovered_services

        if not missing_services:
            return

        self.logger.info(
            f"Attempting targeted discovery for {len(missing_services)} services with billing usage..."
        )

        # Attempt service-specific discovery for missing services
        for service in missing_services:
            spend = self.billing_spend_by_service.get(service, 0)
            self.logger.info(f"Targeting {service} (${spend:.2f} spend)...")

            try:
                self._discover_service_by_name(service)
            except Exception as e:
                self.logger.warning(f"Failed to discover resources for {service}: {e}")

    def _discover_service_by_name(self, service_name: str):
        """Dynamically discover resources for a service using generic AWS API calls."""
        service_normalized = self._normalize_service_name(service_name.lower())

        # Get the AWS service client name from the service name
        service_client_name = self._get_service_client_name(service_name)

        if not service_client_name:
            self.logger.debug(f"No client mapping found for service: {service_name}")
            return

        self.logger.info(
            f"Attempting dynamic discovery for service: {service_normalized} (client: {service_client_name})"
        )

        for region in self.regions:
            try:
                self._discover_service_dynamically(
                    service_client_name, service_normalized, region
                )
            except Exception as e:
                self.logger.warning(
                    f"Dynamic discovery failed for {service_name} in {region}: {e}"
                )

    def _get_discovered_services(self) -> Set[str]:
        """Get set of services that have been discovered."""
        return set(resource.get("service", "").upper() for resource in self.resources)

    def _add_billing_metadata(self):
        """Add billing metadata to discovered resources."""
        if not self.enable_billing_validation:
            return

        for resource in self.resources:
            service = resource.get("service", "").upper()
            if service in self.billing_spend_by_service:
                resource["billing_validated"] = True
                resource["service_monthly_spend"] = self.billing_spend_by_service[
                    service
                ]
            else:
                resource["billing_validated"] = False
                resource["service_monthly_spend"] = 0.0

    def _discover_via_resource_groups_tagging_api(self):
        """Use Resource Groups Tagging API to discover all taggable resources."""
        self.logger.info("Discovering resources via ResourceGroupsTagging API...")

        for region in self.regions:
            try:
                rgt_client = self.session.client(
                    "resourcegroupstaggingapi", region_name=region
                )

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
                                    resource_type, resource_id = resource_part.split(
                                        "/", 1
                                    )
                                else:
                                    resource_type = resource_part
                                    resource_id = resource_part

                                # Convert tag list to dictionary
                                tags = {
                                    tag["Key"]: tag["Value"]
                                    for tag in resource.get("Tags", [])
                                }

                                # Create resource entry with normalized service name
                                normalized_service = self._normalize_service_name(
                                    service
                                )
                                resource_entry = {
                                    "service": normalized_service,
                                    "type": self._normalize_resource_type(
                                        service, resource_type
                                    ),
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
                                if self.services and service.upper() not in [
                                    s.upper() for s in self.services
                                ]:
                                    continue

                                # Apply tag filters if specified
                                if self.tag_filters and not self._matches_tag_filters(
                                    tags
                                ):
                                    continue

                                self.resources.append(resource_entry)
                                region_resources += 1

                        except Exception as e:
                            self.logger.warning(
                                f"Failed to process resource {resource.get('ResourceARN', 'unknown')}: {e}"
                            )
                            continue

                self.logger.info(
                    f"Found {region_resources} resources in region {region} via ResourceGroupsTagging API"
                )

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code == "UnauthorizedOperation":
                    self.logger.warning(
                        f"No permission for ResourceGroupsTagging API in region {region}"
                    )
                else:
                    self.logger.warning(
                        f"ResourceGroupsTagging API failed in region {region}: {e}"
                    )
            except Exception as e:
                self.logger.warning(
                    f"ResourceGroupsTagging API failed in region {region}: {e}"
                )

    def _normalize_service_name(self, service: str) -> str:
        """Normalize service names for consistent display across discovery methods."""
        # Mapping from AWS service identifiers to consistent display names
        service_normalizations = {
            # Compute
            "ec2": "EC2",
            "lambda": "Lambda",
            "ecs": "ECS",
            "eks": "EKS",
            "batch": "Batch",
            "elasticbeanstalk": "Elastic Beanstalk",
            # Storage
            "s3": "S3",
            "ebs": "EBS",
            "efs": "EFS",
            "fsx": "FSx",
            # Database
            "rds": "RDS",
            "dynamodb": "DynamoDB",
            "elasticache": "ElastiCache",
            "redshift": "Redshift",
            "neptune": "Neptune",
            "documentdb": "DocumentDB",
            # Networking
            "vpc": "VPC",
            "elb": "ELB",
            "elbv2": "ELB",
            "cloudfront": "CloudFront",
            "route53": "Route 53",
            "directconnect": "Direct Connect",
            "apigateway": "API Gateway",
            "apigatewayv2": "API Gateway",
            # Security & Identity
            "iam": "IAM",
            "cognito-idp": "Cognito",
            "cognito-identity": "Cognito",
            "secretsmanager": "Secrets Manager",
            "acm": "ACM",
            "kms": "KMS",
            "keymanagementservice": "KMS",
            "waf": "WAF",
            "wafv2": "WAF",
            "shield": "Shield",
            # Management & Governance
            "cloudwatch": "CloudWatch",
            "amazoncloudwatch": "CloudWatch",
            "cloudwatchevents": "CloudWatch Events",
            "cloudformation": "CloudFormation",
            "cloudtrail": "CloudTrail",
            "config": "Config",
            "organizations": "Organizations",
            "ssm": "Systems Manager",
            # Developer Tools
            "codecommit": "CodeCommit",
            "codebuild": "CodeBuild",
            "codepipeline": "CodePipeline",
            "codedeploy": "CodeDeploy",
            # Application Integration
            "sns": "SNS",
            "sqs": "SQS",
            "kinesis": "Kinesis",
            "stepfunctions": "Step Functions",
            # Analytics
            "glue": "Glue",
            "athena": "Athena",
            "quicksight": "QuickSight",
            "elasticsearch": "Elasticsearch",
            # Machine Learning
            "sagemaker": "SageMaker",
            "rekognition": "Rekognition",
            "comprehend": "Comprehend",
            "translate": "Translate",
        }

        service_lower = service.lower()
        return service_normalizations.get(service_lower, service.upper())

    def _get_service_client_name(self, service_name: str) -> Optional[str]:
        """Map service names to boto3 client names for dynamic discovery."""
        service_lower = service_name.lower()

        # Mapping from service identifiers to boto3 client names
        service_client_mapping = {
            # Core services
            "ec2": "ec2",
            "lambda": "lambda",
            "s3": "s3",
            "rds": "rds",
            "dynamodb": "dynamodb",
            "iam": "iam",
            "vpc": "ec2",
            # Management & Governance
            "cloudwatch": "cloudwatch",
            "amazoncloudwatch": "cloudwatch",
            "cloudwatchevents": "events",
            "cloudtrail": "cloudtrail",
            "cloudformation": "cloudformation",
            "config": "config",
            "ssm": "ssm",
            "organizations": "organizations",
            # Security & Identity
            "acm": "acm",
            "kms": "kms",
            "keymanagementservice": "kms",
            "secretsmanager": "secretsmanager",
            "waf": "waf",
            "wafv2": "wafv2",
            "shield": "shield",
            # Storage
            "efs": "efs",
            "fsx": "fsx",
            "backup": "backup",
            # Database
            "elasticache": "elasticache",
            "redshift": "redshift",
            "neptune": "neptune",
            "docdb": "docdb",
            "documentdb": "docdb",
            # Networking
            "elb": "elbv2",
            "elbv2": "elbv2",
            "route53": "route53",
            "cloudfront": "cloudfront",
            "directconnect": "directconnect",
            "apigateway": "apigateway",
            "apigatewayv2": "apigatewayv2",
            # Application Integration
            "sns": "sns",
            "sqs": "sqs",
            "kinesis": "kinesis",
            "stepfunctions": "stepfunctions",
            # Analytics
            "glue": "glue",
            "athena": "athena",
            "quicksight": "quicksight",
            "elasticsearch": "es",
            "opensearch": "opensearch",
            # Compute
            "ecs": "ecs",
            "eks": "eks",
            "batch": "batch",
            "elasticbeanstalk": "elasticbeanstalk",
            # Machine Learning
            "sagemaker": "sagemaker",
            "rekognition": "rekognition",
            "comprehend": "comprehend",
            "translate": "translate",
            # Developer Tools
            "codecommit": "codecommit",
            "codebuild": "codebuild",
            "codepipeline": "codepipeline",
            "codedeploy": "codedeploy",
            # Business Applications
            "workmail": "workmail",
            "amazonworkmail": "workmail",
            "connect": "connect",
            "chime": "chime",
            # Other
            "support": "support",
            "trustedadvisor": "support",
        }

        return service_client_mapping.get(service_lower)

    def _discover_service_dynamically(
        self, client_name: str, service_display_name: str, region: str
    ):
        """Dynamically discover resources for a service using its AWS API."""
        try:
            client = self.session.client(client_name, region_name=region)

            # Get all available operations for this client
            available_operations = client._service_model.operation_names

            # Common list operations that typically return resources
            list_operations = [
                op
                for op in available_operations
                if op.startswith(("List", "Describe", "Get"))
                and not any(
                    skip in op
                    for skip in ["Policy", "Version", "Status", "Health", "Metrics"]
                )
            ]

            # Priority list operations (most likely to return actual resources)
            priority_operations = [
                op
                for op in list_operations
                if any(
                    keyword in op
                    for keyword in [
                        "List",
                        "DescribeInstances",
                        "DescribeVolumes",
                        "DescribeClusters",
                        "DescribeServices",
                        "DescribeTables",
                        "DescribeBuckets",
                        "DescribeFunctions",
                        "DescribeStacks",
                        "DescribeAlarms",
                        "DescribeRules",
                        "DescribeKeys",
                        "DescribeCertificates",
                        "DescribeQueues",
                        "DescribeTopics",
                    ]
                )
            ]

            operations_to_try = (
                priority_operations[:5] if priority_operations else list_operations[:3]
            )

            self.logger.debug(
                f"Trying {len(operations_to_try)} operations for {service_display_name} in {region}"
            )

            for operation_name in operations_to_try:
                try:
                    self._call_operation_and_extract_resources(
                        client, operation_name, service_display_name, region
                    )
                except Exception as e:
                    self.logger.debug(
                        f"Operation {operation_name} failed for {service_display_name}: {e}"
                    )
                    continue

        except Exception as e:
            self.logger.warning(
                f"Failed to create client for {client_name} in {region}: {e}"
            )

    def _call_operation_and_extract_resources(
        self, client, operation_name: str, service_name: str, region: str
    ):
        """Call an AWS API operation and generically extract resource information."""
        try:
            # Get the operation model to understand parameters
            operation_model = client._service_model.operation_model(operation_name)

            # Convert PascalCase operation name to snake_case for boto3
            snake_case_operation = self._pascal_to_snake_case(operation_name)
            operation = getattr(client, snake_case_operation)

            # Handle paginated operations
            if hasattr(client, "get_paginator"):
                try:
                    paginator = client.get_paginator(snake_case_operation)
                    response_data = []
                    for page in paginator.paginate():
                        response_data.append(page)
                except:
                    # Fallback to direct call
                    response_data = [operation()]
            else:
                response_data = [operation()]

            # Extract resources from the response
            for response in response_data:
                self._extract_resources_from_response(
                    response, service_name, region, operation_name
                )

        except Exception as e:
            # Don't log every failed operation as it's expected for some services
            raise

    def _extract_resources_from_response(
        self, response: dict, service_name: str, region: str, operation_name: str
    ):
        """Extract resource information from AWS API response generically."""
        if not isinstance(response, dict):
            return

        # Common response keys that contain resource lists
        resource_list_keys = [
            # Generic patterns
            key
            for key in response.keys()
            if any(
                pattern in key
                for pattern in [
                    "List",
                    "Items",
                    "Resources",
                    "Results",
                    "Stacks",
                    "Instances",
                    "Volumes",
                    "Buckets",
                    "Functions",
                    "Tables",
                    "Clusters",
                    "Services",
                    "Alarms",
                    "Rules",
                    "Keys",
                    "Certificates",
                    "Queues",
                    "Topics",
                    "Databases",
                    "Snapshots",
                    "Images",
                    "Groups",
                    "Policies",
                ]
            )
        ]

        for key in resource_list_keys:
            resource_list = response.get(key, [])
            if isinstance(resource_list, list):
                for resource_data in resource_list:
                    if isinstance(resource_data, dict):
                        self._create_resource_from_api_data(
                            resource_data, service_name, region, operation_name, key
                        )

    def _create_resource_from_api_data(
        self,
        resource_data: dict,
        service_name: str,
        region: str,
        operation_name: str,
        list_key: str,
    ):
        """Create a standardized resource entry from AWS API data."""
        try:
            # Extract common fields that most AWS resources have
            resource_id = self._extract_resource_id(resource_data)
            resource_name = self._extract_resource_name(resource_data)
            resource_arn = resource_data.get("Arn") or resource_data.get("ARN") or ""

            if not resource_id:
                return  # Skip if we can't identify the resource

            # Determine resource type from the operation name and data
            resource_type = self._determine_resource_type(
                operation_name, list_key, resource_data
            )

            # Extract tags if present
            tags = self._extract_tags(resource_data)

            # Create the standardized resource entry
            resource_entry = {
                "service": service_name,
                "type": resource_type,
                "region": region,
                "id": resource_id,
                "name": resource_name or resource_id,
                "arn": resource_arn,
                "tags": tags,
                "discovered_via": "DynamicDiscovery",
                "api_operation": operation_name,
                "discovered_at": datetime.utcnow().isoformat(),
                "raw_data": resource_data,  # Include raw data for debugging/enhancement
            }

            self.resources.append(resource_entry)

        except Exception as e:
            self.logger.debug(f"Failed to create resource from API data: {e}")

    def _extract_resource_id(self, resource_data: dict) -> Optional[str]:
        """Extract resource ID from AWS API response data."""
        # Common ID fields in AWS API responses
        id_fields = [
            "Id",
            "ResourceId",
            "InstanceId",
            "VolumeId",
            "ClusterId",
            "ServiceName",
            "FunctionName",
            "TableName",
            "BucketName",
            "StackName",
            "AlarmName",
            "RuleName",
            "KeyId",
            "CertificateArn",
            "QueueUrl",
            "TopicArn",
            "Name",
            "DBInstanceIdentifier",
            "DBClusterIdentifier",
            "UserPoolId",
            "RestApiId",
        ]

        for field in id_fields:
            if field in resource_data and resource_data[field]:
                return str(resource_data[field])

        # Fallback: use the first string field as ID
        for key, value in resource_data.items():
            if isinstance(value, str) and len(value) > 0 and len(value) < 200:
                return value

        return None

    def _extract_resource_name(self, resource_data: dict) -> Optional[str]:
        """Extract resource name from AWS API response data."""
        name_fields = ["Name", "ResourceName", "DisplayName", "Title", "Label"]

        for field in name_fields:
            if field in resource_data and resource_data[field]:
                return str(resource_data[field])

        return None

    def _determine_resource_type(
        self, operation_name: str, list_key: str, resource_data: dict
    ) -> str:
        """Determine resource type from operation name and response data."""
        # Extract type from operation name
        if operation_name.startswith("Describe"):
            type_from_op = operation_name[8:]  # Remove 'Describe'
        elif operation_name.startswith("List"):
            type_from_op = operation_name[4:]  # Remove 'List'
        elif operation_name.startswith("Get"):
            type_from_op = operation_name[3:]  # Remove 'Get'
        else:
            type_from_op = operation_name

        # Clean up the type name
        type_from_op = type_from_op.rstrip("s")  # Remove plural 's'

        # Check if resource_data has a Type field
        if "Type" in resource_data:
            return resource_data["Type"]
        elif "ResourceType" in resource_data:
            return resource_data["ResourceType"]

        return type_from_op

    def _extract_tags(self, resource_data: dict) -> dict:
        """Extract tags from AWS API response data."""
        tags = {}

        # Different tag formats in AWS APIs
        if "Tags" in resource_data:
            tag_data = resource_data["Tags"]
            if isinstance(tag_data, list):
                # List of {"Key": "key", "Value": "value"} format
                for tag in tag_data:
                    if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                        tags[tag["Key"]] = tag["Value"]
            elif isinstance(tag_data, dict):
                # Direct key-value mapping
                tags.update(tag_data)

        elif "TagList" in resource_data:
            for tag in resource_data.get("TagList", []):
                if isinstance(tag, dict) and "Key" in tag and "Value" in tag:
                    tags[tag["Key"]] = tag["Value"]

        return tags

    def _pascal_to_snake_case(self, pascal_string: str) -> str:
        """Convert PascalCase to snake_case for boto3 method names."""
        import re

        # Insert underscore before uppercase letters (except the first one)
        snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", pascal_string)
        return snake.lower()

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
            elif (
                isinstance(filter_value, list) and tags[filter_key] not in filter_value
            ):
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
        self.logger.info(
            "Running service-specific discovery for enhanced resource details..."
        )

        # Get existing services from ResourceGroupsTagging discovery
        discovered_services = set(r.get("service", "").upper() for r in self.resources)

        for region in self.regions:
            self.logger.info(f"Enhanced scanning region: {region}")

            # Only run service-specific discovery for services we found via RGT API
            if "EC2" in discovered_services:
                self._enhance_ec2_resources(region)
                self._enhance_vpc_resources(
                    region
                )  # VPC resources are part of EC2 service
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
                self._discover_cloudwatch_resources(region)

    def _deduplicate_resources(self):
        """Remove duplicate resources based on ARN."""
        seen_arns = set()
        deduplicated = []

        for resource in self.resources:
            arn = resource.get("arn", "")
            # Create a unique key for resources without ARNs
            unique_key = (
                arn
                or f"{resource.get('service', '')}-{resource.get('type', '')}-{resource.get('id', '')}-{resource.get('region', '')}"
            )

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
        return self._discover_cloudwatch_resources(region)

    # Additional service discovery methods for billing-validated services
    def _discover_rds_comprehensive(self, region: str):
        """Comprehensive RDS discovery including all resource types."""
        try:
            rds = self.session.client("rds", region_name=region)

            # DB Instances, Clusters, Snapshots, Parameter Groups, etc.
            resources_found = []

            # DB Instances
            try:
                instances = rds.describe_db_instances()
                for instance in instances["DBInstances"]:
                    self.resources.append(
                        {
                            "service": "RDS",
                            "type": "DB Instance",
                            "region": region,
                            "id": instance["DBInstanceIdentifier"],
                            "name": instance["DBInstanceIdentifier"],
                            "arn": instance.get("DBInstanceArn", ""),
                            "engine": instance["Engine"],
                            "status": instance["DBInstanceStatus"],
                            "discovered_via": "BillingTargetedDiscovery",
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
                    resources_found.append("DB Instance")
            except Exception as e:
                self.logger.warning(
                    f"Failed to discover RDS instances in {region}: {e}"
                )

            # DB Clusters
            try:
                clusters = rds.describe_db_clusters()
                for cluster in clusters["DBClusters"]:
                    self.resources.append(
                        {
                            "service": "RDS",
                            "type": "DB Cluster",
                            "region": region,
                            "id": cluster["DBClusterIdentifier"],
                            "name": cluster["DBClusterIdentifier"],
                            "arn": cluster.get("DBClusterArn", ""),
                            "engine": cluster["Engine"],
                            "status": cluster["Status"],
                            "discovered_via": "BillingTargetedDiscovery",
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
                    resources_found.append("DB Cluster")
            except Exception as e:
                self.logger.warning(f"Failed to discover RDS clusters in {region}: {e}")

            if resources_found:
                self.logger.info(
                    f"RDS targeted discovery in {region}: {', '.join(set(resources_found))}"
                )

        except ClientError as e:
            self.logger.warning(f"RDS comprehensive discovery failed in {region}: {e}")

    def _discover_dynamodb_resources(self, region: str):
        """Discover DynamoDB resources."""
        try:
            dynamodb = self.session.client("dynamodb", region_name=region)

            tables = dynamodb.list_tables()
            for table_name in tables["TableNames"]:
                try:
                    table_details = dynamodb.describe_table(TableName=table_name)
                    table = table_details["Table"]

                    self.resources.append(
                        {
                            "service": "DYNAMODB",
                            "type": "Table",
                            "region": region,
                            "id": table_name,
                            "name": table_name,
                            "arn": table.get("TableArn", ""),
                            "status": table["TableStatus"],
                            "discovered_via": "BillingTargetedDiscovery",
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to get details for DynamoDB table {table_name}: {e}"
                    )

        except ClientError as e:
            self.logger.warning(f"DynamoDB discovery failed in {region}: {e}")

    def _discover_elasticache_resources(self, region: str):
        """Discover ElastiCache resources."""
        try:
            elasticache = self.session.client("elasticache", region_name=region)

            # Redis clusters
            try:
                redis_clusters = elasticache.describe_cache_clusters()
                for cluster in redis_clusters["CacheClusters"]:
                    self.resources.append(
                        {
                            "service": "ELASTICACHE",
                            "type": "Cache Cluster",
                            "region": region,
                            "id": cluster["CacheClusterId"],
                            "name": cluster["CacheClusterId"],
                            "engine": cluster["Engine"],
                            "status": cluster["CacheClusterStatus"],
                            "discovered_via": "BillingTargetedDiscovery",
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    f"Failed to discover ElastiCache clusters in {region}: {e}"
                )

        except ClientError as e:
            self.logger.warning(f"ElastiCache discovery failed in {region}: {e}")

    def _discover_redshift_resources(self, region: str):
        """Discover Redshift resources."""
        try:
            redshift = self.session.client("redshift", region_name=region)

            clusters = redshift.describe_clusters()
            for cluster in clusters["Clusters"]:
                self.resources.append(
                    {
                        "service": "REDSHIFT",
                        "type": "Cluster",
                        "region": region,
                        "id": cluster["ClusterIdentifier"],
                        "name": cluster["ClusterIdentifier"],
                        "status": cluster["ClusterStatus"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Redshift discovery failed in {region}: {e}")

    def _discover_elb_resources(self, region: str):
        """Discover ELB/ALB/NLB resources."""
        try:
            # ELBv2 (ALB/NLB)
            elbv2 = self.session.client("elbv2", region_name=region)
            load_balancers = elbv2.describe_load_balancers()

            for lb in load_balancers["LoadBalancers"]:
                self.resources.append(
                    {
                        "service": "ELB",
                        "type": f"{lb['Type'].upper()}",
                        "region": region,
                        "id": lb["LoadBalancerName"],
                        "name": lb["LoadBalancerName"],
                        "arn": lb["LoadBalancerArn"],
                        "status": lb["State"]["Code"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"ELB discovery failed in {region}: {e}")

    def _discover_apigateway_resources(self, region: str):
        """Discover API Gateway resources."""
        try:
            apigw = self.session.client("apigateway", region_name=region)

            # REST APIs
            rest_apis = apigw.get_rest_apis()
            for api in rest_apis["items"]:
                self.resources.append(
                    {
                        "service": "APIGATEWAY",
                        "type": "REST API",
                        "region": region,
                        "id": api["id"],
                        "name": api["name"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"API Gateway discovery failed in {region}: {e}")

    def _discover_sns_resources(self, region: str):
        """Discover SNS resources."""
        try:
            sns = self.session.client("sns", region_name=region)

            topics = sns.list_topics()
            for topic in topics["Topics"]:
                topic_arn = topic["TopicArn"]
                topic_name = topic_arn.split(":")[-1]

                self.resources.append(
                    {
                        "service": "SNS",
                        "type": "Topic",
                        "region": region,
                        "id": topic_name,
                        "name": topic_name,
                        "arn": topic_arn,
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"SNS discovery failed in {region}: {e}")

    def _discover_sqs_resources(self, region: str):
        """Discover SQS resources."""
        try:
            sqs = self.session.client("sqs", region_name=region)

            queues = sqs.list_queues()
            for queue_url in queues.get("QueueUrls", []):
                queue_name = queue_url.split("/")[-1]

                self.resources.append(
                    {
                        "service": "SQS",
                        "type": "Queue",
                        "region": region,
                        "id": queue_name,
                        "name": queue_name,
                        "queue_url": queue_url,
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"SQS discovery failed in {region}: {e}")

    def _discover_kinesis_resources(self, region: str):
        """Discover Kinesis resources."""
        try:
            kinesis = self.session.client("kinesis", region_name=region)

            streams = kinesis.list_streams()
            for stream_name in streams["StreamNames"]:
                self.resources.append(
                    {
                        "service": "KINESIS",
                        "type": "Stream",
                        "region": region,
                        "id": stream_name,
                        "name": stream_name,
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Kinesis discovery failed in {region}: {e}")

    def _discover_stepfunctions_resources(self, region: str):
        """Discover Step Functions resources."""
        try:
            sfn = self.session.client("stepfunctions", region_name=region)

            state_machines = sfn.list_state_machines()
            for sm in state_machines["stateMachines"]:
                self.resources.append(
                    {
                        "service": "STEPFUNCTIONS",
                        "type": "State Machine",
                        "region": region,
                        "id": sm["name"],
                        "name": sm["name"],
                        "arn": sm["stateMachineArn"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Step Functions discovery failed in {region}: {e}")

    def _discover_secretsmanager_resources(self, region: str):
        """Discover Secrets Manager resources."""
        try:
            secrets = self.session.client("secretsmanager", region_name=region)

            secret_list = secrets.list_secrets()
            for secret in secret_list["SecretList"]:
                self.resources.append(
                    {
                        "service": "SECRETSMANAGER",
                        "type": "Secret",
                        "region": region,
                        "id": secret["Name"],
                        "name": secret["Name"],
                        "arn": secret["ARN"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Secrets Manager discovery failed in {region}: {e}")

    def _discover_ssm_resources(self, region: str):
        """Discover Systems Manager resources."""
        try:
            ssm = self.session.client("ssm", region_name=region)

            # Parameters
            try:
                parameters = ssm.describe_parameters()
                for param in parameters["Parameters"]:
                    self.resources.append(
                        {
                            "service": "SSM",
                            "type": "Parameter",
                            "region": region,
                            "id": param["Name"],
                            "name": param["Name"],
                            "discovered_via": "BillingTargetedDiscovery",
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    f"Failed to discover SSM parameters in {region}: {e}"
                )

        except ClientError as e:
            self.logger.warning(f"SSM discovery failed in {region}: {e}")

    def _discover_route53_resources(self, region: str):
        """Discover Route53 resources (global service)."""
        if region != "us-east-1":  # Route53 is global
            return

        try:
            route53 = self.session.client("route53", region_name=region)

            hosted_zones = route53.list_hosted_zones()
            for zone in hosted_zones["HostedZones"]:
                self.resources.append(
                    {
                        "service": "ROUTE53",
                        "type": "Hosted Zone",
                        "region": "global",
                        "id": zone["Id"].split("/")[-1],
                        "name": zone["Name"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"Route53 discovery failed: {e}")

    def _discover_cloudfront_resources(self, region: str):
        """Discover CloudFront resources (global service)."""
        if region != "us-east-1":  # CloudFront is global
            return

        try:
            cloudfront = self.session.client("cloudfront", region_name=region)

            distributions = cloudfront.list_distributions()
            for dist in distributions.get("DistributionList", {}).get("Items", []):
                self.resources.append(
                    {
                        "service": "CLOUDFRONT",
                        "type": "Distribution",
                        "region": "global",
                        "id": dist["Id"],
                        "name": dist.get("DomainName", dist["Id"]),
                        "status": dist["Status"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"CloudFront discovery failed: {e}")

    def _discover_acm_resources(self, region: str):
        """Discover ACM (Certificate Manager) resources."""
        try:
            acm = self.session.client("acm", region_name=region)

            certificates = acm.list_certificates()
            for cert in certificates["CertificateSummaryList"]:
                self.resources.append(
                    {
                        "service": "ACM",
                        "type": "Certificate",
                        "region": region,
                        "id": cert["CertificateArn"].split("/")[-1],
                        "name": cert["DomainName"],
                        "arn": cert["CertificateArn"],
                        "status": cert["Status"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"ACM discovery failed in {region}: {e}")

    def _discover_waf_resources(self, region: str):
        """Discover WAF resources."""
        try:
            waf = self.session.client("wafv2", region_name=region)

            # Web ACLs
            web_acls = waf.list_web_acls(Scope="REGIONAL")
            for acl in web_acls["WebACLs"]:
                self.resources.append(
                    {
                        "service": "WAF",
                        "type": "Web ACL",
                        "region": region,
                        "id": acl["Id"],
                        "name": acl["Name"],
                        "arn": acl["ARN"],
                        "discovered_via": "BillingTargetedDiscovery",
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(f"WAF discovery failed in {region}: {e}")

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

    def _discover_cloudwatch_resources(self, region: str):
        """Discover CloudWatch resources using CloudWatch API."""
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

    def _discover_cloudtrail_resources(self, region: str):
        """Discover CloudTrail resources."""
        try:
            client = self.session.client("cloudtrail", region_name=region)

            # CloudTrail trails
            trails_response = client.describe_trails()
            for trail in trails_response["trailList"]:
                self.resources.append(
                    {
                        "service": "CloudTrail",
                        "type": "Trail",
                        "region": region,
                        "id": trail["Name"],
                        "name": trail["Name"],
                        "arn": trail.get("TrailARN", ""),
                        "home_region": trail.get("HomeRegion", ""),
                        "is_multi_region": trail.get(
                            "IncludeGlobalServiceEvents", False
                        ),
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(
                f"Failed to discover CloudTrail resources in {region}: {e}"
            )

    def _discover_kms_resources(self, region: str):
        """Discover KMS resources."""
        try:
            client = self.session.client("kms", region_name=region)

            # KMS keys
            keys_response = client.list_keys()
            for key in keys_response["Keys"]:
                try:
                    key_details = client.describe_key(KeyId=key["KeyId"])
                    key_metadata = key_details["KeyMetadata"]

                    self.resources.append(
                        {
                            "service": "KMS",
                            "type": "Key",
                            "region": region,
                            "id": key["KeyId"],
                            "name": key_metadata.get("Description", ""),
                            "arn": key_metadata.get("Arn", ""),
                            "key_usage": key_metadata.get("KeyUsage", ""),
                            "key_state": key_metadata.get("KeyState", ""),
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
                except ClientError as key_error:
                    # Skip keys we can't access
                    continue

        except ClientError as e:
            self.logger.warning(f"Failed to discover KMS resources in {region}: {e}")

    def _discover_glue_resources(self, region: str):
        """Discover Glue resources."""
        try:
            client = self.session.client("glue", region_name=region)

            # Glue databases
            try:
                databases_response = client.get_databases()
                for database in databases_response["DatabaseList"]:
                    self.resources.append(
                        {
                            "service": "Glue",
                            "type": "Database",
                            "region": region,
                            "id": database["Name"],
                            "name": database["Name"],
                            "description": database.get("Description", ""),
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
            except ClientError:
                pass  # Skip if no permissions

            # Glue tables
            try:
                tables_response = client.get_tables()
                for table in tables_response["TableList"]:
                    self.resources.append(
                        {
                            "service": "Glue",
                            "type": "Table",
                            "region": region,
                            "id": table["Name"],
                            "name": table["Name"],
                            "database": table.get("DatabaseName", ""),
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
            except ClientError:
                pass  # Skip if no permissions

        except ClientError as e:
            self.logger.warning(f"Failed to discover Glue resources in {region}: {e}")

    def _discover_cloudwatch_events_resources(self, region: str):
        """Discover CloudWatch Events resources."""
        try:
            client = self.session.client("events", region_name=region)

            # EventBridge rules
            rules_response = client.list_rules()
            for rule in rules_response["Rules"]:
                self.resources.append(
                    {
                        "service": "CloudWatch Events",
                        "type": "Rule",
                        "region": region,
                        "id": rule["Name"],
                        "name": rule["Name"],
                        "arn": rule.get("Arn", ""),
                        "state": rule.get("State", ""),
                        "description": rule.get("Description", ""),
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

            # Event buses
            buses_response = client.list_event_buses()
            for bus in buses_response["EventBuses"]:
                self.resources.append(
                    {
                        "service": "CloudWatch Events",
                        "type": "Event Bus",
                        "region": region,
                        "id": bus["Name"],
                        "name": bus["Name"],
                        "arn": bus.get("Arn", ""),
                        "discovered_at": datetime.utcnow().isoformat(),
                    }
                )

        except ClientError as e:
            self.logger.warning(
                f"Failed to discover CloudWatch Events resources in {region}: {e}"
            )

    def _discover_workmail_resources(self, region: str):
        """Discover WorkMail resources."""
        try:
            client = self.session.client("workmail", region_name=region)

            # WorkMail organizations
            try:
                orgs_response = client.list_organizations()
                for org in orgs_response["OrganizationSummaries"]:
                    self.resources.append(
                        {
                            "service": "WorkMail",
                            "type": "Organization",
                            "region": region,
                            "id": org["OrganizationId"],
                            "name": org.get("Alias", org["OrganizationId"]),
                            "state": org.get("State", ""),
                            "discovered_at": datetime.utcnow().isoformat(),
                        }
                    )
            except ClientError as e:
                if (
                    e.response.get("Error", {}).get("Code")
                    == "OrganizationNotFoundException"
                ):
                    # No WorkMail organizations in this region
                    pass
                else:
                    raise

        except ClientError as e:
            self.logger.warning(
                f"Failed to discover WorkMail resources in {region}: {e}"
            )

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
