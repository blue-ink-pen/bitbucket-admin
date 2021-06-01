import requests
from atlassian import Bitbucket
import logging

logging.basicConfig(filename='bitbucket_connect.log', filemode='w', level=logging.DEBUG)


try:

  #s = requests.Session()
  #s.headers['Authorization'] = 'Bearer ODQxMDk1MjM2MDAyOmwnG3YrYz//ooaXoks24NMnb/yx'
  #bitbucket = Bitbucket(url='http://localhost:7990', session=s)
  bitbucket = Bitbucket(url='http://localhost:7990', username="bitbucket-admin", password="P@ssw0rd")

  project_list = bitbucket.project_list()


  for project in project_list:

    project_key = project.get("key")
    project_type = project.get("type")
    project_public = str(project.get("public"))
    project_link = str(project.get("links").get("self"))
    print("projectkey:" + project_key)
    print("type:" + project_type)
    print("public:" + project_public)
    print("link:" + project_link)
    
    for repo in bitbucket.repo_list(project_key):
      print(repo)
      repo_name = repo.get("name")
      repo_links = str(repo.get("links"))
      print("  reponame:"+repo_name)
      print("  repolinks"+repo_links)

      repo_users = bitbucket.repo_users(project_key, repo_name, limit=9999, filter_str=None)
    
      for repo_user in repo_users:
        print(repo_user)
        user_name = repo_user.get("user").get("name")
        user_active = str(repo_user.get("user").get("active"))
        user_permission = repo_user.get("permission")
        print("   username:"+user_name)
        print("   user_active:"+user_active)        
        print("   user_permission:"+user_permission)        
        

  print("--------")


except Exception as e:
    logging.error(e)
    






