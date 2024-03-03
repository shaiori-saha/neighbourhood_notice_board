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
async def test_create_notice_with_detailed_assertion(new_user):
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

  tear_down(new_notice_1['id'], new_notice_1['user_id'])
  tear_down(new_notice_2['id'], new_notice_2['user_id'])
  delete_res = requests.delete(f"{BASE_URL}/users/{non_neighbour_user_id}")

@pytest.mark.asyncio
async def test_create_reactions_of_notices(new_notice_1, new_notice_2):
  neighbour_1_id = new_notice_1['user_id']
  neighbour_2_id = new_notice_2['user_id']

  reaction_by_neigh_2 = {
    "user_id": neighbour_2_id,
    "notice_id": new_notice_1['id'],
    "reaction": "LIKED"
        
    }
  reaction_by_neigh_2_self_like = {
    "user_id": neighbour_2_id,
    "notice_id": new_notice_2['id'],
    "reaction": "LIKED"
        
    }
  reaction_by_neigh_1 = {
    "user_id": neighbour_1_id,
    "notice_id": new_notice_2['id'],
    "reaction": "DISLIKED"
        
    }
  
  reaction_by_neigh_2_self_dislike = {
    "user_id": neighbour_2_id,
    "notice_id": new_notice_2['id'],
    "reaction": "DISLIKED"
        
    }
  reaction_from_neigh_2 = requests.post(f"{BASE_URL}/interactions/user/{neighbour_2_id}/notice/{new_notice_1['id']}", 
                                        json=reaction_by_neigh_2)
  res_by_neigh_2_self_like = requests.post(f"{BASE_URL}/interactions/user/{neighbour_2_id}/notice/{new_notice_2['id']}", 
                                        json=reaction_by_neigh_2_self_like)
  
  reaction_from_neigh_1 = requests.post(f"{BASE_URL}/interactions/user/{neighbour_1_id}/notice/{new_notice_2['id']}", 
                                        json=reaction_by_neigh_1)
  
  reaction_response_neigh_2_like = reaction_from_neigh_2.json()
  reaction_response_neigh_2_like_id = reaction_response_neigh_2_like["id"]
  assert reaction_from_neigh_2.status_code == 201
  assert reaction_response_neigh_2_like['reaction'] == reaction_by_neigh_2['reaction']

  reaction_response_neigh_2_dislike = res_by_neigh_2_self_like.json()
  reaction_response_neigh_2_dislike_id = reaction_response_neigh_2_dislike["id"]

  reaction_response_neigh_1_like = reaction_from_neigh_1.json()
  reaction_response_neigh_1_dislike_id = reaction_response_neigh_1_like["id"]

  reaction_count_res = requests.get(f"{BASE_URL}/interactions/status/notice/{new_notice_2['id']}")
  reaction_status = reaction_count_res.json()
  assert reaction_status['count_liked'] == 1
  assert reaction_status['count_disliked'] == 1

  res_by_neigh_2_self_dislike = requests.post(f"{BASE_URL}/interactions/user/{neighbour_2_id}/notice/{new_notice_2['id']}", 
                                        json=reaction_by_neigh_2_self_dislike)
  reaction_response_neigh_2_self_dislike = res_by_neigh_2_self_dislike.json()
  reaction_response_neigh_2_self_dislike_id = reaction_response_neigh_2_self_dislike["id"]
  
  reaction_count_res_self = requests.get(f"{BASE_URL}/interactions/status/notice/{new_notice_2['id']}")
  reaction_status_self = reaction_count_res_self.json()
  print(reaction_status_self)
  #assert reaction_status_self['count_liked'] == 0
  assert reaction_status_self['count_disliked'] == 2

  delete_reaction_1 = requests.delete(f"{BASE_URL}/interactions/{reaction_response_neigh_2_like_id}")
  delete_reaction_2 = requests.delete(f"{BASE_URL}/interactions/{reaction_response_neigh_2_dislike_id}")
  delete_reaction_3 = requests.delete(f"{BASE_URL}/interactions/{reaction_response_neigh_1_dislike_id}")
  delete_reaction_4 = requests.delete(f"{BASE_URL}/interactions/{reaction_response_neigh_2_self_dislike_id}")
  tear_down(new_notice_1['id'], new_notice_1['user_id'])
  tear_down(new_notice_2['id'], new_notice_2['user_id'])

