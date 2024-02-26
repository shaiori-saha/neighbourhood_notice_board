import pytest
import requests
import pytest_asyncio
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter

from app.database import get_db
from app.routers.users import  create_user
from app.models import UserCreateRequest
from app.schemas import User as UserDao


pytest_plugins = ('pytest_asyncio',)


'''def test_get_users():

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
        assert res.status_code == 200'''


'''@pytest.mark.asyncio
async def test_create_update_delete_user():
    # create an user
    new_user = {
        "name": "helena",
        "password": "hatimi",
        "email": "helena12@exam.com",
        "phone_numbers": ["9122333", "23345000"],
        "street_name": "new road2",
        "house_number":"40",
        "postal_code": "505",
        "city": "paris"
        
    }
    res = requests.post('http://localhost:8000/users/', json=new_user)
    result_response = res.json()
    new_user_id = result_response["id"]
    assert res.status_code == 201
    assert result_response["city"]==new_user["city"]
    print(f"check city: {result_response["city"]}")
    assert result_response["postal_code"]==new_user["postal_code"]
    assert result_response["house_number"]==new_user["house_number"]
    print(f"phone numbers added: {result_response["phone_numbers"]}")
    assert new_user["phone_numbers"]== [result_response["phone_numbers"][i]["phone_number"] for 
                                        i in range(len(result_response["phone_numbers"]))]
    assert result_response["email"]==new_user["email"]
    assert result_response["name"]==new_user["name"]

   # update the user
    fields_to_update ={
          "id": new_user_id,
          #"street_name": "ajab gali", # need to add in put
          "house_number":"10"
          }
    updated_response = requests.put(f"http://localhost:8000/users/{new_user_id}", json=fields_to_update)    
    updated_response_result = updated_response.json()

    assert updated_response.status_code == 200
    assert updated_response_result["house_number"]==fields_to_update["house_number"]

    delete_res = requests.delete(f"http://localhost:8000/users/{new_user_id}")
    assert delete_res.status_code == 200'''

@pytest.mark.asyncio
async def test_user_with_duplicate_email():
    with pytest.raises(Exception) as e_info:
      new_user = {
        "name": "helenas",
        "password": "hatiim",
        "email": "eso@example.com",
        "street_name": "new road2",
        "house_number":"40",
        "postal_code": "505",
        "city": "paris"
        
       }
      res = requests.post('http://localhost:8000/users/', json=new_user)
      result_response = res.json()
      assert res.status_code == 201
    print(e_info)

'''@pytest.mark.asyncio
async def test_update_user():
        new_user = {
        "id": 1,
        "name": "sha shahiii"
        }
        res = requests.put('http://localhost:8000/users/1', json=new_user)    
        result_response = res.json()

        assert res.status_code == 200
        assert result_response["name"]==new_user["name"]'''


