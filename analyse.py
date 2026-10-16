"""Parse supported text-based Standard Bank statement layouts; never infer amounts."""
import re,json
from datetime import datetime
DATE=re.compile(r'^\s*(\d{2} [A-Za-z]{3} \d{2})\s+(.+)$')
MONEY=re.compile(r'-?\s*\d[\d,]*\.\d{2}')
def number(s):return float(re.sub(r'\s|,','',s))
def parse(text):
    rows=[]
    opening=re.search(r'STATEMENT OPENING BALANCE\s+(-?[\d,]+\.\d{2})',text)
    opening=number(opening[1]) if opening else None
    prev=opening;lines=text.splitlines()
    for index,line in enumerate(lines):
        m=DATE.match(line)
        if not m:continue
        # pypdf sometimes places the numbers on the secondary description line.
        description=m[2].strip();found=None;details=[]
        for j in range(index,min(index+5,len(lines))):
            if j>index and DATE.match(lines[j]):break
            nums=list(MONEY.finditer(lines[j]))
            if len(nums)>=2:
                amount=number(nums[-2][0]);bal=number(nums[-1][0]);found=(amount,bal)
                prefix=lines[j][:nums[-2].start()].strip()
                if j==index:description=DATE.match(prefix)[2].strip()
                elif prefix:details.append(prefix)
                break
            if j>index and lines[j].strip():details.append(lines[j].strip())
        if found is None:continue
        amount,bal=found
        if j==index:
            for detail in lines[index+1:index+3]:
                if DATE.match(detail):break
                if detail.strip():details.append(detail.strip())
        diff=round(bal-prev,2) if prev is not None else amount
        rows.append({'date':datetime.strptime(m[1],'%d %b %y').strftime('%Y-%m-%d'),'description':description,'amount':amount,'balance':bal,'balanceDifference':diff,'verified':abs(diff-amount)<.011,'details':' '.join(details)})
        prev=bal
    return rows,opening
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Extract layout text from a Standard Bank statement into JSON')
    p.add_argument('text_file');p.add_argument('output_file');a=p.parse_args()
    rows,opening=parse(open(a.text_file,encoding='utf8').read())
    json.dump({'transactions':rows,'opening':opening},open(a.output_file,'w',encoding='utf8'),indent=2)
    print(f'{len(rows)} rows extracted')


def statement(text):
    """Validate a Standard Bank PDF against running balances and printed summary."""
    if not re.search(r'STANDARD\s+BANK|standardbank\.co\.za',text,re.I):
        raise ValueError('This importer supports Standard Bank statements. Bank heading not found.')
    rows,opening=parse(text)
    if opening is None or not rows:raise ValueError('No readable statement ledger found. Upload the original text-based PDF, not a scan.')
    if any(not r['verified'] for r in rows):raise ValueError('Amounts do not reconcile with every running balance. Nothing imported; check the PDF format.')
    start=re.search(r'From:\s*(\d{2} [A-Za-z]{3} \d{2})',text);end=re.search(r'To:\s*(\d{2} [A-Za-z]{3} \d{2})',text)
    if not start or not end:raise ValueError('Statement From / To dates not found. Nothing imported.')
    first=datetime.strptime(start[1],'%d %b %y').strftime('%Y-%m-%d');last=datetime.strptime(end[1],'%d %b %y').strftime('%Y-%m-%d')
    if first>last or any(not first<=r['date']<=last for r in rows):raise ValueError('Transactions fall outside the printed statement dates.')
    summary=text.rsplit('Statement Summary',1)[-1] if 'Statement Summary' in text else ''
    payments=re.search(r'Payments\s+(-?\s*R?\s*[\d,]+\.\d{2})',summary)
    deposits=re.search(r'Deposits\s+(-?\s*R?\s*[\d,]+\.\d{2})',summary)
    if not payments or not deposits:raise ValueError('Printed statement summary not found. Upload the complete PDF with all pages.')
    paid=round(sum(-r['amount'] for r in rows if r['amount']<0),2);received=round(sum(r['amount'] for r in rows if r['amount']>0),2)
    if abs(abs(number(payments[1].replace('R','')))-paid)>.011 or abs(number(deposits[1].replace('R',''))-received)>.011:raise ValueError('Printed payments / deposits do not match extracted rows. Nothing imported.')
    account=re.search(r'Account number:[ \t]*([0-9]+(?: [0-9]+)*)',text,re.I);digits=re.sub(r'\D','',account[1]) if account else ''
    return {'transactions':rows,'opening':opening,'closing':rows[-1]['balance'],'warnings':0,'from':first,'to':last,'accountLast4':digits[-4:],'summaryVerified':True,'payments':paid,'deposits':received}
