import subprocess
import sys
import os

# Run the crawler script
def run_menu_crawler():
    script_path = os.path.join(os.path.dirname(__file__), 'menu_crawler.py')
    subprocess.run([sys.executable, script_path])

def main():
    # Run the crawler
    run_menu_crawler()
    print("Crawling completed. Starting OCR...")
    
if __name__ == "__main__":
    main()
