
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from bybit_marathon import bybit_wallet_marathon
from bybit_sprint import bybit_wallet_sprint
from zapper import fetch_portfolio

SPREADSHEET_ID = '12vSL7nK6_ydl3AxoQLSGMw07ruR8vc8gxbaLH-fwZ38'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def update_marathon_sheet(service, current_time, is_end_of_day=False, zapper_balance=None, bybit_balance=None):
    # Use provided balances
    if zapper_balance is None:
        zapper_balance = fetch_portfolio()
    if bybit_balance is None:
        bybit_balance = float(bybit_wallet_marathon())
    current_date = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%I:%M %p')

    sheet = service.spreadsheets()
    
    # Get current values to find the last row
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A6:A1000'
    ).execute()

    first_empty_row = 6
    if 'values' in result:
        first_empty_row = len(result['values']) + 6

    # day_number = ((first_empty_row - 6) // 2) + 1
    # Setup Google Sheets
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    day_number = get_current_cycle(service)

    if is_end_of_day:
        row = first_empty_row - 1
        range_name = f'Reconciliation Marathon Fund!B{row}:I{row}'
        values = [[current_date, time_str, day_number, None, None, None, zapper_balance, bybit_balance]]
    else:
        range_name = f'Reconciliation Marathon Fund!A{first_empty_row}:I{first_empty_row}'
        values = [[current_date, None, time_str, day_number, zapper_balance, bybit_balance, None, None]]

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body={'values': values, 'majorDimension': 'ROWS'}
    ).execute()

def update_sprint_sheet(service, current_time, is_end_of_day=False, bybit_balance=None):
    # Use provided balance
    if bybit_balance is None:
        bybit_balance = float(bybit_wallet_sprint())
    current_date = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%I:%M %p')

    sheet = service.spreadsheets()
    
    # Get current values to find the last row
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Sprint Fund!A6:A1000'
    ).execute()

    first_empty_row = 6
    if 'values' in result:
        first_empty_row = len(result['values']) + 6

    # day_number = ((first_empty_row - 6) // 2) + 1
    # Setup Google Sheets
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    day_number = get_current_cycle(service)

    if is_end_of_day:
        row = first_empty_row - 1
        range_name = f'Reconciliation Sprint Fund!B{row}:I{row}'
        values = [[current_date, time_str, day_number, None, None, None, None, bybit_balance]]
    else:
        range_name = f'Reconciliation Sprint Fund!A{first_empty_row}:I{first_empty_row}'
        values = [[current_date, None, time_str, day_number, None, bybit_balance, None, None]]

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body={'values': values, 'majorDimension': 'ROWS'}
    ).execute()

def get_current_cycle(service):
    # Check Marathon Fund sheet to determine current cycle
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A6:A1000'
    ).execute()
    
    total_rows = len(result.get('values', [])) if 'values' in result else 0
    return total_rows  # Current cycle (1-based)

def update_joint_funds_sheet(service, current_time, is_end_of_day=False):
    current_date = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%I:%M %p')

    sheet = service.spreadsheets()
    
    # Get current values to find the last row
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Joint Funds!A6:A1000'
    ).execute()

    first_empty_row = 6
    if 'values' in result:
        first_empty_row = len(result['values']) + 6

    day_number = get_current_cycle(service)

    if is_end_of_day:
        row = first_empty_row - 1
        range_name = f'Joint Funds!B{row}:D{row}'
        values = [[current_date, time_str, day_number]]
    else:
        range_name = f'Joint Funds!A{first_empty_row}:D{first_empty_row}'
        values = [[current_date, None, time_str, day_number]]

    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body={'values': values, 'majorDimension': 'ROWS'}
    ).execute()

def update_sheets():
    current_time = datetime.now()
    
    # Setup Google Sheets
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    current_cycle = get_current_cycle(service)
    
    # Fetch balances once
    zapper_balance = fetch_portfolio()
    bybit_balance_marathon = float(bybit_wallet_marathon())
    bybit_balance_sprint = float(bybit_wallet_sprint())

    if current_cycle == 0:
        # First run - only start of day
        update_marathon_sheet(service, current_time, is_end_of_day=False, 
                            zapper_balance=zapper_balance, bybit_balance=bybit_balance_marathon)
        update_sprint_sheet(service, current_time, is_end_of_day=False, 
                          bybit_balance=bybit_balance_sprint)
        update_joint_funds_sheet(service, current_time, is_end_of_day=False)
        print("First run - Updated start of day balances")
    elif current_cycle == 31:
        # Last run - only end of day
        update_marathon_sheet(service, current_time, is_end_of_day=True, 
                            zapper_balance=zapper_balance, bybit_balance=bybit_balance_marathon)
        update_sprint_sheet(service, current_time, is_end_of_day=True, 
                          bybit_balance=bybit_balance_sprint)
        update_joint_funds_sheet(service, current_time, is_end_of_day=True)
        print("Last run - Updated end of day balances")
    else:
        # Regular run - both end of previous day and start of new day
        update_marathon_sheet(service, current_time, is_end_of_day=True, 
                            zapper_balance=zapper_balance, bybit_balance=bybit_balance_marathon)
        update_sprint_sheet(service, current_time, is_end_of_day=True, 
                          bybit_balance=bybit_balance_sprint)
        update_joint_funds_sheet(service, current_time, is_end_of_day=True)
        
        # Use same balance values for start of day
        update_marathon_sheet(service, current_time, is_end_of_day=False, 
                            zapper_balance=zapper_balance, bybit_balance=bybit_balance_marathon)
        update_sprint_sheet(service, current_time, is_end_of_day=False, 
                          bybit_balance=bybit_balance_sprint)
        update_joint_funds_sheet(service, current_time, is_end_of_day=False)
        print(f"Updated both end of day and start of day balances for cycle {current_cycle}")

if __name__ == '__main__':

    update_sheets()
