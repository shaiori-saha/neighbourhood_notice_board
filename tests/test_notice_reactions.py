import pytest
import requests
import pytest_asyncio
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter

from app.database import get_db
from app.routers.users import  create_user
from app.models import UserCreateRequest
from app.schemas import User as UserDao
from tests.test_users import new_user, new_user_2


pytest_plugins = ('pytest_asyncio',)
BASE_URL = "http://localhost:8000"

def tear_down(new_notice_id, new_user_id):
  delete_notice = requests.delete(f"{BASE_URL}/notices/{new_notice_id}")
  delete_user = requests.delete(f"{BASE_URL}/users/{new_user_id}")
  return 

@pytest.fixture
def new_notice_1(new_user):
  user_id = new_user['id']
  new_notice = {
       "content": "lets write a poem",
        "user_id": user_id
  }
  res = requests.post(f"{BASE_URL}/notices/", json=new_notice)
  result_response = res.json()
  return result_response


@pytest.fixture
def new_notice_2(new_user_2):
  user_id = new_user_2['id']
  new_notice = {
       "content": "lets write a story",
        "user_id": user_id
  }
  res = requests.post(f"{BASE_URL}/notices/", json=new_notice)
  result_response = res.json()
  return result_response

@pytest.fixture
def new_user_3():
  # create an user as a fixture to check several cases for create, update, delete
  new_user_3_body = {
      "name": "different user",
      "password": "johndoe",
      "email": "diff12@exam.com",
      "phone_numbers": ["70150044"],
      "street_name": "diff road 22",
      "house_number":"88",
      "postal_code": "505059",
      "city": "paris"
      
  }
  res = requests.post(f"{BASE_URL}/users/", json=new_user_3_body)
  result_response = res.json()
  return result_response

@pytest.mark.asyncio
async def test_create_notice_reaction_with_detailed_assertion(new_user):
  user_id  = new_user["id"]
  new_notice = {
        "content": "new sprint planning",
        "user_id": user_id
        
    }
  res = requests.post(f"{BASE_URL}/notices/", json=new_notice)
  notice_response = res.json()
  notice_id = notice_response["id"]
  assert res.status_code == 201
  assert notice_response['content'] == new_notice['content']
  assert notice_response['user_id'] == new_notice['user_id']
  tear_down(notice_id, user_id)

@pytest.mark.asyncio
async def test_get_notices_from_neighbours(new_notice_1, new_notice_2, new_user_3):
  neighbour_1_id = new_notice_1['user_id']
  neighbour_2_id = new_notice_2['user_id']
  non_neighbour_user_id = new_user_3['id']

  list_of_notices_for_neigh_1 = requests.get(f"{BASE_URL}/interactions/view_notices/user/{neighbour_1_id}")
  list_of_non_neigh = requests.get(f"{BASE_URL}/interactions/view_notices/user/{non_neighbour_user_id}")
  assert len(list_of_non_neigh.json()) == 0
  assert len(list_of_notices_for_neigh_1.json()) == 2

  print(list_of_notices_for_neigh_1.json())
  tear_down(new_notice_1['id'], new_notice_1['user_id'])
  tear_down(new_notice_2['id'], new_notice_2['user_id'])
  delete_res = requests.delete(f"{BASE_URL}/users/{non_neighbour_user_id}")
