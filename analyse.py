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
