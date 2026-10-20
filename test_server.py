import unittest,tempfile,pathlib,threading,http.client,json
import server
class LocalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();server.DB=pathlib.Path(cls.temp.name)/'data'/'finance.sqlite3'
        cls.http=server.HTTPServer(('127.0.0.1',0),server.Handler);server.PORT=cls.http.server_address[1]
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.temp.cleanup()
    def call(self,method,path,body=None,origin=True):
        c=http.client.HTTPConnection('127.0.0.1',server.PORT)
        h={'Content-Type':'application/json','X-Finance-Local':'1'}
        if origin:h['Origin']=f'http://127.0.0.1:{server.PORT}'
        c.request(method,path,body,h);r=c.getresponse();data=r.read();status=r.status;c.close();return status,data
    def test_static_and_private_files(self):
        self.assertEqual(self.call('GET','/')[0],200)
        self.assertEqual(self.call('GET','/data/finance.sqlite3')[0],404)
        self.assertEqual(self.call('GET','/server.py')[0],404)
    def test_persistence_and_origin(self):
        state={'version':1,'transactions':[],'income':[],'budgets':[],'debts':[],'audits':[],'settings':{}}
        self.assertEqual(self.call('POST','/api/state',json.dumps(state),False)[0],403)
        self.assertEqual(self.call('POST','/api/state',json.dumps(state))[0],200)
        self.assertEqual(json.loads(self.call('GET','/api/state')[1]),state)
        self.assertTrue(server.DB.exists())
    def test_bad_payload(self):
        self.assertEqual(self.call('POST','/api/state','garbage')[0],400)
        self.assertEqual(self.call('POST','/api/state','{}')[0],400)
    def test_rejected_save_preserves_previous_state_and_negative_length_is_bounded(self):
        good={'version':1,'transactions':[],'income':[],'budgets':[],'debts':[],'audits':[],'settings':{}}
        self.assertEqual(self.call('POST','/api/state',json.dumps(good))[0],200)
        bad={**good,'debts':[{'balance':float('nan'),'minimum':10,'apr':None}]}
        self.assertEqual(self.call('POST','/api/state',json.dumps(bad))[0],400)
        self.assertEqual(json.loads(self.call('GET','/api/state')[1]),good)
        connection=http.client.HTTPConnection('127.0.0.1',server.PORT,timeout=2)
        connection.request('POST','/api/state',body=b'',headers={'Content-Length':'-1','Origin':f'http://127.0.0.1:{server.PORT}','X-Finance-Local':'1'})
        response=connection.getresponse()
        self.assertEqual(response.status,400)
        response.read();connection.close()
    def test_pdf_empty_password_security_and_real_password(self):
        import io
        from pypdf import PdfWriter
        from unittest.mock import patch
        for password,expected in [('',200),('required-password',400)]:
            writer=PdfWriter();page=writer.add_blank_page(width=100,height=100)
            from pypdf.generic import NameObject,DecodedStreamObject
            stream=DecodedStreamObject();stream.set_data(b'BT ET');page[NameObject('/Contents')]=stream
            writer.encrypt(password)
            output=io.BytesIO();writer.write(output)
            with patch('server.statement',return_value={'summaryVerified':True}):
                status,body=self.call('POST','/api/pdf',output.getvalue())
            self.assertEqual(status,expected,body)
            if expected==400:self.assertIn('password',json.loads(body)['error'])
    def test_split_pdf_text_layout(self):
        from analyse import parse
        text='STATEMENT OPENING BALANCE   -100.00\n  01 Oct 26   Grocery store\n  CHEQUE CARD PURCHASE      - 12.00       -112.00\n  02 Oct 26   Income    50.00     -62.00\n'
        rows,op=parse(text);self.assertEqual(len(rows),2);self.assertTrue(all(r['verified'] for r in rows));self.assertEqual(op,-100)
if __name__=='__main__':unittest.main()

class StatementValidationTests(unittest.TestCase):
    def text(self):
        return 'STANDARD BANK\nFrom: 01 Oct 26\nTo: 02 Oct 26\nAccount number: 10 12 204 273 3         051001\nSTATEMENT OPENING BALANCE -100.00\n01 Oct 26 Store -12.00 -112.00\n02 Oct 26 Salary 50.00 -62.00\nStatement Summary\nPayments -R12.00\nDeposits R50.00'
    def test_summary_and_account(self):
        from analyse import statement
        data=statement(self.text());self.assertEqual(data['accountLast4'],'2733');self.assertTrue(data['summaryVerified']);self.assertEqual(data['closing'],-62)
    def test_partial_or_bad_statement_is_rejected(self):
        from analyse import statement
        for text in [self.text().replace('Deposits R50.00','Deposits R51.00'),self.text().replace('-112.00','-111.00'),self.text().replace('STANDARD BANK','OTHER BANK'),self.text().split('Statement Summary')[0]]:
            with self.assertRaises(ValueError):statement(text)
