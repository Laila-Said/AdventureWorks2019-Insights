# =============================================================================
# AdventureWorks Null Handler
# =============================================================================

import pandas as pd
import os
from datetime import datetime

# =============================================================================
# Individual Table Handler Functions
# =============================================================================

def clean_workorder(file_path, output_path=None):
    """Clean nulls in Production WorkOrder table"""
    df = pd.read_excel(file_path, sheet_name="Production WorkOrder")
    print(f"Production WorkOrder: {len(df)} rows")
    
    # ScrapReasonID has 71,862 nulls out of 72,591 rows (98.9%)
    # Since almost all rows have null ScrapReasonID, this appears to be
    # an optional field that's only populated when a product is scrapped
    
    # Option 1: Keep nulls (recommended for analysis)
    df_clean = df.copy()
    print("Keeping ScrapReasonID nulls as they represent non-scrapped items")
    
    # Option 2: Fill with 0 (if you need a numeric value for all rows)
    # df_clean = df.copy()
    # df_clean["ScrapReasonID"] = df_clean["ScrapReasonID"].fillna(0)
    # print("Filled ScrapReasonID nulls with 0")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_productinventory(file_path, output_path=None):
    """Clean nulls in Production ProductInventory table"""
    df = pd.read_excel(file_path, sheet_name="Production ProductInventory")
    print(f"Production ProductInventory: {len(df)} rows")
    
    # Shelf has 290 nulls out of 1,069 rows (27.1%)
    # This is a significant number but not the majority
    
    # Analyze the pattern of nulls
    null_pattern = df[df["Shelf"].isnull()]
    print(f"Shelf nulls: {len(null_pattern)} out of {len(df)} rows")
    
    # Check if nulls are associated with particular locations
    if "LocationID" in df.columns:
        location_counts = null_pattern["LocationID"].value_counts()
        print("Nulls by LocationID:")
        print(location_counts)
    
    # Option 1: Fill with a placeholder indicating "No Shelf Assigned"
    df_clean = df.copy()
    df_clean["Shelf"] = df_clean["Shelf"].fillna("NONE")
    print("Filled Shelf nulls with 'NONE'")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_product(file_path, output_path=None):
    """Clean nulls in Production Product table"""
    df = pd.read_excel(file_path, sheet_name="Production Product")
    print(f"Production Product: {len(df)} rows")
    
    # Multiple columns have nulls, analyze each
    null_counts = df.isnull().sum()
    print("Null counts per column:")
    for col in null_counts[null_counts > 0].index:
        print(f"  {col}: {null_counts[col]} nulls ({null_counts[col]/len(df)*100:.1f}%)")
    
    df_clean = df.copy()
    
    # Handle optional descriptive fields (Color, Size, etc.)
    # These are likely not applicable for all products
    for col in ["Color", "Size", "SizeUnitMeasureCode", "WeightUnitMeasureCode", 
                "ProductLine", "Class", "Style"]:
        if col in df.columns and null_counts.get(col, 0) > 0:
            # Keep nulls for these fields as they are legitimately N/A for some products
            print(f"Keeping nulls in {col} as they represent 'Not Applicable'")
    
    # Handle Weight - fill with 0 for products with no weight
    if "Weight" in df.columns and null_counts.get("Weight", 0) > 0:
        df_clean["Weight"] = df_clean["Weight"].fillna(0)
        print("Filled Weight nulls with 0")
    
    # Handle category IDs - use -1 to indicate uncategorized
    for col in ["ProductSubcategoryID", "ProductModelID"]:
        if col in df.columns and null_counts.get(col, 0) > 0:
            df_clean[col] = df_clean[col].fillna(-1)
            print(f"Filled {col} nulls with -1 (uncategorized)")
    
    # SellEndDate nulls indicate products still being sold
    if "SellEndDate" in df.columns and null_counts.get("SellEndDate", 0) > 0:
        print("Keeping SellEndDate nulls as they indicate 'Still selling'")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_salesorderheader(file_path, output_path=None):
    """Clean nulls in Sales SalesOrderHeader table"""
    df = pd.read_excel(file_path, sheet_name="Sales SalesOrderHeader")
    print(f"Sales SalesOrderHeader: {len(df)} rows")
    
    # Multiple columns have nulls
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].index.tolist()
    
    print("Null counts per column:")
    for col in cols_with_nulls:
        percent = null_counts[col]/len(df)*100
        print(f"  {col}: {null_counts[col]} nulls ({percent:.1f}%)")
    
    df_clean = df.copy()
    
    # PurchaseOrderNumber - Null for 27,659 out of 31,465 rows (87.9%)
    # This field is likely only used for certain types of orders
    if "PurchaseOrderNumber" in cols_with_nulls:
        # Leave as null since it's a legitimate business case
        print("Keeping PurchaseOrderNumber nulls as they represent orders without POs")
    
    # SalesPersonID - Null for 27,659 rows (87.9%)
    # These are likely online orders without a specific salesperson
    if "SalesPersonID" in cols_with_nulls:
        df_clean["SalesPersonID"] = df_clean["SalesPersonID"].fillna(-1)
        print("Filled SalesPersonID nulls with -1 (no salesperson)")
    
    # CreditCardID and CreditCardApprovalCode - Null for 1,131 rows (3.6%)
    # These likely represent orders not paid by credit card
    if "CreditCardID" in cols_with_nulls:
        df_clean["CreditCardID"] = df_clean["CreditCardID"].fillna(-1)
        print("Filled CreditCardID nulls with -1 (no credit card)")
    
    if "CreditCardApprovalCode" in cols_with_nulls:
        # Keep as null or use a specific code
        print("Keeping CreditCardApprovalCode nulls as they represent non-credit card transactions")
    
    # CurrencyRateID - Null for 17,489 rows (55.6%)
    # Likely represents transactions in the default currency
    if "CurrencyRateID" in cols_with_nulls:
        df_clean["CurrencyRateID"] = df_clean["CurrencyRateID"].fillna(-1)
        print("Filled CurrencyRateID nulls with -1 (default currency)")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_salesorderdetail(file_path, output_path=None):
    """Clean nulls in Sales SalesOrderDetail table"""
    df = pd.read_excel(file_path, sheet_name="Sales SalesOrderDetail")
    print(f"Sales SalesOrderDetail: {len(df)} rows")
    
    # CarrierTrackingNumber - 60,398 nulls out of 121,317 rows (49.8%)
    # This is likely legitimately missing for items not yet shipped
    
    df_clean = df.copy()
    
    # Option 1: Fill with a placeholder indicating "Not Yet Shipped"
    df_clean["CarrierTrackingNumber"] = df_clean["CarrierTrackingNumber"].fillna("PENDING")
    print("Filled CarrierTrackingNumber nulls with 'PENDING'")
    
    # Option 2: Keep nulls (if you want to distinguish between shipped and unshipped)
    # print("Keeping CarrierTrackingNumber nulls to distinguish shipped vs unshipped items")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_address(file_path, output_path=None):
    """Clean nulls in Person Address table"""
    df = pd.read_excel(file_path, sheet_name="Person Address")
    print(f"Person Address: {len(df)} rows")
    
    # AddressLine2 - 19,252 nulls out of 19,614 rows (98.2%)
    # This field is clearly optional and rarely used
    
    df_clean = df.copy()
    
    # Since almost all rows have null AddressLine2, we have two main options:
    
    # Option 1: Keep the nulls (recommended since it's standard for addresses)
    print("Keeping AddressLine2 nulls as this is a standard optional address field")
    
    # Option 2: Drop the column entirely since it's rarely used
    # df_clean = df_clean.drop(columns=["AddressLine2"])
    # print("Dropped AddressLine2 column as it's rarely used (98.2% null)")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_person(file_path, output_path=None):
    """Clean nulls in Person Person table"""
    df = pd.read_excel(file_path, sheet_name="Person Person")
    print(f"Person Person: {len(df)} rows")
    
    # Title - 18,963 nulls out of 19,972 rows (94.9%)
    # MiddleName - 8,499 nulls out of 19,972 rows (42.6%)
    # These are standard optional name fields
    
    df_clean = df.copy()
    
    # Keep nulls for these name fields as they're legitimately missing
    print("Keeping Title and MiddleName nulls as they're standard optional name fields")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_billofmaterials(file_path, output_path=None):
    """Clean nulls in Production BillOfMaterials table"""
    df = pd.read_excel(file_path, sheet_name="Production BillOfMaterials")
    print(f"Production BillOfMaterials: {len(df)} rows")
    
    # ProductAssemblyID - 103 nulls out of 2,679 rows (3.8%)
    # EndDate - 2,480 nulls out of 2,679 rows (92.6%)
    
    df_clean = df.copy()
    
    # ProductAssemblyID is null for top-level components (not part of an assembly)
    # Fill with -1 to indicate this special case
    df_clean["ProductAssemblyID"] = df_clean["ProductAssemblyID"].fillna(-1)
    print("Filled ProductAssemblyID nulls with -1 (top-level components)")
    
    # EndDate null means the BOM is still active
    print("Keeping EndDate nulls as they indicate 'Still active'")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_customer(file_path, output_path=None):
    """Clean nulls in Sales Customer table"""
    df = pd.read_excel(file_path, sheet_name="Sales Customer")
    print(f"Sales Customer: {len(df)} rows")
    
    # PersonID - 701 nulls out of 19,820 rows (3.5%)
    # StoreID - 18,484 nulls out of 19,820 rows (93.3%)
    
    # This pattern indicates two types of customers:
    # 1. Store customers (have StoreID, no PersonID)
    # 2. Individual customers (have PersonID, no StoreID)
    
    df_clean = df.copy()
    
    # Add a CustomerType column for clarity
    df_clean["CustomerType"] = "Unknown"
    df_clean.loc[df_clean["StoreID"].notnull(), "CustomerType"] = "Store"
    df_clean.loc[df_clean["PersonID"].notnull(), "CustomerType"] = "Individual"
    
    print("Added CustomerType column instead of filling nulls")
    print("Keep both PersonID and StoreID nulls as they indicate customer type")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_salesperson(file_path, output_path=None):
    """Clean nulls in Sales SalesPerson table"""
    df = pd.read_excel(file_path, sheet_name="Sales SalesPerson")
    print(f"Sales SalesPerson: {len(df)} rows")
    
    # TerritoryID - 3 nulls out of 17 rows (17.6%)
    # SalesQuota - 3 nulls out of 17 rows (17.6%)
    
    df_clean = df.copy()
    
    # TerritoryID null indicates a salesperson not assigned to a territory
    df_clean["TerritoryID"] = df_clean["TerritoryID"].fillna(-1)
    print("Filled TerritoryID nulls with -1 (unassigned)")
    
    # SalesQuota null indicates no quota assigned
    df_clean["SalesQuota"] = df_clean["SalesQuota"].fillna(0)
    print("Filled SalesQuota nulls with 0 (no quota)")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_vendor(file_path, output_path=None):
    """Clean nulls in Purchasing Vendor table"""
    df = pd.read_excel(file_path, sheet_name="Purchasing Vendor")
    print(f"Purchasing Vendor: {len(df)} rows")
    
    # PurchasingWebServiceURL - 98 nulls out of 104 rows (94.2%)
    # Most vendors don't have a web service URL
    
    df_clean = df.copy()
    
    # Option 1: Keep nulls (recommended since it's clearly optional)
    print("Keeping PurchasingWebServiceURL nulls as this is an optional field")
    
    # Option 2: Drop the column since it's rarely used
    # df_clean = df_clean.drop(columns=["PurchasingWebServiceURL"])
    # print("Dropped PurchasingWebServiceURL column as it's rarely used (94.2% null)")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_employee(file_path, output_path=None):
    """Clean nulls in HumanResources Employee table"""
    df = pd.read_excel(file_path, sheet_name="HumanResources Employee")
    print(f"HumanResources Employee: {len(df)} rows")
    
    # OrganizationNode - 1 null out of 290 rows (0.3%)
    # OrganizationLevel - 1 null out of 290 rows (0.3%)
    
    # This likely represents the CEO or top executive with no superior
    df_clean = df.copy()
    
    # Find the record with null OrganizationNode
    null_record = df[df["OrganizationNode"].isnull()]
    if not null_record.empty:
        job_title = null_record["JobTitle"].values[0] if "JobTitle" in df.columns else "Unknown"
        print(f"Found null OrganizationNode for: {job_title}")
        print("Keeping null as it likely represents the top of organization")
    
    # Keep nulls as they have hierarchical meaning
    print("Keeping OrganizationNode and OrganizationLevel nulls as they indicate top of hierarchy")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_vstorewithaddresses(file_path, output_path=None):
    """Clean nulls in Sales vStoreWithAddresses view"""
    df = pd.read_excel(file_path, sheet_name="Sales vStoreWithAddresses")
    print(f"Sales vStoreWithAddresses: {len(df)} rows")
    
    # AddressLine2 - 679 nulls out of 712 rows (95.4%)
    # This is a standard optional address field
    
    df_clean = df.copy()
    
    # Keep nulls as this is a standard optional field
    print("Keeping AddressLine2 nulls as this is a standard optional address field")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_vsalesperson(file_path, output_path=None):
    """Clean nulls in Sales vSalesPerson view"""
    df = pd.read_excel(file_path, sheet_name="Sales vSalesPerson")
    print(f"Sales vSalesPerson: {len(df)} rows")
    
    # Multiple columns have nulls
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].index.tolist()
    
    print("Null counts per column:")
    for col in cols_with_nulls:
        percent = null_counts[col]/len(df)*100
        print(f"  {col}: {null_counts[col]} nulls ({percent:.1f}%)")
    
    df_clean = df.copy()
    
    # Optional name fields (Title, MiddleName, Suffix)
    for col in ["Title", "MiddleName", "Suffix"]:
        if col in cols_with_nulls:
            print(f"Keeping {col} nulls as these are optional name fields")
    
    # Optional address fields
    if "AddressLine2" in cols_with_nulls:
        print("Keeping AddressLine2 nulls as this is an optional address field")
    
    # Territory fields (TerritoryName, TerritoryGroup)
    for col in ["TerritoryName", "TerritoryGroup"]:
        if col in cols_with_nulls:
            # Better to keep as null to indicate no territory assignment
            print(f"Keeping {col} nulls as they indicate salespeople without territory")
    
    # SalesQuota
    if "SalesQuota" in cols_with_nulls:
        df_clean["SalesQuota"] = df_clean["SalesQuota"].fillna(0)
        print("Filled SalesQuota nulls with 0")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

def clean_vindividualcustomer(file_path, output_path=None):
    """Clean nulls in Sales vIndividualCustomer view"""
    df = pd.read_excel(file_path, sheet_name="Sales vIndividualCustomer")
    print(f"Sales vIndividualCustomer: {len(df)} rows")
    
    # Multiple columns have nulls
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].index.tolist()
    
    print("Null counts per column:")
    for col in cols_with_nulls:
        percent = null_counts[col]/len(df)*100
        print(f"  {col}: {null_counts[col]} nulls ({percent:.1f}%)")
    
    df_clean = df.copy()
    
    # Optional name fields (Title, MiddleName, Suffix)
    for col in ["Title", "MiddleName", "Suffix"]:
        if col in cols_with_nulls:
            print(f"Keeping {col} nulls as these are optional name fields")
    
    # Optional address fields
    if "AddressLine2" in cols_with_nulls:
        print("Keeping AddressLine2 nulls as this is an optional address field")
    
    if output_path:
        df_clean.to_excel(output_path, index=False)
        print(f"Saved to {output_path}")
    
    return df_clean

# =============================================================================
# Main Processing Functions
# =============================================================================

def process_adventure_works_nulls(file_path, output_dir=None):
    """Process all AdventureWorks tables with nulls using specialized handlers"""
    # Set default output directory if none provided
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = os.path.join(output_dir, f"AdventureWorks_Clean_{timestamp}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Define tables with nulls and their handlers
    null_tables = {
        "Production WorkOrder": clean_workorder,
        "Production ProductInventory": clean_productinventory,
        "Production Product": clean_product,
        "Sales SalesOrderHeader": clean_salesorderheader,
        "Sales SalesOrderDetail": clean_salesorderdetail,
        "Person Address": clean_address,
        "Person Person": clean_person,
        "Production BillOfMaterials": clean_billofmaterials,
        "Sales Customer": clean_customer,
        "Sales SalesPerson": clean_salesperson,
        "Purchasing Vendor": clean_vendor,
        "HumanResources Employee": clean_employee,
        "Sales vStoreWithAddresses": clean_vstorewithaddresses,
        "Sales vSalesPerson": clean_vsalesperson,
        "Sales vIndividualCustomer": clean_vindividualcustomer
    }
    
    # Process each table
    print(f"Processing {len(null_tables)} tables with nulls")
    
    for table_name, handler_func in null_tables.items():
        print(f"\n{'='*50}")
        print(f"Processing: {table_name}")
        print(f"{'='*50}")
        
        output_file = os.path.join(output_dir, f"{table_name.replace(' ', '_')}_clean.xlsx")
        
        try:
            handler_func(file_path, output_file)
        except Exception as e:
            print(f"Error processing {table_name}: {str(e)}")
    
    print(f"\nAll tables processed. Clean files saved to: {output_dir}")

def process_selected_tables(file_path):
    """Process only selected AdventureWorks tables with nulls"""
    # Define tables with nulls and their handlers
    null_tables = {
        "1. Production WorkOrder": clean_workorder,
        "2. Production ProductInventory": clean_productinventory,
        "3. Production Product": clean_product,
        "4. Sales SalesOrderHeader": clean_salesorderheader,
        "5. Sales SalesOrderDetail": clean_salesorderdetail,
        "6. Person Address": clean_address,
        "7. Person Person": clean_person,
        "8. Production BillOfMaterials": clean_billofmaterials,
        "9. Sales Customer": clean_customer,
        "10. Sales SalesPerson": clean_salesperson,
        "11. Purchasing Vendor": clean_vendor,
        "12. HumanResources Employee": clean_employee,
        "13. Sales vStoreWithAddresses": clean_vstorewithaddresses,
        "14. Sales vSalesPerson": clean_vsalesperson,
        "15. Sales vIndividualCustomer": clean_vindividualcustomer
    }
    
    # Show available tables
    print("\nTables with nulls that can be processed:")
    for table_name in null_tables.keys():
        print(table_name)
    
    # Get user selection
    selection = input("\nEnter table numbers to process (comma separated, e.g., 1,3,5) or 'all': ")
    
    # Create output directory
    output_dir = os.path.dirname(file_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = os.path.join(output_dir, f"AdventureWorks_Selected_{timestamp}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process selected tables
    if selection.lower() == 'all':
        selected_tables = list(null_tables.keys())
    else:
        selected_indices = [int(idx.strip()) for idx in selection.split(',')]
        selected_tables = [list(null_tables.keys())[idx-1] for idx in selected_indices 
                         if 1 <= idx <= len(null_tables)]
    
    print(f"\nProcessing {len(selected_tables)} selected tables")
    
    for table_name in selected_tables:
        print(f"\n{'='*50}")
        print(f"Processing: {table_name}")
        print(f"{'='*50}")
        
        # Extract actual table name (remove numbering)
        actual_table = ' '.join(table_name.split('. ')[1:]) if '. ' in table_name else table_name
        output_file = os.path.join(output_dir, f"{actual_table.replace(' ', '_')}_clean.xlsx")
        
        try:
            null_tables[table_name](file_path, output_file)
        except Exception as e:
            print(f"Error processing {table_name}: {str(e)}")
    
    print(f"\nSelected tables processed. Clean files saved to: {output_dir}")

def process_single_table(file_path, table_name):
    """Process a single AdventureWorks table"""
    # Map of table names to handler functions
    handlers = {
        "Production WorkOrder": clean_workorder,
        "Production ProductInventory": clean_productinventory,
        "Production Product": clean_product,
        "Sales SalesOrderHeader": clean_salesorderheader,
        "Sales SalesOrderDetail": clean_salesorderdetail,
        "Person Address": clean_address,
        "Person Person": clean_person,
        "Production BillOfMaterials": clean_billofmaterials,
        "Sales Customer": clean_customer,
        "Sales SalesPerson": clean_salesperson,
        "Purchasing Vendor": clean_vendor,
        "HumanResources Employee": clean_employee,
        "Sales vStoreWithAddresses": clean_vstorewithaddresses,
        "Sales vSalesPerson": clean_vsalesperson,
        "Sales vIndividualCustomer": clean_vindividualcustomer
    }
    
    # Check if the table is supported
    if table_name not in handlers:
        print(f"Error: Table '{table_name}' is not supported.")
        print("Supported tables:")
        for t in handlers.keys():
            print(f"  {t}")
        return
    
    # Create output path
    output_dir = os.path.dirname(file_path)
    output_file = os.path.join(output_dir, f"{table_name.replace(' ', '_')}_clean.xlsx")
    
    # Process the table
    print(f"Processing table: {table_name}")
    try:
        handlers[table_name](file_path, output_file)
        print(f"Table processed successfully. Output saved to: {output_file}")
    except Exception as e:
        print(f"Error processing table: {str(e)}")

# =============================================================================
# Main Menu and Program Entry
# =============================================================================

def show_main_menu():
    """Display the main menu for the application"""
    print("\n" + "="*50)
    print("ADVENTURE WORKS NULL HANDLER")
    print("="*50)
    print("1. Process all tables with nulls")
    print("2. Process selected tables")
    print("3. Process a single table")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    return choice

# Main program
if __name__ == "__main__":
    print("Welcome to the AdventureWorks Null Handler!")
    
    # Get the file path first
    file_path = input("Enter the path to your Excel file (e.g., D:/finaaaaalllllll  project.xlsx): ")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        print("Please check the path and try again.")
        input("Press Enter to exit...")
        exit()
    
    # Show menu and process choice
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            process_adventure_works_nulls(file_path)
        elif choice == '2':
            process_selected_tables(file_path)
        elif choice == '3':
            # Show available tables
            handlers = {
                "Production WorkOrder": clean_workorder,
                "Production ProductInventory": clean_productinventory,
                "Production Product": clean_product,
                "Sales SalesOrderHeader": clean_salesorderheader,
                "Sales SalesOrderDetail": clean_salesorderdetail,
                "Person Address": clean_address,
                "Person Person": clean_person,
                "Production BillOfMaterials": clean_billofmaterials,
                "Sales Customer": clean_customer,
                "Sales SalesPerson": clean_salesperson,
                "Purchasing Vendor": clean_vendor,
                "HumanResources Employee": clean_employee,
                "Sales vStoreWithAddresses": clean_vstorewithaddresses,
                "Sales vSalesPerson": clean_vsalesperson,
                "Sales vIndividualCustomer": clean_vindividualcustomer
            }
            
            print("\nAvailable tables:")
            for i, table in enumerate(handlers.keys(), 1):
                print(f"{i}. {table}")
            
            table_choice = input("\nEnter table number: ")
            try:
                table_idx = int(table_choice) - 1
                if 0 <= table_idx < len(handlers):
                    table_name = list(handlers.keys())[table_idx]
                    process_single_table(file_path, table_name)
                else:
                    print("Invalid table number.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == '4':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")