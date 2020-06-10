"""
This file implements all the Google Sheets backend features for the tab.
"""

import datetime

from googleapiclient.discovery import build

import config
import db
import google_auth


def import_inventory():
    service = build('sheets', 'v4', credentials=google_auth.creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.INVENTORY_SHEET_ID, range="A1:3", majorDimension = "COLUMNS").execute()
    values = result.get('values', [])
    values = list(map(lambda x: [x[0], int(x[1]), int(x[2])], values[1:]))

    print(values)
    db.delete_inventory()
    for i in values:
        db.add_item(i[0], i[1], i[2])
    return len(values)


def import_users():
    service = build('sheets', 'v4', credentials=google_auth.creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.USERS_SHEET_ID, range="A1:D", majorDimension = "ROWS").execute()
    values = result.get('values', [])
    values = list(map(lambda x: [x[0], x[1], x[2], int(x[3])], values))

    users = len(db.get_users())
    print(values)

    export_users() #safety export to not lose data

    db.delete_users()
    for i in values:
        db.add_user(i[0], i[1], i[2], i[3])

    return len(db.get_users()) - users


def import_transactions():
    service = build('sheets', 'v4', credentials=google_auth.creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.TRANSACTIONS_SHEET_ID, range="A1:F").execute()["values"]
    print(result[:10])
    values = list(map(lambda x: (int(x[1]), x[3], x[5], int(float(x[4]))), result[1:]))
    print(values[:10])
    #values = list(map(lambda x: (x[1], x[3], x[5], x[4]), result))

    db.delete_transactions()

    for i in values:
        try:
            db.add_transaction(int(i[0]), None, i[1], i[2], int(i[3]))
        except:
            pass
            #print(i)

    return len(values)


def export_inventory():
    service = build('sheets', 'v4', credentials=google_auth.creds)

    inventory = list(map(lambda x: str(x[0]), db.get_stocks()))

    print(inventory)
    values = [[datetime.datetime.today().isoformat()[:16]] + inventory]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=config.INVENTORY_SHEET_ID, range="A1:A",
        valueInputOption="RAW", body=body).execute()


def export_users():
    service = build('sheets', 'v4', credentials=google_auth.creds)
    sheet = service.spreadsheets()

    date = datetime.datetime.today().isoformat()[:16].replace(":", ".")

    users = list(map(lambda x: [str(i) for i in x], db.get_users()))

    requests = []
    requests.append({
      "addSheet": {
        "properties": {
          "title": date,
          "index": 0
        }
      }
    })

    sheets = sheet.get(spreadsheetId=config.USERS_SHEET_ID).execute()["sheets"]
    horizon = (datetime.datetime.today() - datetime.timedelta(days = 30)).isoformat()

    for i in sheets:
        if i["properties"]["title"] < horizon:
            requests.append({"deleteSheet": {"sheetId": i["properties"]["sheetId"]}})

    add_body = {"requests": requests}
    body = {"values": users}

    response = service.spreadsheets().batchUpdate(
    spreadsheetId=config.USERS_SHEET_ID,
    body=add_body).execute()

    result = service.spreadsheets().values().append(
    spreadsheetId=config.USERS_SHEET_ID, range= date + "!A1",
    valueInputOption="RAW", body=body).execute()

    return len(users)


def export_transactions():
    service = build('sheets', 'v4', credentials=google_auth.creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.TRANSACTIONS_SHEET_ID, range="A1:F").execute()
    values = result.get('values', [])

    end = "2019-01-01"
    if len(values) > 1:
        end = values[-1][5]

    trans = db.get_transactions_after(end)

    mapped = list(map(lambda x: [str(i) for i in x], trans))

    body = {"values": mapped}

    result = service.spreadsheets().values().append(
        spreadsheetId=config.TRANSACTIONS_SHEET_ID, range="A1:A",
        valueInputOption="RAW", body=body).execute()

    return len(trans)
