#!/usr/bin/env python3
"""
Enhanced BOM Converter Utility
Converts JSON/YAML AWS resource inventory to Excel/CSV format.
Creates separate Excel sheets per AWS service and enriches VPC/subnet information.
Uses minimal dependencies for portability.
"""

import argparse
import json
import yaml
import csv
import sys
import boto3
from typing import Dict, List, Any, Union, Optional
from datetime import datetime
import os
from botocore.exceptions import ClientError


class BOMConverter:
    def __init__(self, enrich_vpc_info: bool = True):
        """Initialize the BOM converter."""
        self.data = []
        self.headers = set()
        self.enrich_vpc_info = enrich_vpc_info
        self.vpc_cache = {}  # Cache for VPC/subnet name lookups
        self.session = boto3.Session() if enrich_vpc_info else None
    
    def load_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from JSON or YAML file."""
        try:
            with open(filename, 'r') as f:
                if filename.lower().endswith('.json'):
                    self.data = json.load(f)
                elif filename.lower().endswith(('.yaml', '.yml')):
                    self.data = yaml.safe_load(f)
                else:
                    # Try to detect format by content
                    content = f.read()
                    try:
                        self.data = json.loads(content)
                    except json.JSONDecodeError:
                        try:
                            self.data = yaml.safe_load(content)
                        except yaml.YAMLError:
                            raise ValueError("Unable to parse file as JSON or YAML")
            
            # Enrich VPC/subnet information if enabled
            if self.enrich_vpc_info:
                self._enrich_vpc_subnet_info()
            
            # Collect all possible headers from the data
            for item in self.data:
                if isinstance(item, dict):
                    self._collect_headers(item)
            
            print(f"Loaded {len(self.data)} resources from {filename}")
            return self.data
            
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)
    
    def _collect_headers(self, item: Dict[str, Any], prefix: str = ""):
        """Recursively collect all possible headers from nested dictionaries."""
        for key, value in item.items():
            header = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # For nested dictionaries, create flattened headers
                self._collect_headers(value, f"{header}.")
            elif isinstance(value, list):
                # For lists, just add the header (we'll stringify the list)
                self.headers.add(header)
            else:
                self.headers.add(header)
    
    def _flatten_dict(self, item: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Flatten nested dictionaries for tabular output."""
        flattened = {}
        
        for key, value in item.items():
            header = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_dict(value, f"{header}."))
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                flattened[header] = ", ".join(str(v) for v in value)
            elif value is None:
                flattened[header] = ""
            else:
                flattened[header] = str(value)
        
        return flattened
    
    def _enrich_vpc_subnet_info(self):
        """Enrich resources with VPC and subnet names."""
        if not self.session:
            return
        
        print("Enriching VPC and subnet information...")
        
        for item in self.data:
            if isinstance(item, dict):
                region = item.get('region', '')
                vpc_id = item.get('vpc_id', '')
                subnet_id = item.get('subnet_id', '')
                
                # Skip global resources or resources without VPC info
                if region in ['global', ''] or (not vpc_id and not subnet_id):
                    continue
                
                try:
                    # Get VPC name if vpc_id exists
                    if vpc_id and vpc_id != '':
                        vpc_name = self._get_vpc_name(region, vpc_id)
                        if vpc_name:
                            item['vpc_name'] = vpc_name
                    
                    # Get subnet name if subnet_id exists
                    if subnet_id and subnet_id != '':
                        subnet_name = self._get_subnet_name(region, subnet_id)
                        if subnet_name:
                            item['subnet_name'] = subnet_name
                
                except Exception as e:
                    # Silently continue if we can't get VPC/subnet info
                    continue
    
    def _get_vpc_name(self, region: str, vpc_id: str) -> Optional[str]:
        """Get VPC name from tags."""
        cache_key = f"{region}:{vpc_id}"
        
        if cache_key in self.vpc_cache:
            return self.vpc_cache[cache_key]
        
        try:
            ec2 = self.session.client('ec2', region_name=region)
            response = ec2.describe_vpcs(VpcIds=[vpc_id])
            
            if response['Vpcs']:
                vpc = response['Vpcs'][0]
                # Look for Name tag
                for tag in vpc.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        self.vpc_cache[cache_key] = name
                        return name
                
                # If no Name tag, cache empty result
                self.vpc_cache[cache_key] = None
                return None
        
        except ClientError:
            # Cache None result for failed lookups to avoid repeated attempts
            self.vpc_cache[cache_key] = None
            return None
    
    def _get_subnet_name(self, region: str, subnet_id: str) -> Optional[str]:
        """Get subnet name from tags."""
        cache_key = f"{region}:{subnet_id}"
        
        if cache_key in self.vpc_cache:
            return self.vpc_cache[cache_key]
        
        try:
            ec2 = self.session.client('ec2', region_name=region)
            response = ec2.describe_subnets(SubnetIds=[subnet_id])
            
            if response['Subnets']:
                subnet = response['Subnets'][0]
                # Look for Name tag
                for tag in subnet.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        self.vpc_cache[cache_key] = name
                        return name
                
                # If no Name tag, cache empty result
                self.vpc_cache[cache_key] = None
                return None
        
        except ClientError:
            # Cache None result for failed lookups to avoid repeated attempts
            self.vpc_cache[cache_key] = None
            return None
    
    def to_csv(self, output_filename: str):
        """Convert data to CSV format with AWS service as a column."""
        try:
            # Sort headers for consistent output, ensuring 'service' comes first
            sorted_headers = sorted(list(self.headers))
            if 'service' in sorted_headers:
                sorted_headers.remove('service')
                sorted_headers.insert(0, 'service')
            
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted_headers)
                writer.writeheader()
                
                for item in self.data:
                    if isinstance(item, dict):
                        flattened = self._flatten_dict(item)
                        # Ensure all headers are present (fill missing with empty string)
                        row = {header: flattened.get(header, '') for header in sorted_headers}
                        writer.writerow(row)
            
            print(f"CSV export saved to {output_filename} (AWS service included as column)")
            
        except Exception as e:
            print(f"Error creating CSV: {e}")
            sys.exit(1)
    
    def to_excel(self, output_filename: str):
        """Convert data to Excel format with separate sheets per AWS service."""
        try:
            # Try to import openpyxl, fall back to CSV if not available
            try:
                from openpyxl import Workbook
                from openpyxl.styles import Font, PatternFill, Alignment
                from openpyxl.utils import get_column_letter
            except ImportError:
                print("Warning: openpyxl not available. Falling back to CSV format.")
                csv_filename = output_filename.replace('.xlsx', '.csv')
                self.to_csv(csv_filename)
                return
            
            # Group resources by service
            resources_by_service = {}
            for item in self.data:
                if isinstance(item, dict):
                    service = item.get('service', 'Unknown')
                    if service not in resources_by_service:
                        resources_by_service[service] = []
                    resources_by_service[service].append(item)
            
            # Create workbook
            wb = Workbook()
            
            # Remove default sheet
            wb.remove(wb.active)
            
            # Create summary sheet first
            self._create_summary_sheet(wb, resources_by_service)
            
            # Create a sheet for each service
            for service_name in sorted(resources_by_service.keys()):
                service_resources = resources_by_service[service_name]
                self._create_service_sheet(wb, service_name, service_resources)
            
            # Save workbook
            wb.save(output_filename)
            print(f"Excel export saved to {output_filename}")
            print(f"Created {len(resources_by_service)} service sheets + summary sheet")
            
        except Exception as e:
            print(f"Error creating Excel file: {e}")
            sys.exit(1)
    
    def _create_summary_sheet(self, wb: 'Workbook', resources_by_service: Dict[str, List[Dict]]):
        """Create summary sheet with overview statistics."""
        from openpyxl.styles import Font, PatternFill, Alignment
        
        summary_ws = wb.create_sheet("Summary", 0)
        
        # Title
        summary_ws.append(["AWS Resource Inventory Summary"])
        summary_ws.cell(1, 1).font = Font(bold=True, size=16)
        summary_ws.append([])
        
        # Basic info
        summary_ws.append(["Generated on:", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')])
        summary_ws.append(["Total Resources:", len(self.data)])
        summary_ws.append(["Total Services:", len(resources_by_service)])
        summary_ws.append([])
        
        # Service breakdown table
        summary_ws.append(["Service Breakdown:"])
        summary_ws.cell(7, 1).font = Font(bold=True, size=12)
        summary_ws.append([])
        
        # Table headers
        headers = ["Service", "Resource Count", "Resource Types"]
        summary_ws.append(headers)
        
        # Format headers
        for col_num, header in enumerate(headers, 1):
            cell = summary_ws.cell(9, col_num)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Service data
        for service_name in sorted(resources_by_service.keys()):
            service_resources = resources_by_service[service_name]
            resource_types = set(item.get('type', 'Unknown') for item in service_resources)
            
            summary_ws.append([
                service_name,
                len(service_resources),
                ", ".join(sorted(resource_types))
            ])
        
        # Auto-adjust column widths
        for col_num in range(1, 4):
            column_letter = get_column_letter(col_num)
            max_length = 10
            
            for row in summary_ws.iter_rows(min_col=col_num, max_col=col_num):
                for cell in row:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
            
            summary_ws.column_dimensions[column_letter].width = min(max_length + 2, 60)
    
    def _create_service_sheet(self, wb: 'Workbook', service_name: str, service_resources: List[Dict]):
        """Create a sheet for a specific AWS service."""
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter
        
        # Sanitize sheet name (Excel sheet names have restrictions)
        safe_service_name = service_name.replace('/', '_').replace('\\', '_')[:31]
        ws = wb.create_sheet(safe_service_name)
        
        # Collect headers specific to this service
        service_headers = set()
        for item in service_resources:
            if isinstance(item, dict):
                self._collect_headers(item, service_headers)
        
        # Sort headers, prioritizing important ones first
        priority_headers = ['service', 'type', 'region', 'id', 'name', 'arn', 'vpc_id', 'vpc_name', 'subnet_id', 'subnet_name']
        sorted_headers = []
        
        # Add priority headers first (if they exist)
        for header in priority_headers:
            if header in service_headers:
                sorted_headers.append(header)
                service_headers.remove(header)
        
        # Add remaining headers
        sorted_headers.extend(sorted(service_headers))
        
        # Write headers with formatting
        for col_num, header in enumerate(sorted_headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Write data rows
        for row_num, item in enumerate(service_resources, 2):
            if isinstance(item, dict):
                flattened = self._flatten_dict(item)
                for col_num, header in enumerate(sorted_headers, 1):
                    value = flattened.get(header, '')
                    ws.cell(row=row_num, column=col_num, value=value)
        
        # Auto-adjust column widths
        for col_num, header in enumerate(sorted_headers, 1):
            column_letter = get_column_letter(col_num)
            max_length = len(header)
            
            # Check data in this column to find max length
            for row_num in range(2, min(102, len(service_resources) + 2)):  # Check first 100 rows
                cell_value = ws.cell(row=row_num, column=col_num).value
                if cell_value:
                    max_length = max(max_length, len(str(cell_value)))
            
            # Set column width (max 50 to avoid extremely wide columns)
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def _collect_headers(self, item: Dict[str, Any], headers_set: set, prefix: str = ""):
        """Collect headers into a specific set (for service-specific sheets)."""
        for key, value in item.items():
            header = f"{prefix}{key}" if prefix else key
            
            if isinstance(value, dict):
                # For nested dictionaries, create flattened headers
                self._collect_headers(value, headers_set, f"{header}.")
            elif isinstance(value, list):
                # For lists, just add the header (we'll stringify the list)
                headers_set.add(header)
            else:
                headers_set.add(header)


def main():
    parser = argparse.ArgumentParser(description='Enhanced BOM Converter - Convert JSON/YAML to Excel/CSV with service sheets and VPC info')
    parser.add_argument('--input', '-i', required=True, 
                       help='Input JSON or YAML file')
    parser.add_argument('--output', '-o', required=True, 
                       help='Output filename')
    parser.add_argument('--format', choices=['excel', 'csv'], default='excel',
                       help='Output format (default: excel)')
    parser.add_argument('--no-vpc-enrichment', action='store_true',
                       help='Skip VPC/subnet name enrichment (faster but less detailed)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # Initialize converter
    enrich_vpc = not args.no_vpc_enrichment
    converter = BOMConverter(enrich_vpc_info=enrich_vpc)
    
    if enrich_vpc:
        print("VPC/subnet name enrichment enabled (use --no-vpc-enrichment to disable)")
    else:
        print("VPC/subnet name enrichment disabled")
    
    # Load data
    converter.load_data(args.input)
    
    # Convert based on format
    if args.format == 'excel':
        # Ensure output has .xlsx extension
        if not args.output.lower().endswith('.xlsx'):
            args.output += '.xlsx'
        converter.to_excel(args.output)
    elif args.format == 'csv':
        # Ensure output has .csv extension
        if not args.output.lower().endswith('.csv'):
            args.output += '.csv'
        converter.to_csv(args.output)


if __name__ == "__main__":
    main()