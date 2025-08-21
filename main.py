import waifu
import asyncio

async def main():
    await waifu.start_pipeline()
    
if __name__ == "__main__":
    asyncio.run(main())