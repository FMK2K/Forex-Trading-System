import pandas as pd
import os

#NOTE: OPEN THE SHEET SAVED IN C:\Users\FeisalK\ForexBot

def get_line_chart(book, start_row, end_row, labels_col, data_col, title, sheetname):
    chart = book.add_chart({'type': 'line'})
    chart.add_series({
        'categories': [sheetname, start_row, labels_col, end_row, labels_col],
        'values': [sheetname, start_row, data_col, end_row, data_col],
        'line': {'color': 'blue'}
    })
    chart.set_title({'name': title})
    chart.set_legend({'none': True})
    return chart

def add_chart(pairname, cross, df, writer):
    workbook = writer.book
    worksheet = writer.sheets[pairname]
    chart = get_line_chart(workbook, 1, df.shape[0], 8, 9, f"Cum. Gains for {pairname} {cross}", pairname)
    chart.set_size({'x_scale': 2.5, 'y_scale': 2.5})
    worksheet.insert_chart('K1', chart)

def add_pair_charts(ma_test_res, all_trades, writer=None):
    cols = ['time', 'CUM_GAIN']
    df_temp = ma_test_res.drop_duplicates(subset=['pair'])
    for index, row in df_temp.iterrows():
        temp_all_trades = all_trades[(all_trades.CROSS == row.CROSS) & (all_trades.PAIR == row.pair)].copy()
        temp_all_trades.loc[:, 'CUM_GAIN'] = temp_all_trades.GAIN.cumsum()
        temp_all_trades[cols].to_excel(writer, sheet_name=row.pair, startrow=0, startcol=7)
        add_chart(row.pair, row.CROSS, temp_all_trades, writer)

def add_pair_sheets(ma_test_res, writer):
    for p in ma_test_res.pair.unique():
        temp_df = ma_test_res[ma_test_res.pair == p]
        temp_df.to_excel(writer, sheet_name=p, index=False)

def create_excel(ma_test_res, all_trades):
    filename = "ma_results.xlsx"
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except PermissionError:
            print(f"PermissionError: Unable to delete {filename}. Ensure the file is closed and try again.")
            return
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    ma_test_res = ma_test_res[['pair', 'num_trades', 'total_gain', 'mashort', 'malong']].copy()
    ma_test_res['CROSS'] = 'MA_' + ma_test_res.mashort.map(str) + "_" + ma_test_res.malong.map(str)
    ma_test_res.sort_values(by=["pair", "total_gain"], ascending=[True, False], inplace=True)
    all_trades["CROSS"] = "MA_" + all_trades.MASHORT.map(str) + "_" + all_trades.MALONG.map(str)
    all_trades['time'] = [x.replace(tzinfo=None) for x in all_trades.time]

    add_pair_sheets(ma_test_res, writer)
    add_pair_charts(ma_test_res, all_trades, writer)

    writer._save()  # Ensure all data is written before closing

if __name__ == '__main__':
    file_path = 'C:/Users/FeisalK/ForexBot/Part4_Venv/{}'

    if os.path.exists(file_path.format('ma_test_res.pkl')) and os.path.exists(file_path.format('all_trades.pkl')):
        ma_test = pd.read_pickle(file_path.format('ma_test_res.pkl'))
        all_trades = pd.read_pickle(file_path.format('all_trades.pkl'))
        create_excel(ma_test, all_trades)
    else:
        print(f"File not found: {file_path.format('ma_test_res.pkl')} or {file_path.format('all_trades.pkl')}")
