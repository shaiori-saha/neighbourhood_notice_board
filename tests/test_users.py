import pytest
import requests
import pytest_asyncio

from app.routers.users import  create_user
from app.models import UserCreateRequest

pytest_plugins = ('pytest_asyncio',)


def test_get_users():

    res = requests.get('http://localhost:8000/users/search/')

    expected_response =[{
    "id": 1,
    "name": "sha",
    "email": "petuk@example.com",
    "created_at": "2024-02-11T18:04:17.732550+00:00",
    "address": "berlin",
    "phone_numbers": [
      {
        "id": 1,
        "phone_number": "12345"
      },
      {
        "id": 2,
        "phone_number": "34567"
      }
    ]
  }]

    print(res.json())

    assert res.status_code == 200
    #assert res.json() == expected_response

@pytest.mark.asyncio
async def test_create_user():
    new_user = {
        "name": "shahji",
        "password": "hatimi",
        "email": "again00@exam.com",
        "phone_numbers": []
    }
    res = requests.post('http://localhost:8000/users/', json=new_user)
    
    assert res.status_code == 201

@pytest.mark.asyncio
async def test_update_user():
        new_user = {
        "id": 1,
        "name": "sha shahiii"
        }
        res = requests.put('http://localhost:8000/users/1', json=new_user)
        assert res.status_code == 200

@pytest.mark.asyncio
async def test_delete_user():
        
        res = requests.delete('http://localhost:8000/users/5')
        assert res.status_code == 200


