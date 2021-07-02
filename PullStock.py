def scan_file(path_to_file):
    """
    Retrieves tickers in the table and return a dict where the key is the ticker and the value is the name
    e.g. {'AAPL','Apple Inc.', 'GOOG' ,'Alphabet Inc.'}
}
    :param path_to_file : stock table csv file path
    :return: stock dictionary
    """
    all_data = {}
    with open(path_to_file, 'r') as eFile:
        for line in eFile:
            _stockInfo = line.split(',', 1)
            all_data[_stockInfo[0]] = _stockInfo[1].strip('\n')
    eFile.close()
    return all_data
    #print(all_data)
