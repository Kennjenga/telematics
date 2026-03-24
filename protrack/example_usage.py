"""
Example script demonstrating how to fetch and store vehicle mileage data
from Protrack API with accurate timestamps.
"""

from main import get_access_token, fetch_and_store_vehicle_mileage
from fetch_mileage import fetch_multiple_vehicles_mileage, save_mileage_data_to_json


def example_single_vehicle():
    """
    Example: Fetch mileage data for a single vehicle.
    """
    print("=" * 70)
    print("Example 1: Fetching mileage for a single vehicle")
    print("=" * 70)
    
    # Step 1: Get access token
    account: str = os.getenv("PROTRACK_ACCOUNT", "")
    password: str = os.getenv("PROTRACK_PASSWORD", "")
    access_token: str = get_access_token(account, password)
    
    if not access_token:
        print("Failed to get access token. Exiting.")
        return
    
    # Step 2: Fetch mileage data with accurate timestamps
    imei: str = "355710090499992"
    start_date: str = "2024-01-15"
    end_date: str = "2024-01-16"
    
    try:
        mileage_data = fetch_and_store_vehicle_mileage(
            access_token=access_token,
            imeis=imei,
            start_date=start_date,
            end_date=end_date,
            output_file="mileage_single_vehicle.json"
        )
        
        # Display results
        if mileage_data:
            print("\n✓ Successfully fetched mileage data:")
            for data in mileage_data:
                print(f"  - IMEI: {data.imei}, Mileage: {data.mileage} km")
        else:
            print("\n⚠ No mileage data found for the specified period.")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def example_multiple_vehicles():
    """
    Example: Fetch mileage data for multiple vehicles.
    """
    print("\n" + "=" * 70)
    print("Example 2: Fetching mileage for multiple vehicles")
    print("=" * 70)
    
    # Step 1: Get access token
    account: str = os.getenv("PROTRACK_ACCOUNT", "")
    password: str = os.getenv("PROTRACK_PASSWORD", "")
    access_token: str = get_access_token(account, password)
    
    if not access_token:
        print("Failed to get access token. Exiting.")
        return
    
    # Step 2: Define list of vehicles (IMEIs)
    imeis_list: list[str] = [
        "355710090499992",
        # Add more IMEIs here as needed
    ]
    
    # Step 3: Fetch mileage data for all vehicles
    start_date: str = "2024-01-15"
    end_date: str = "2024-01-16"
    
    try:
        results = fetch_multiple_vehicles_mileage(
            access_token=access_token,
            imeis_list=imeis_list,
            start_date=start_date,
            end_date=end_date,
            verbose=True
        )
        
        # Display summary
        print("\n" + "=" * 70)
        print("Summary:")
        print("=" * 70)
        for imei, mileage_data_list in results.items():
            if mileage_data_list:
                print(f"IMEI {imei}: {len(mileage_data_list)} record(s) found")
                for data in mileage_data_list:
                    print(f"  - Mileage: {data.mileage} km")
            else:
                print(f"IMEI {imei}: No data found")
        
        # Save all data to a single file
        all_data = []
        for mileage_data_list in results.values():
            all_data.extend(mileage_data_list)
        
        if all_data:
            save_mileage_data_to_json(all_data, "mileage_all_vehicles.json")
            print(f"\n✓ Saved {len(all_data)} total record(s) to mileage_all_vehicles.json")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


def example_custom_date_range():
    """
    Example: Fetch mileage data with custom date range and format.
    """
    print("\n" + "=" * 70)
    print("Example 3: Custom date range with specific format")
    print("=" * 70)
    
    # Step 1: Get access token
    account: str = os.getenv("PROTRACK_ACCOUNT", "")
    password: str = os.getenv("PROTRACK_PASSWORD", "")
    access_token: str = get_access_token(account, password)
    
    if not access_token:
        print("Failed to get access token. Exiting.")
        return
    
    # Step 2: Use custom date format
    imei: str = "355710090499992"
    start_date: str = "15/01/2024 08:00:00"  # DD/MM/YYYY format
    end_date: str = "16/01/2024 18:30:00"
    
    try:
        mileage_data = fetch_and_store_vehicle_mileage(
            access_token=access_token,
            imeis=imei,
            start_date=start_date,
            end_date=end_date,
            start_date_format="%d/%m/%Y %H:%M:%S",
            end_date_format="%d/%m/%Y %H:%M:%S",
            output_file="mileage_custom_range.json"
        )
        
        if mileage_data:
            print("\n✓ Successfully fetched mileage data with custom date format")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    """
    Run examples to demonstrate accurate mileage data fetching.
    Uncomment the example you want to run.
    """
    
    # Example 1: Single vehicle
    example_single_vehicle()
    
    # Example 2: Multiple vehicles (uncomment to use)
    # example_multiple_vehicles()
    
    # Example 3: Custom date format (uncomment to use)
    # example_custom_date_range()


