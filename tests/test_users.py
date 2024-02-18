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
    
    assert res.status_code == 200
    #assert res.json() == expected_response


@pytest.mark.asyncio
async def test_delete_user():
        
        res = requests.delete('http://localhost:8000/users/14')
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_user():
    new_user = {
        "name": "ttt",
        "password": "hatimi",
        "email": "tttng@exam.com",
        "phone_numbers": ["00034"],
        "street_name": "abc",
        "house_number":"23",
        "postal_code": "1235",
        "city": "qwe"
        
    }
    res = requests.post('http://localhost:8000/users/', json=new_user)
    result_response = res.json()
    print(f"check city: {result_response["city"]}")
    assert res.status_code == 201
    assert result_response["city"]==new_user["city"]

@pytest.mark.asyncio
async def test_update_user():
        new_user = {
        "id": 1,
        "name": "sha shahiii"
        }
        res = requests.put('http://localhost:8000/users/1', json=new_user)    
        result_response = res.json()

        assert res.status_code == 200
        assert result_response["name"]==new_user["name"]


