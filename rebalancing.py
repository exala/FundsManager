
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from leveraged_position_reserve import get_leveraged_position_reserve
from spot_position_reserve import total_spot_position_reserve
from liquidity_provision import get_liquidity_provision_zapper
from locked_nft import get_locked_nft_zapper
from stablecoin import total_stablecoin
from bybit_marathon import bybit_wallet_marathon
from zapper import fetch_portfolio

SPREADSHEET_ID = '12vSL7nK6_ydl3AxoQLSGMw07ruR8vc8gxbaLH-fwZ38'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def find_next_empty_row(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Rebalancing!C6:C100000000'
    ).execute()
    
    if 'values' not in result:
        return 6
    
    values = result.get('values', [])
    current_row = 6
    
    while current_row <= len(values) + 6:
        # Check if the current row is empty
        row_index = current_row - 6
        if row_index >= len(values) or not values[row_index]:
            return current_row
        current_row += 4
    
    return current_row

def update_rebalancing_sheet():
    current_time = datetime.now()
    current_date = current_time.strftime('%Y-%m-%d')
    
    # Get all balance values
    bybit_balance = float(bybit_wallet_marathon())
    zapper_balance = float(fetch_portfolio())
    total_balance = bybit_balance + zapper_balance
    
    leveraged_position = float(get_leveraged_position_reserve())
    spot_position = float(total_spot_position_reserve())
    liquidity_provision = float(get_liquidity_provision_zapper())
    locked_nft = float(get_locked_nft_zapper())
    stablecoin = float(total_stablecoin())
    
    # Setup Google Sheets
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    # Find the next empty row
    row = find_next_empty_row(service)
    
    # Prepare the ranges and values
    ranges = [
        f'Rebalancing!C{row}:J{row+2}',  # For the main data
        f'Rebalancing!F{row+2}:J{row+2}'  # For the formulas
    ]
    
    # First range values (main data)
    values = [
        [
            current_date, 'CONTROL', total_balance, 
            f'=E{row}*$F$3', f'=E{row}*$G$3', f'=E{row}*$H$3', f'=E{row}*$I$3', f'=E{row}*$J$3'
        ],
        [
            '', 'ACTUAL', total_balance, 
            leveraged_position, spot_position, liquidity_provision, locked_nft, stablecoin
        ],
        [
            '', '', '',
            f'=SUM(F{row}-F{row+1})', f'=SUM(G{row}-G{row+1})', 
            f'=SUM(H{row}-H{row+1})', f'=SUM(I{row}-I{row+1})', f'=SUM(J{row}-J{row+1})'
        ]
    ]
    
    # Update the sheet
    sheet = service.spreadsheets()
    
    # Update main data
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=ranges[0],
        valueInputOption='USER_ENTERED',
        body={'values': values}
    ).execute()
    
    
    
    print(f"Updated Rebalancing sheet at row {row}")

if __name__ == '__main__':
    update_rebalancing_sheet()
