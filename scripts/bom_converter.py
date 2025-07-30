#!/usr/bin/env python3
"""
InvenTag - BOM Converter
Professional AWS™ resource inventory to Excel/CSV converter.

BACKWARD COMPATIBILITY WRAPPER
This script now imports from the unified inventag package while maintaining
identical CLI interfaces and output formats.

Part of InvenTag: Python tool to check on AWS™ cloud inventory and tagging.
Integrate into your CI/CD flow to meet your organization's stringent compliance requirements.

AWS™ is a trademark of Amazon Web Services, Inc. InvenTag is not affiliated with AWS.

Features:
- Creates service-specific Excel sheets for organized reporting
- Intelligent data enhancement with VPC names and account IDs
- Standardizes resource types and IDs across discovery methods
- Professional formatting with summary dashboards
- CI/CD ready for automated compliance workflows

Usage:
    python bom_converter.py --input inventory.json --output report.xlsx
"""

import argparse
import sys
import os
from datetime import datetime

# Import from the unified inventag package
try:
    from inventag.reporting import BOMConverter
except ImportError:
    # Fallback for development/testing
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from inventag.reporting import BOMConverter


def main():
    parser = argparse.ArgumentParser(
        description="InvenTag BOM Converter - Convert AWS inventory to professional reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON inventory to Excel
  python bom_converter.py --input inventory.json --output report.xlsx --format excel

  # Convert to CSV
  python bom_converter.py --input inventory.json --output report.csv --format csv

  # Disable VPC enrichment for faster processing
  python bom_converter.py --input inventory.json --output report.xlsx --no-vpc-enrichment

  # Process compliance checker output
  python bom_converter.py --input compliance_report.json --output bom_report.xlsx --format excel
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input file with resource inventory (JSON or YAML)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output filename (with extension). If not specified, auto-generated based on format",
    )
    parser.add_argument(
        "--format",
        choices=["excel", "csv"],
        default="excel",
        help="Output format (default: excel)",
    )
    parser.add_argument(
        "--no-vpc-enrichment",
        action="store_true",
        help="Disable VPC/subnet name enrichment (faster but less detailed)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        # Initialize BOM converter
        enrich_vpc = not args.no_vpc_enrichment
        converter = BOMConverter(enrich_vpc_info=enrich_vpc)

        # Load data
        print(f"Loading data from {args.input}...")
        data = converter.load_data(args.input)

        if not data:
            print("No data found in input file.")
            sys.exit(1)

        # Generate output filename if not specified
        if not args.output:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            if args.format == "excel":
                args.output = f"{base_name}_bom_{timestamp}.xlsx"
            else:
                args.output = f"{base_name}_bom_{timestamp}.csv"

        # Export data
        print(f"Exporting to {args.format.upper()} format...")
        if args.format == "excel":
            converter.export_to_excel(args.output)
        elif args.format == "csv":
            converter.export_to_csv(args.output)

        print(f"BOM report generated: {args.output}")
        print(f"Total resources processed: {len(data)}")

        # Show service breakdown
        if args.verbose:
            services = {}
            for resource in data:
                service = resource.get("service", "Unknown")
                services[service] = services.get(service, 0) + 1

            print("\nService breakdown:")
            for service, count in sorted(services.items()):
                print(f"  {service}: {count} resources")

    except FileNotFoundError:
        print(f"Error: Input file {args.input} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()