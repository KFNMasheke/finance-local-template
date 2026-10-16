"""Loopback-only local app. No remote services. Python 3.10+."""
import json,sqlite3,pathlib,webbrowser,threading,io,re,sys
from http.server import HTTPServer,BaseHTTPRequestHandler
from analyse import parse
from datetime import datetime
ROOT=pathlib.Path(__file__).resolve().parent
DB=ROOT/'data'/'finance.sqlite3'
PORT=8765

def connection():
    DB.parent.mkdir(exist_ok=True)
    db=sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS states (id INTEGER PRIMARY KEY, saved TEXT DEFAULT CURRENT_TIMESTAMP, body TEXT NOT NULL)')
    return db

def validate(s):
    if not isinstance(s,dict) or s.get('version')!=1 or not all(isinstance(s.get(k),list) for k in ['transactions','income','budgets','debts','audits']) or not isinstance(s.get('settings'),dict):raise ValueError('Invalid finance data')
    return s
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def allowed(self):return self.headers.get('Host')==f'127.0.0.1:{PORT}'
    def reply(self,status,data,mime='application/json'):
        if not isinstance(data,bytes):data=json.dumps(data).encode()
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.allowed():return self.reply(403,{'error':'Invalid host'})
        if self.path=='/api/state':
            with connection() as db:r=db.execute('SELECT body FROM states ORDER BY id DESC LIMIT 1').fetchone()
            return self.reply(200,json.loads(r[0]) if r else None)
        files={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript'),'/core.js':('core.js','text/javascript'),'/style.css':('style.css','text/css')}
        if self.path not in files:return self.reply(404,{'error':'Not found'})
        file,mime=files[self.path];self.reply(200,(ROOT/file).read_bytes(),mime)
    def do_POST(self):
        if not self.allowed() or self.headers.get('Origin')!=f'http://127.0.0.1:{PORT}' or self.headers.get('X-Finance-Local')!='1':return self.reply(403,{'error':'Only the local app can write data'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size>20*1024*1024:raise ValueError('File is larger than 20 MB')
            raw=self.rfile.read(size)
            if self.path=='/api/state':
                state=validate(json.loads(raw))
                with connection() as db:
                    db.execute('INSERT INTO states(body) VALUES (?)',(json.dumps(state),))
                    db.execute('DELETE FROM states WHERE id NOT IN (SELECT id FROM states ORDER BY id DESC LIMIT 100)')
                return self.reply(200,{'ok':True})
            if self.path=='/api/pdf':
                try:from pypdf import PdfReader
                except ImportError:return self.reply(400,{'error':'PDF support is not installed. Run Install-PDF-Support.bat once, or import CSV instead.'})
                pdf=PdfReader(io.BytesIO(raw))
                if pdf.is_encrypted:raise ValueError('Unlock the PDF locally first')
                text='\n'.join(p.extract_text(extraction_mode='layout') or '' for p in pdf.pages)
                rows,opening=parse(text)
                if not rows:raise ValueError('This PDF layout is unsupported. Export a CSV using the supplied template.')
                bad=sum(not r['verified'] for r in rows)
                if bad:raise ValueError('Extracted amounts do not reconcile with running balances. Import CSV or check the statement layout.')
                start=re.search(r'From:\s*(\d{2} [A-Za-z]{3} \d{2})',text);end=re.search(r'To:\s*(\d{2} [A-Za-z]{3} \d{2})',text)
                period_from=datetime.strptime(start[1],'%d %b %y').strftime('%Y-%m-%d') if start else min(r['date'] for r in rows)
                period_to=datetime.strptime(end[1],'%d %b %y').strftime('%Y-%m-%d') if end else max(r['date'] for r in rows)
                return self.reply(200,{'transactions':rows,'opening':opening,'closing':rows[-1]['balance'],'warnings':bad,'from':period_from,'to':period_to})
            self.reply(404,{'error':'Not found'})
        except Exception as e:self.reply(400,{'error':str(e)})
if __name__=='__main__':
    try:server=HTTPServer(('127.0.0.1',PORT),Handler)
    except OSError:
        print('Port 8765 is in use. Close an existing Finance Local window/server and retry.');sys.exit(1)
    print(f'Finance Local is running at http://127.0.0.1:{PORT}. Keep this window open. Ctrl+C to stop.')
    if '--no-browser' not in sys.argv:threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{PORT}')).start()
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
