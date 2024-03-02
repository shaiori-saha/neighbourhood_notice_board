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

@pytest.fixture
def new_user():
  # create an user as a fixture to check several cases for create, update, delete
  new_user = {
      "name": "helena",
      "password": "exclamation",
      "email": "helena12@exam.com",
      "phone_numbers": ["9122333", "23345000"],
      "street_name": "new road2",
      "house_number":"40",
      "postal_code": "505055",
      "city": "paris"
      
  }
  res = requests.post('http://localhost:8000/users/', json=new_user)
  result_response = res.json()
  return result_response

@pytest.mark.asyncio
async def test_create_user_with_detailed_assertion():
  new_user = {
        "name": "leo caprio",
        "password": "titanic",
        "email": "sunkensheep@end.com",
        "phone_numbers": ["9122333", "23345000"],
        "street_name": "new iceberg",
        "house_number":"11",
        "postal_code": "76077",
        "city": "new york"
        
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
  delete_res = requests.delete(f"http://localhost:8000/users/{new_user_id}")


@pytest.mark.asyncio
async def test_update_user(new_user):
  #new_user = create_user_for_fixture()
  new_user_id = new_user["id"]

  fields_to_update = {
      "id": new_user_id,
      "name": "sail againS"
      }
  res = requests.put(f"http://localhost:8000/users/{new_user_id}", json=fields_to_update)    
  result_response = res.json()

  assert res.status_code == 200
  assert result_response["name"]==fields_to_update["name"]

  response_from_db = requests.get(f"http://localhost:8000/users/{new_user_id}").json()
  assert response_from_db['name'] == fields_to_update['name']

  delete_res = requests.delete(f"http://localhost:8000/users/{new_user_id}")


@pytest.mark.asyncio
async def test_delete_user(new_user):
  #new_user = create_user_for_fixture()
  new_user_id = new_user["id"]
  res = requests.delete(f"http://localhost:8000/users/{new_user_id}")
  assert res.status_code == 200

  res = requests.get(f"http://localhost:8000/users/{new_user_id}")
  result_response = res.json()
  assert res.status_code == 404
  assert result_response['detail'] == f"user with id:{new_user_id} doesn't exist."


@pytest.mark.asyncio
async def test_user_with_duplicate_email(new_user):
  new_user_1_id = new_user["id"]

  new_user_2 = {
        "name": "helenas",
        "password": "hatiim",
        "email": new_user["email"],
        "street_name": "new road2",
        "house_number":"40",
        "postal_code": "505",
        "city": "paris"
        
       }
  res = requests.post('http://localhost:8000/users/', json=new_user_2)
  result_response = res.json()
  assert res.status_code == 400
  assert result_response['detail'] == f"email {new_user["email"]} already exists"
  print(f"response message {result_response}")
  delete_res = requests.delete(f"http://localhost:8000/users/{new_user_1_id}")
  user_2_res = requests.post('http://localhost:8000/users/', json=new_user_2)  
  assert user_2_res.status_code == 201
  user_2_response = user_2_res.json()
  delete_res_user_2 = requests.delete(f"http://localhost:8000/users/{user_2_response['id']}")