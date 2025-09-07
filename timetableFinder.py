from playwright.sync_api import sync_playwright
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def setup_stealth_page(page):
    # Remove webdriver property
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    """)
    
    # Override the plugins property
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    """)
    
    # Override the languages property
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """)
    
    # Override chrome property
    page.add_init_script("""
        window.chrome = {
            runtime: {},
        };
    """)
    
    # Override permissions
    page.add_init_script("""
        const originalQuery = window.navigator.permissions.query;
        return window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)

def get_timetable(username=None, password=None, headless=False, output_filename="weekly_schedule_timetable", start_date=None):
    """
    Get timetable data from the SIT portal.
    
    Args:
        username (str, optional): Login username. If None, uses default USERNAME.
        password (str, optional): Login password. If None, uses default PASSWORD.
        headless (bool): Whether to run browser in headless mode. Default is False.
        output_filename (str): Base filename for output files (without extension).
    
    Returns:
        pandas.DataFrame: The extracted timetable data, or None if extraction failed.
    """
    # Use provided credentials or fall back to defaults
    login_username = username or USERNAME
    login_password = password or PASSWORD
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        page = context.new_page()
        setup_stealth_page(page)
        
        # Simulate human-like behavior
        time.sleep(random.uniform(1, 3))
        
        try:
            # Navigate with realistic timing
            response = page.goto(
                "https://in4sit.singaporetech.edu.sg/CSSISSTD/signon.html",
                wait_until='domcontentloaded'
            )
            
            # Wait and check for Incapsula
            time.sleep(random.uniform(3, 7))
            
            # Look for Incapsula indicators
            incapsula_detected = page.evaluate("""
                () => {
                    const content = document.body.innerText.toLowerCase();
                    return content.includes('incapsula') || 
                           content.includes('access denied') ||
                           content.includes('blocked') ||
                           document.querySelector('[data-cy="challenge"]') !== null;
                }
            """)
            
            if incapsula_detected:
                print("Incapsula challenge detected, waiting...")
                # Wait for challenge to resolve
                page.wait_for_function(
                    "() => !document.body.innerText.toLowerCase().includes('incapsula')",
                    timeout=60000
                )
            
            # Continue with normal flow
            page.wait_for_load_state('networkidle')
            print(f"Successfully accessed: {page.url}")
            
            # Fill in login credentials
            print("Looking for login form elements...")
            
            # Wait for login form to be available
            page.wait_for_selector('#userNameInput', timeout=10000)
            
            # Locate username input field
            username_input = page.locator('#userNameInput')
            if username_input.is_visible():
                print("Found username input field")
                # Clear any existing text and fill with preset username
                username_input.clear()
                time.sleep(random.uniform(0.5, 1.5))  # Human-like delay
                username_input.fill(login_username)
                print(f"Filled username: {login_username}")
            else:
                print("Username input field not visible")
            
            # Locate password input field
            password_input = page.locator('#passwordInput')
            if password_input.is_visible():
                print("Found password input field")
                # Clear any existing text and fill with preset password
                password_input.clear()
                time.sleep(random.uniform(0.5, 1.5))  # Human-like delay
                password_input.fill(login_password)
                print("Filled password (hidden for security)")
            else:
                print("Password input field not visible")
            
            # Click the specific submit button (span element with id "submitButton")
            print("Looking for submit button...")
            
            # Wait for the submit button to be available
            page.wait_for_selector('#submitButton', timeout=10000)
            
            submit_button = page.locator('#submitButton')
            if submit_button.is_visible():
                print("Found submit button (span#submitButton)")
                
                # Wait for navigation after clicking submit
                with page.expect_navigation(wait_until='networkidle', timeout=30000):
                    submit_button.click()
                    print("Clicked submit button, waiting for redirect...")
            else:
                print("Submit button not visible")
                # Fallback: try pressing Enter on password field
                password_input.press('Enter')
                page.wait_for_load_state('networkidle', timeout=30000)
            
            # Wait for redirect to complete
            time.sleep(random.uniform(2, 5))
            
            print(f"After login redirect: {page.url}")
            
            # STEP 1: Click the first div element
            print("STEP 1: Looking for first div element (win0divPTNUI_LAND_REC_GROUPLET$1)...")
            
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(2)
                
                first_div_selector = '#win0divPTNUI_LAND_REC_GROUPLET\\$1'
                page.wait_for_selector(first_div_selector, timeout=15000)
                
                first_div = page.locator(first_div_selector)
                if first_div.is_visible():
                    print("Found first div element (win0divPTNUI_LAND_REC_GROUPLET$1)")
                    time.sleep(random.uniform(1, 2))
                    first_div.click()
                    print("Clicked first div element")
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(random.uniform(2, 3))
                else:
                    print("First div element not visible")
                    # page.screenshot(path=os.path.join(SCRIPT_DIR, "step1_div_not_found.png"))
                    
            except Exception as step1_error:
                print(f"Error in STEP 1: {step1_error}")
                # page.screenshot(path=os.path.join(SCRIPT_DIR, "step1_error.png"))
            
            # STEP 2: Click the second div element
            print("STEP 2: Looking for second div element (win2div$ICField$11$$1)...")
            
            try:
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(2)
                
                # Use CSS selector that matches both win1div and win2div variations
                second_div_selector = '[id*="div\\$ICField\\$11\\$\\$1"]'
                page.wait_for_selector(second_div_selector, timeout=15000)
                
                second_div = page.locator(second_div_selector)
                if second_div.is_visible():
                    # Get the actual ID for logging
                    actual_id = second_div.get_attribute('id')
                    print(f"Found second div element ({actual_id})")
                    time.sleep(random.uniform(1, 2))
                    second_div.click()
                    print("Clicked second div element")
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(random.uniform(2, 3))
                else:
                    print("Second div element not visible")
                    page.screenshot(path=os.path.join(SCRIPT_DIR, "step2_div_not_found.png"))
                    
            except Exception as step2_error:
                print(f"Error in STEP 2: {step2_error}")
                page.screenshot(path=os.path.join(SCRIPT_DIR, "step2_error.png"))
            
            # TABLE EXTRACTION: Navigate to iframe and extract specific table
            print("TABLE EXTRACTION: Navigating to iframe content and looking for WEEKLY_SCHED_HTMLAREA table...")
            
            try:
                # Wait for the page to fully load
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(3)
                
                # Check if iframe exists and get its source URL
                iframe_selector = '#main_target_win0'
                iframe_exists = page.locator(iframe_selector).count() > 0
                
                if iframe_exists:
                    iframe_src = page.locator(iframe_selector).get_attribute('src')
                    print(f"Found iframe with source: {iframe_src}")
                    
                    # Navigate to the iframe source URL
                    print("Navigating to iframe source...")
                    page.goto(iframe_src, wait_until='networkidle', timeout=30000)
                    time.sleep(3)
                    
                    # Take screenshot after navigation
                    page.screenshot(path=os.path.join(SCRIPT_DIR, "iframe_content.png"))
                    print("Screenshot of iframe content saved as iframe_content.png")
                    
                else:
                    print("Iframe not found, searching for table on current page...")
                
                # Click the first element with ID DERIVED_CLASS_S_SSR_DISP_TITLE_LBL
                try:
                    print("Clicking element with ID DERIVED_CLASS_S_SSR_DISP_TITLE_LBL...")
                    title_element_selector = '#DERIVED_CLASS_S_SSR_DISP_TITLE_LBL'
                    
                    # Wait for the element to be available
                    page.wait_for_selector(title_element_selector, timeout=10000)
                    
                    title_element = page.locator(title_element_selector)
                    if title_element.is_visible():
                        title_element.click()
                        print("Successfully clicked DERIVED_CLASS_S_SSR_DISP_TITLE_LBL element")
                        
                        # Wait a moment for any potential page changes
                        time.sleep(random.uniform(1, 2))
                        page.wait_for_load_state('networkidle', timeout=5000)
                    else:
                        print("DERIVED_CLASS_S_SSR_DISP_TITLE_LBL element not visible")
                        
                except Exception as click_error:
                    print(f"Error clicking DERIVED_CLASS_S_SSR_DISP_TITLE_LBL: {click_error}")
                    # Continue with next click even if this fails
                
                # start_date = datetime.date(2025, 8, 29)
                next_working_day_str = (start_date + datetime.timedelta(days=3 if start_date.weekday() == 4 else (2 if start_date.weekday() == 5 else (1 if start_date.weekday() == 6 else 1)))).strftime("%d/%m/%Y")
                
                try:
                    print("Clicking element with ID DERIVED_CLASS_S_START_DT...")
                    title_element_selector = '#DERIVED_CLASS_S_START_DT'
                    
                    # Wait for the element to be available
                    page.wait_for_selector(title_element_selector, timeout=10000)
                    startdate_input = page.locator('#DERIVED_CLASS_S_START_DT')
                    if startdate_input.is_visible():
                        print("Found startdate input field")
                        # Clear any existing text and fill with preset username
                        startdate_input.clear()
                        time.sleep(random.uniform(0.5, 1.5))  # Human-like delay
                        startdate_input.fill(next_working_day_str)
                        print(f"Filled start date: {next_working_day_str}")
                    else:
                        print("Start date input field not visible")
                except Exception as click_error:
                    print(f"Error finding DERIVED_CLASS_S_START_DT: {click_error}")
                    # Continue with next click even if this fails
                
                # Click the second element with ID DERIVED_CLASS_S_SSR_REFRESH_CAL$38$
                try:
                    print("Clicking element with ID DERIVED_CLASS_S_SSR_REFRESH_CAL$38$...")
                    refresh_element_selector = '#DERIVED_CLASS_S_SSR_REFRESH_CAL\\$38\\$'
                    
                    # Wait for the element to be available
                    page.wait_for_selector(refresh_element_selector, timeout=10000)
                    
                    refresh_element = page.locator(refresh_element_selector)
                    if refresh_element.is_visible():
                        refresh_element.click()
                        print("Successfully clicked DERIVED_CLASS_S_SSR_REFRESH_CAL$38$ element")
                        
                        # Wait a moment for any potential page changes
                        time.sleep(random.uniform(1, 2))
                        page.wait_for_load_state('networkidle', timeout=5000)
                    else:
                        print("DERIVED_CLASS_S_SSR_REFRESH_CAL$38$ element not visible")
                        
                except Exception as click_error:
                    print(f"Error clicking DERIVED_CLASS_S_SSR_REFRESH_CAL$38$: {click_error}")
                    # Continue with saving even if click fails
                    
                # Get the page HTML content (either iframe content or current page)
                html_content = page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look specifically for the table with ID WEEKLY_SCHED_HTMLAREA
                target_table = soup.find('table', id='WEEKLY_SCHED_HTMLAREA')
                
                if not target_table:
                    # Try alternative selectors
                    target_table = soup.find(id='WEEKLY_SCHED_HTMLAREA')
                    if not target_table:
                        target_table = soup.find(attrs={'id': lambda x: x and 'WEEKLY_SCHED_HTMLAREA' in x})
                
                if target_table:
                    print("Found table with ID WEEKLY_SCHED_HTMLAREA!")
                    
                    # Get table attributes for identification
                    table_id = target_table.get('id', 'No ID')
                    table_class = target_table.get('class', 'No Class')
                    if isinstance(table_class, list):
                        table_class = ' '.join(table_class)
                    
                    print(f"Table ID: {table_id}")
                    print(f"Table Class: {table_class}")
                    
                    # Custom parser to handle rowspan properly
                    def parse_table_with_rowspan(table):
                        """Parse HTML table handling rowspan attributes properly"""
                        rows_data = []
                        
                        # Get all rows
                        all_rows = table.find_all('tr')
                        
                        # Track cells that span multiple rows
                        spanning_cells = {}  # {col_index: {'content': text, 'remaining_rows': count}}
                        
                        for row_idx, row in enumerate(all_rows):
                            cells = row.find_all(['td', 'th'])
                            row_data = []
                            cell_idx = 0
                            
                            # Process each column position
                            col_pos = 0
                            while col_pos < 8:  # 8 columns total (Time + 7 days)
                                # Check if this column has a spanning cell from previous rows
                                if col_pos in spanning_cells and spanning_cells[col_pos]['remaining_rows'] > 0:
                                    # Use the spanning cell content
                                    row_data.append(spanning_cells[col_pos]['content'])
                                    spanning_cells[col_pos]['remaining_rows'] -= 1
                                    
                                    # Remove if no more rows to span
                                    if spanning_cells[col_pos]['remaining_rows'] == 0:
                                        del spanning_cells[col_pos]
                                else:
                                    # Process current cell if available
                                    if cell_idx < len(cells):
                                        cell = cells[cell_idx]
                                        
                                        # Get cell content with br tag replacement
                                        cell_html = str(cell)
                                        cell_html = cell_html.replace('<br>', '|')
                                        cell_html = cell_html.replace('<br/>', '|')
                                        cell_html = cell_html.replace('<br />', '|')
                                        cell_html = cell_html.replace('<BR>', '|')
                                        cell_html = cell_html.replace('<BR/>', '|')
                                        cell_html = cell_html.replace('<BR />', '|')
                                        
                                        modified_cell = BeautifulSoup(cell_html, 'html.parser')
                                        cell_text = modified_cell.get_text(strip=True)
                                        
                                        # Check for rowspan
                                        rowspan = int(cell.get('rowspan', 1))
                                        
                                        row_data.append(cell_text)
                                        
                                        # If cell spans multiple rows, track it
                                        if rowspan > 1:
                                            spanning_cells[col_pos] = {
                                                'content': cell_text,
                                                'remaining_rows': rowspan - 1
                                            }
                                        
                                        cell_idx += 1
                                    else:
                                        # No more cells, add empty content
                                        row_data.append('')
                                
                                col_pos += 1
                            
                            rows_data.append(row_data)
                        
                        return rows_data
                    
                    try:
                        # Use custom parser
                        parsed_rows = parse_table_with_rowspan(target_table)
                        
                        if parsed_rows:
                            # Extract headers from first row
                            headers = parsed_rows[0] if parsed_rows else []
                            data_rows = parsed_rows[1:] if len(parsed_rows) > 1 else []
                            
                            print(f"Successfully parsed table with custom parser!")
                            print(f"Headers: {headers}")
                            print(f"Number of data rows: {len(data_rows)}")
                            
                            # Create DataFrame
                            if data_rows and headers:
                                # Ensure all rows have the same number of columns as headers
                                max_cols = len(headers)
                                normalized_rows = []
                                
                                for row in data_rows:
                                    # Pad or trim row to match header length
                                    if len(row) < max_cols:
                                        row.extend([''] * (max_cols - len(row)))
                                    elif len(row) > max_cols:
                                        row = row[:max_cols]
                                    normalized_rows.append(row)
                                
                                df = pd.DataFrame(normalized_rows, columns=headers)
                                
                                # Save to CSV
                                csv_filename = os.path.join(SCRIPT_DIR, 'weekly_schedule_timetable.csv')
                                df.to_csv(csv_filename, index=False)
                                print(f"Timetable saved to {csv_filename}")
                                print(f"DataFrame shape: {df.shape}")
                                print(f"DataFrame Info:")
                                print(f"Shape: {df.shape}")
                                print(f"Columns: {list(df.columns)}")
                                
                                with open('iframe_source_debug.html', 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                
                                # Return the DataFrame when successful
                                return df
                        
                    except Exception as custom_parser_error:
                        print(f"Custom parser failed: {custom_parser_error}")
                        print("Falling back to manual parsing...")
                    
                    # Fallback to original manual parsing if custom parser fails
                    rows = []
                    headers = []
                    
                    # Get headers from thead or first tr
                    thead = target_table.find('thead')
                    if thead:
                        header_row = thead.find('tr')
                        if header_row:
                            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    else:
                        # If no thead, try to get headers from first row
                        first_row = target_table.find('tr')
                        if first_row:
                            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
                    
                    # Get data rows from tbody or all tr elements
                    tbody = target_table.find('tbody')
                    if tbody:
                        data_rows = tbody.find_all('tr')
                    else:
                        data_rows = target_table.find_all('tr')
                        # Skip first row if it contains headers
                        if headers and data_rows:
                            data_rows = data_rows[1:]
                    
                    # Extract data from each row
                    for row in data_rows:
                        cells = row.find_all(['td', 'th'])
                        row_data = []
                        for cell in cells:
                            # Get the HTML content and replace <br /> tags with |
                            cell_html = str(cell)
                            # Replace various forms of br tags with |
                            cell_html = cell_html.replace('<br>', '|')
                            cell_html = cell_html.replace('<br/>', '|')
                            cell_html = cell_html.replace('<br />', '|')
                            cell_html = cell_html.replace('<BR>', '|')
                            cell_html = cell_html.replace('<BR/>', '|')
                            cell_html = cell_html.replace('<BR />', '|')
                            
                            # Parse the modified HTML and extract text
                            modified_cell = BeautifulSoup(cell_html, 'html.parser')
                            cell_text = modified_cell.get_text(strip=True)
                            row_data.append(cell_text)
                        
                        # Add all rows to preserve timetable structure, including empty ones
                        rows.append(row_data)
                    
                    # Create DataFrame if we have data
                    if rows:
                        # Ensure all rows have the same number of columns
                        max_cols = max(len(row) for row in rows) if rows else 0
                        
                        # Create or adjust headers
                        if not headers or len(headers) < max_cols:
                            headers = [f'Column_{i+1}' for i in range(max_cols)]
                        elif len(headers) > max_cols:
                            headers = headers[:max_cols]
                        
                        # Pad rows if necessary
                        for row in rows:
                            while len(row) < max_cols:
                                row.append('')
                            # Trim if too long
                            if len(row) > max_cols:
                                row = row[:max_cols]
                        
                        # Create DataFrame
                        df = pd.DataFrame(rows, columns=headers)
                        
                        # Remove the first row
                        df = df.drop(df.index[0]).reset_index(drop=True)
                        print(f"Removed first row. DataFrame now has {len(df)} rows.")
                        
                        # Filter out Saturday and Sunday columns
                        columns_to_keep = []
                        for col in df.columns:
                            col_lower = col.lower()
                            # Keep the column if it doesn't contain 'saturday', 'sunday', 'sat', or 'sun'
                            if not any(day in col_lower for day in ['saturday', 'sunday', 'sat|', 'sun|']):
                                columns_to_keep.append(col)
                            else:
                                print(f"Filtering out weekend column: {col}")
                        
                        # Keep only weekday columns
                        df = df[columns_to_keep]
                        print(f"After filtering weekends, DataFrame shape: {df.shape}")
                        
                        # Save to CSV
                        df.to_csv(os.path.join(SCRIPT_DIR, 'weekly_schedule_timetable.csv'), index=False)
                        print(f"Weekly schedule table saved to weekly_schedule_timetable.csv with shape: {df.shape}")
                        
                        # Show the complete DataFrame
                        print("\nComplete Weekly Schedule Data (Weekdays Only):")
                        print(df.to_string(index=False))
                        
                        # Show basic info about the DataFrame
                        print(f"\nDataFrame Info:")
                        print(f"Shape: {df.shape}")
                        print(f"Columns: {list(df.columns)}")
                        
                    with open('iframe_source_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    # Return the DataFrame when successful
                    return df
                        
                else:
                    print("Table with ID WEEKLY_SCHED_HTMLAREA not found")
                    
                    # List all tables for debugging
                    all_tables = soup.find_all('table')
                    print(f"Total tables found: {len(all_tables)}")
                    
                    if all_tables:
                        print("Available table IDs:")
                        for i, table in enumerate(all_tables[:10]):  # Show first 10 tables
                            table_id = table.get('id', 'No ID')
                            table_class = table.get('class', 'No Class')
                            if isinstance(table_class, list):
                                table_class = ' '.join(table_class)
                            print(f"  Table {i+1}: ID='{table_id}', Class='{table_class}'")
                    
                    # Save HTML for debugging
                    # with open('iframe_source_debug.html', 'w', encoding='utf-8') as f:
                    #     f.write(html_content)
                    print("Iframe source saved as iframe_source_debug.html for debugging")
                    return None
                    
            except Exception as table_error:
                print(f"Error during table extraction: {table_error}")
                # page.screenshot(path=os.path.join(SCRIPT_DIR, 'weekly_schedule_extraction_error.png'))
                # print("Error screenshot saved as weekly_schedule_extraction_error.png")
                
                # Also save HTML for debugging
                try:
                    html_content = page.content()
                    with open('weekly_schedule_error.html', 'w', encoding='utf-8') as f:
                        f.write(page.content())
                    print("Page source saved as weekly_schedule_error.html for debugging")
                except Exception as debug_error:
                    print(f"Could not save debug HTML: {debug_error}")
        
            # Wait a bit to see the final result
            time.sleep(5)
            
        except Exception as e:
            print(f"Error: {e}")
            # page.screenshot(path=os.path.join(SCRIPT_DIR, "error.png"))
            # print("Error screenshot saved as error.png")
            return None
        finally:
            # Ensure browser is always closed, even if an exception occurs
            try:
                browser.close()
            except:
                pass  # Ignore errors when closing browser

# Main execution block - only runs when script is executed directly
if __name__ == "__main__":
    # Run the getter with default settings
    result = get_timetable()
    if result is not None:
        print("\nTimetable extraction completed successfully!")
        print(f"DataFrame shape: {result.shape}")
    else:
        print("\nTimetable extraction failed.")

