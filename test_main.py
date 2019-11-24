import os
import  unittest
from main import app

class testClass(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        self.app=app.test_client()
    def tearDown(self):
        pass
    def test_slash(self):
        print('Login Page test')
        resp=self.app.post('/',follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_login(self):
        print('Login test')
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_home(self):
        print('Home test')
        resp=self.app.post('/home',data=dict(myquery='mm'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_render_wallet(self):
        print('Render Wallet test')
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
        resp=self.app.post('/wallet_pg',follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_req_credits(self):
        print('Request Credits test')
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
        resp=self.app.post('/wallet',data=dict(amt='200'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_get_credits(self):
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)   
        resp=self.app.post('/get_wallet',data=dict(passcode='2485'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_render_enlist(self):
        print('Render Enlist test')
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
        resp=self.app.post('/enlist_pr',follow_redirects=True)
        self.assertEqual(resp.status_code,200)
    def test_blockchain(self):
        print('Render blockchain test')
        resp=self.app.post('/login',data=dict(user='ruser',password='root'),follow_redirects=True)
        self.assertEqual(resp.status_code,200)
        resp=self.app.post('/blockchain',follow_redirects=True)
        self.assertEqual(resp.status_code,200)


if __name__=='__main__':
    unittest.main()
