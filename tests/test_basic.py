# tests/test_basic.py
import requests

BASE = 'http://localhost:5000/api'

def test_list_elections():
    r = requests.get(BASE + '/elections')
    assert r.status_code == 200
