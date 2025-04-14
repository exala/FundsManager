import logging
import pycron
from reconciliation import update_sheets, SPREADSHEET_ID
from datetime import datetime
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import time

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def initialize_counter():
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A6:A36'
    ).execute()

    if 'values' not in result:
        return 0

    values = result.get('values', [])
    if not values:
        return 0

    for i, row in enumerate(values):
        if not row:  # If row is empty
            return i

    return len(values)  # If all rows are filled

counter = initialize_counter()

def move_data_to_history():
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Move Marathon Fund data
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A6:X36',
        valueRenderOption='UNFORMATTED_VALUE'
    ).execute()

    if 'values' in result:
        # Find first empty row in history
        history_result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Marathon History!A2:A1000'
        ).execute()

        first_empty_row = 2
        if 'values' in history_result:
            first_empty_row = len(history_result['values']) + 2

        # Get additional cells (K38:M41) with their values
        additional_cells = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Reconciliation Marathon Fund!K38:M41',
            valueRenderOption='FORMATTED_VALUE'  # This gets the displayed values including formula results
        ).execute()

        # Paste to history at first empty row
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Marathon History!A{first_empty_row}',
            valueInputOption='USER_ENTERED',
            body={'values': result['values']}
        ).execute()

        # Add dashes in the next row
        dashes = [['-' for _ in range(27)]]  # 27 columns (A to AA)
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Marathon History!A{first_empty_row + len(result["values"])}',
            valueInputOption='USER_ENTERED',
            body={'values': dashes}
        ).execute()

        # Paste additional cells to Y, Z, AA columns in last 4 rows
        if 'values' in additional_cells:
            last_row = first_empty_row + len(result['values']) - 1
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Marathon History!Y{last_row-3}:AA{last_row}',
                valueInputOption='USER_ENTERED',
                body={'values': additional_cells['values']}
            ).execute()

        # Clear specific columns for Marathon Fund
        # empty_values = [['' for _ in range(6)] for _ in range(31)]  # A-F columns
        # sheet.values().update(
        #     spreadsheetId=SPREADSHEET_ID,
        #     range='Reconciliation Marathon Fund!A6:F36',
        #     valueInputOption='USER_ENTERED',
        #     body={'values': empty_values}
        # ).execute()

        # empty_values = [['' for _ in range(2)] for _ in range(31)]  # H-I columns
        # sheet.values().update(
        #     spreadsheetId=SPREADSHEET_ID,
        #     range='Reconciliation Marathon Fund!H6:I36',
        #     valueInputOption='USER_ENTERED',
        #     body={'values': empty_values}
        # ).execute()

    # Move Sprint Fund data
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Sprint Fund!A6:X36',
        valueRenderOption='UNFORMATTED_VALUE'
    ).execute()

    if 'values' in result:
        # Find first empty row in history
        history_result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Sprint History!A2:A1000'
        ).execute()

        first_empty_row = 2
        if 'values' in history_result:
            first_empty_row = len(history_result['values']) + 2

        # Paste to history at first empty row
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sprint History!A{first_empty_row}',
            valueInputOption='USER_ENTERED',
            body={'values': result['values']}
        ).execute()

        # Add dashes in the next row
        dashes = [['-' for _ in range(24)]]  # 24 columns (A to X)
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sprint History!A{first_empty_row + len(result["values"])}',
            valueInputOption='USER_ENTERED',
            body={'values': dashes}
        ).execute()

        # Get additional cells for Sprint (K38:M41) with their values
        sprint_additional_cells = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Reconciliation Sprint Fund!K38:M41',
            valueRenderOption='FORMATTED_VALUE'  # This gets the displayed values including formula results
        ).execute()

        # Paste additional cells to Y, Z, AA columns in last 4 rows for Sprint
        if 'values' in sprint_additional_cells:
            last_row = first_empty_row + len(result['values']) - 1
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Sprint History!Y{last_row-3}:AA{last_row}',
                valueInputOption='USER_ENTERED',
                body={'values': sprint_additional_cells['values']}
            ).execute()

        # # Clear specific columns for Sprint Fund
        # empty_values = [['' for _ in range(6)] for _ in range(31)]  # A-F columns
        # sheet.values().update(
        #     spreadsheetId=SPREADSHEET_ID,
        #     range='Reconciliation Sprint Fund!A6:F36',
        #     valueInputOption='USER_ENTERED',
        #     body={'values': empty_values}
        # ).execute()

        # empty_values = [['' for _ in range(2)] for _ in range(31)]  # H-I columns
        # sheet.values().update(
        #     spreadsheetId=SPREADSHEET_ID,
        #     range='Reconciliation Sprint Fund!H6:I36',
        #     valueInputOption='USER_ENTERED',
        #     body={'values': empty_values}
        # ).execute()

    # Move Joint Funds data
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Joint Funds!A6:X36',
        valueRenderOption='UNFORMATTED_VALUE'  # Use UNFORMATTED_VALUE to get the calculated values
    ).execute()

    if 'values' in result:
        # Get additional cells for Joint (K38:M41) with their values
        joint_additional_cells = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Joint Funds!K38:M41',
            valueRenderOption='FORMATTED_VALUE'  # This gets the displayed values including formula results
        ).execute()

    if 'values' in result:
        # Find first empty row in history
        history_result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Joint History!A2:A1000'
        ).execute()

        first_empty_row = 2
        if 'values' in history_result:
            first_empty_row = len(history_result['values']) + 2

        # Paste to history at first empty row
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Joint History!A{first_empty_row}',
            valueInputOption='USER_ENTERED',
            body={'values': result['values']}
        ).execute()

        # Add dashes in the next row
        dashes = [['-' for _ in range(27)]]  # 27 columns (A to AA)
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Joint History!A{first_empty_row + len(result["values"])}',
            valueInputOption='USER_ENTERED',
            body={'values': dashes}
        ).execute()

        # Paste additional cells to Y, Z, AA columns in last 4 rows for Joint
        if 'values' in joint_additional_cells:
            last_row = first_empty_row + len(result['values']) - 1
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Joint History!Y{last_row-3}:AA{last_row}',
                valueInputOption='USER_ENTERED',
                body={'values': joint_additional_cells['values']}
            ).execute()

            ###############################################################################################
    # Clear specific columns for Sprint Fund
    empty_values = [['' for _ in range(6)] for _ in range(31)]  # A-F columns
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Sprint Fund!A6:F36',
        valueInputOption='USER_ENTERED',
        body={'values': empty_values}
    ).execute()

    empty_values = [['' for _ in range(2)] for _ in range(31)]  # H-I columns
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Sprint Fund!H6:I36',
        valueInputOption='USER_ENTERED',
        body={'values': empty_values}
        ).execute()

    # Clear specific columns for Marathon Fund
    empty_values = [['' for _ in range(6)] for _ in range(31)]  # A-F columns
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A6:F36',
        valueInputOption='USER_ENTERED',
        body={'values': empty_values}
    ).execute()

    empty_values = [['' for _ in range(2)] for _ in range(31)]  # H-I columns
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!H6:I36',
        valueInputOption='USER_ENTERED',
        body={'values': empty_values}
    ).execute()
    ###############################################################################################

    # Clear specific columns for Joint Funds
    empty_values = [['' for _ in range(4)] for _ in range(31)]  # A-D columns
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range='Joint Funds!A6:D36',
        valueInputOption='USER_ENTERED',
        body={'values': empty_values}
    ).execute()

def get_scheduled_time():
    creds = service_account.Credentials.from_service_account_file(
        'mechanical-standard-afbdba01c069.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range='Reconciliation Marathon Fund!A1'
    ).execute()

    if 'values' in result and result['values']:
        return result['values'][0][0]  # Return the value from A1 cell
    return "08:00"  # Default to 8 AM if no time is found


def get_cron_time():
    scheduled_time = get_scheduled_time()
    if not scheduled_time:
        return "0 8 * * *"  # Default to 8 AM if no time found

    # Parse 24-hour format
    from datetime import datetime
    time_obj = datetime.strptime(scheduled_time, '%H:%M')
    hour = str(int(time_obj.strftime('%H')))  # Convert to int to remove leading zeros
    minute = str(int(time_obj.strftime('%M')))  # Convert to int to remove leading zeros
    print(hour)
    print(minute)
    return f"{minute} {hour} * * *"

# @pycron.cron(get_cron_time())
# async def run(datetime):
#     global counter
#     if counter < 32:
#         print('counter:', counter)
#         update_sheets()
#         counter += 1
#     else:
#         print("Month Completed")
#         move_data_to_history()
#         counter = 0  # Reset counter
#         print("Data moved to history sheets, starting new cycle")

# if __name__ == '__main__':
#     pycron.start()

@pycron.cron("* * * * * */20")
async def run(datetime):
    global counter
    if counter < 32:
        print('counter:', counter)
        update_sheets()
        counter += 1
    else:
        print("Month Completed")
        move_data_to_history()
        counter = 0  # Reset counter
        print("Data moved to history sheets, starting new cycle")

while True:
    try:
        current_time = datetime.datetime.now().strftime("%H:%M")
        scheduled_time = get_scheduled_time()

        print(f"Checking... Current: {current_time}, Scheduled: {scheduled_time}", end='\r')

        if current_time == scheduled_time:
            if last_triggered_time != current_time:
                pycron.start()
                last_triggered_time = current_time
        else:
            # Reset trigger if time changes
            last_triggered_time = None

        time.sleep(20)

    except KeyboardInterrupt:
        print("\nScript stopped")
        break
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(20)

# if __name__ == '__main__':
#     pycron.start()