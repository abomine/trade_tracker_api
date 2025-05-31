from datetime import datetime, timedelta
from tradetracker_api import TradeTrackerAPI

tt = TradeTrackerAPI(
    #Change these to your credentials 
    customer_id="amine_abouhodaifa",
    passphrase="not_my_password_:D",
    sandbox=True
)

if tt.authenticate():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Authentication successful - proceeding with data retrieval")
    
    campaigns = tt.get_campaigns()
    print(f"Found {len(campaigns)} campaigns")
    
    if campaigns:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        clicks = tt.get_transactions(
            transaction_type='click',
            start_date=start_date,
            end_date=end_date,
            limit=5
        )
        print(f"Found {len(clicks)} click transactions")
        
        conversions = tt.get_transactions(
            transaction_type='conversion',
            start_date=start_date,
            end_date=end_date,
            limit=5
        )
        print(f"Found {len(conversions)} conversion transactions")
else:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Critical error - authentication failed")
    print("Unable to proceed without valid API access")