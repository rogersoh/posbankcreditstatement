import os
import re
import parse
import pdfplumber
import pandas as pd
from collections import namedtuple

DATA_DIR = "data"
SOURCES_DIR = os.path.join(DATA_DIR, "sources")
CSV_DIR = os.path.join(DATA_DIR, "csv")

if not os.path.exists(DATA_DIR):
  os.makedirs(DATA_DIR)
    
if not os.path.exists(SOURCES_DIR):
  os.makedirs(SOURCES_DIR)

if not os.path.exists(CSV_DIR):
  os.makedirs(CSV_DIR)

sources = os.listdir(SOURCES_DIR)
sources = [os.path.join(SOURCES_DIR, f) for f in sources if f.endswith(".pdf")]

Line = namedtuple('Line', 'date Description amount')

# regular expression pattern
statement_re = re.compile(r"(^[0-9]+\s{1}[A-Z]{3})\s(.*)") #to identify that line is a transaction
credit_re = re.compile(r"([0-9,]+\.\d+\sCR)") # cater for the credit 
amount_re = re.compile(r"([0-9,]+\.\d+)") # cater for the expenses

def extractStatement(file):
    lines = []
    total_check = 0
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        for page in pdf.pages:
            text = page.extract_text()
            # print(text)
            # print()
            for line in text.split('\n'):
                comp = statement_re.search(line)
                if comp:
                    amt = credit_re.search(line)
                    if not amt:
                        amt = amount_re.search(line)
                    date, desc, amount = comp.group(1), comp.group(2), 'S$'+ amt.group(1)
                    # print('date', date, ', desc', desc, ', amount', amount)
                    lines.append(Line(date, desc, amount))
        df = pd.DataFrame(lines)
        df.Description = df.Description.replace(" CR","", regex=True)
        df.Description = df.Description.replace(to_replace=r'[0-9.,]+$', value="", regex=True)
        return df

for source in sources:
    filename = source.split('/')[-1].split('.')[0]
    creditcard = extractStatement(source)
    save_path = os.path.join(CSV_DIR, filename+ ".csv")
    creditcard.to_csv(save_path, index=False)