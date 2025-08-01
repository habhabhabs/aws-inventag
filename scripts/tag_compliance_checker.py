#!/usr/bin/env python3
"""
InvenTag - Tag Compliance Checker
Enterprise-grade AWS™ resource tag compliance validation tool.

BACKWARD COMPATIBILITY WRAPPER
This script now imports from the unified inventag package while maintaining
identical CLI interfaces and output formats.

Part of InvenTag: Python tool to check on AWS™ cloud inventory and tagging.
Integrate into your CI/CD flow to meet your organization's stringent compliance requirements.

AWS™ is a trademark of Amazon Web Services, Inc. InvenTag is not affiliated with AWS.

Features:
- Comprehensive tag policy validation across all AWS services
- Multi-method resource discovery (ResourceGroupsTaggingAPI, AWSConfig, Service APIs)
- Professional compliance reporting with Excel output
- CI/CD integration for automated compliance monitoring
- Custom tag policy support with exemptions and patterns

Usage:
    python tag_compliance_checker.py --input inventory.json --output compliance-report.xlsx
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Import from the unified inventag package
try:
    from inventag.compliance import ComprehensiveTagComplianceChecker
except ImportError:
    # Fallback for development/testing
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from inventag.compliance import ComprehensiveTagComplianceChecker


def main():
    parser = argparse.ArgumentParser(
        description="InvenTag - Comprehensive Tag Compliance Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic compliance check with config file
  python tag_compliance_checker.py --config tag_policy.yaml --output compliance_report.json

  # Check compliance from existing inventory file
  python tag_compliance_checker.py --input inventory.json --config tag_policy.yaml

  # Generate Excel report
  python tag_compliance_checker.py --config tag_policy.yaml --output report.xlsx --format excel

  # Upload results to S3
  python tag_compliance_checker.py --config tag_policy.yaml --s3-bucket my-bucket --s3-key compliance/report.json

  # Specify regions to scan
  python tag_compliance_checker.py --config tag_policy.yaml --regions us-east-1 us-west-2
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        help="Tag policy configuration file (JSON or YAML)",
        required=False,
    )
    parser.add_argument(
        "--input",
        "-i",
        help="Input file with existing resource inventory (JSON or YAML)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="compliance_report",
        help="Output filename (without extension, default: compliance_report)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "excel"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--regions", nargs="+", help="AWS regions to scan (default: all regions)"
    )
    parser.add_argument("--s3-bucket", help="S3 bucket to upload results")
    parser.add_argument("--s3-key", help="S3 key for uploaded file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.no_color:
        # Disable colorama
        init(strip=True, convert=False)

    try:
        # Initialize compliance checker
        checker = ComprehensiveTagComplianceChecker(
            regions=args.regions, config_file=args.config
        )

        # Load existing inventory or discover resources
        if args.input:
            print(f"Loading existing inventory from {args.input}...")
            # For backward compatibility, we need to load the data
            import json
            import yaml

            with open(args.input, "r") as f:
                if args.input.lower().endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            # Extract resources from the data structure
            if isinstance(data, list):
                resources = data
            elif isinstance(data, dict):
                # Try common keys
                resources = (
                    data.get("all_discovered_resources")
                    or data.get("resources")
                    or data.get("compliant_resources", [])
                    + data.get("non_compliant_resources", [])
                    + data.get("untagged_resources", [])
                )
            else:
                resources = []

            results = checker.check_compliance(resources)
        else:
            print("Discovering resources and checking compliance...")
            results = checker.check_compliance()

        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if args.format == "excel":
            filename = f"{args.output}_{timestamp}.xlsx"
            # For Excel output, we'll use the BOM converter
            temp_json = f"{args.output}_{timestamp}_temp.json"
            checker.save_results(temp_json, "json")

            # Import and use BOM converter for Excel output
            try:
                from inventag.reporting import BOMConverter

                converter = BOMConverter()
                converter.load_data(temp_json)
                converter.export_to_excel(filename)
                os.remove(temp_json)  # Clean up temp file
            except ImportError:
                print("Warning: Could not generate Excel output. Falling back to JSON.")
                filename = f"{args.output}_{timestamp}.json"
                checker.save_results(filename, "json")
        else:
            filename = f"{args.output}_{timestamp}.{args.format}"
            checker.save_results(filename, args.format)

        # Print summary
        summary = results["summary"]
        total = summary["total_resources"]
        compliant = summary["compliant_resources"]
        non_compliant = summary["non_compliant_resources"]
        untagged = summary["untagged_resources"]
        percentage = summary["compliance_percentage"]

        print(f"\n{Fore.CYAN}=== COMPLIANCE SUMMARY ==={Style.RESET_ALL}")
        print(f"Total resources: {total}")
        print(f"{Fore.GREEN}Compliant: {compliant}{Style.RESET_ALL}")
        print(f"{Fore.RED}Non-compliant: {non_compliant}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Untagged: {untagged}{Style.RESET_ALL}")
        print(f"Compliance rate: {Fore.CYAN}{percentage}%{Style.RESET_ALL}")
        print(f"\nResults saved to {filename}")

        # Upload to S3 if requested
        if args.s3_bucket:
            s3_key = args.s3_key or f"compliance-reports/{filename}"
            checker.upload_to_s3(args.s3_bucket, s3_key, args.format)
            print(f"Results uploaded to s3://{args.s3_bucket}/{s3_key}")

    except NoCredentialsError:
        print(
            f"{Fore.RED}Error: AWS credentials not found. Please configure your AWS credentials.{Style.RESET_ALL}"
        )
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
