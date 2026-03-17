"""
Test market data API with new assets (Silver, Bitcoin, Ethereum)
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.endpoints.market_data import get_oil_gold_prices

load_dotenv()

async def main():
    print("=" * 80)
    print("Testing Market Data API - Oil, Gold, Silver, Bitcoin, Ethereum")
    print("=" * 80)
    
    try:
        result = await get_oil_gold_prices()
        
        print("\n✅ API Response Received Successfully!\n")
        
        # Display each asset
        assets = ["gold", "oil", "silver", "bitcoin", "ethereum", "solana", "lebanese_lira"]
        
        for asset in assets:
            if asset in result:
                data = result[asset]
                print(f"\n{asset.upper()}")
                print("-" * 40)
                print(f"  Symbol: {data['symbol']}")
                print(f"  Unit: {data['unit']}")
                print(f"  Current Price: {data['current']['price']}")
                print(f"  Date: {data['current']['date']}")
                print(f"  7-Day Change: {data['change_7d']}%")
                print(f"  Trend Points: {len(data['trend'])} data points")
        
        # Display analysis
        print(f"\n{'=' * 80}")
        print("ANALYSIS")
        print("=" * 80)
        print(f"\nEnglish:\n{result['analysis']['en']}")
        print(f"\nArabic:\n{result['analysis']['ar']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
