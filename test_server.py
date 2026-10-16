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
    def test_split_pdf_text_layout(self):
        from analyse import parse
        text='STATEMENT OPENING BALANCE   -100.00\n  01 Oct 26   Grocery store\n  CHEQUE CARD PURCHASE      - 12.00       -112.00\n  02 Oct 26   Income    50.00     -62.00\n'
        rows,op=parse(text);self.assertEqual(len(rows),2);self.assertTrue(all(r['verified'] for r in rows));self.assertEqual(op,-100)
if __name__=='__main__':unittest.main()
