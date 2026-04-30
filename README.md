# phone-communication-analysis
По результатам скрипт покажет все коммуникации (входящие, исходящие звонки, заявки, заполненные формы), разобьёт по источникам и адресатам. Поддерживает пакетную обработку файлов (для каждого номера свои фильтры дат).

## Phone Communication Analysis

## Description
This project analyzes customer communications based on a list of phone numbers.
It processes communication data from a database and calculates activity metrics for each phone number.

## Features
- Data extraction from SQL database
- Phone number normalization
- Matching input phone list with database records
- Aggregation of communication activity
- Calculation of key metrics

## Tech Stack
- Python
- pandas
- SQLAlchemy

## How It Works
1. Loads communication data from a database
2. Cleans and normalizes phone numbers
3. Matches input phone list with database records
4. Aggregates communication metrics
5.Outputs analysis results
