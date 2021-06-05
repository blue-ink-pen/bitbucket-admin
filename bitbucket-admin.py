import requests
from atlassian import Bitbucket
import logging
import pandas as pd
import numpy as np
import os.path


logging.basicConfig(filename='bitbucket_connect.log', filemode='w', level=logging.DEBUG)


try:

   
  # Read username, password, file path  
  username = input("Username:\n")
  while len(username) == 0:
    print("Please input valid username.")
    username = input("Username:\n")

  password = input("Password:\n")
  while len(password) == 0:
    print("Please input valid password.")
    password = input("Password:\n")

  filepath = input("Filepath:\n")  
  while (len(filepath) == 0) or (os.path.isfile(filepath) == False):
    print("Please input valid file path.")
    filepath = input("Filepath:\n")  

  bitbucket_url = input("Bitbucket URL in http://<hostname>:port format.\nLeave empty to use default: http://localhost:7990.")  
  if len(bitbucket_url) == 0:
    bitbucket_url =  'http://localhost:7990'
    
    
  # Create data frame to store project/repo/user/permission from user input.   
  dfUserInput = pd.read_csv(filepath)

  # Check user input file format.    
  if len(dfUserInput.columns) != 4:
    print("Input file must have 4 columns: PROJECT_KEY,REPO_NAME,USER_NAME,USER_PERMISSION")
    error("Input file must have 4 columns: PROJECT_KEY,REPO_NAME,USER_NAME,USER_PERMISSION")
    
  # Define data frame columns  
  dfColumns = ['PROJECT_KEY','PROJECT_PUBLIC','REPO_NAME','USER_NAME','USER_ACTIVE','USER_PERMISSION']

    

  # Display user input
  print("--------------------------------------")
  print("|          User Input                |")
  print("--------------------------------------")
  print(dfUserInput) 
  print("")    
    
  # Create data frame to store project/repo/user/permission queried from Bitbucket.
  dfBitbucket = pd.DataFrame(columns=dfColumns)
    
    
  # Connect to bitbucket
  print ("Connecting to bitbucket at "+bitbucket_url)
  bitbucket = Bitbucket(url=bitbucket_url, username=username, password=password)  

    
  # Read project list  
  project_list = bitbucket.project_list()

    
  # The following iterate through project and repo
  for project in project_list:

    project_key = project.get("key")
    project_type = project.get("type")
    project_public = str(project.get("public"))
    project_link = str(project.get("links").get("self"))
    
    for repo in bitbucket.repo_list(project_key):
      repo_name = repo.get("name")
      repo_links = str(repo.get("links"))

      repo_users = bitbucket.repo_users(project_key, repo_name, limit=9999, filter_str=None)
    
      for repo_user in repo_users:
        user_name = repo_user.get("user").get("name")
        user_active = str(repo_user.get("user").get("active"))
        user_permission = repo_user.get("permission")
        # Add row to dfBitbucket.
        dfBitbucket = dfBitbucket.append(pd.DataFrame(data=np.array([[project_key,project_public,repo_name,user_name,user_active,user_permission]]), 
                          columns=dfColumns))
        
  
  # Display current configuration in bitbucket
  print("--------------------------------------")
  print("|  Bitbucket Current Configuration    |")
  print("--------------------------------------")
  print(dfBitbucket)
  print("")  


  # Display warning about public repository.
  print("--------------------------------------")
  print("|   Checking for public repository    |")
  print("--------------------------------------")
   
  dfPublicRepo = dfBitbucket.copy()  
  dfPublicRepo = dfPublicRepo[(dfPublicRepo.PROJECT_PUBLIC=="True")]
  dfPublicRepo = dfPublicRepo.drop(["USER_NAME","USER_ACTIVE","USER_PERMISSION"], axis=1)
  dfPublicRepo = dfPublicRepo.drop_duplicates()  
  if (len(dfPublicRepo.index) > 0) :
    print("Warning: The follow project/repo are public.")
    print(dfPublicRepo)
  else :
    print("No repository is configured as public.")
  print("")  
   
    
    
  # Drop column "PROJECT_PUBLIC"   
  dfBitbucket2 = dfBitbucket.copy()
  dfBitbucket2 = dfBitbucket2.drop(["PROJECT_PUBLIC"], axis=1) 
    
    
  # Add column "USER_ACTIVE" to dfUserInput. Assume all user in the user input are active.
  dfUserInput2 = dfUserInput.copy()
  dfUserInput2["USER_ACTIVE"] = "True"                                 
  
        
    
  # Compare User Input vs Bitbucket.
  print("--------------------------------------")
  print("|   Compare User Input vs Bitbucket   |")
  print("--------------------------------------")
    
    
  dfConcat = pd.concat([dfBitbucket2, dfUserInput2])  
  dfConcat = dfConcat.reset_index(drop=True)   
  
      
  dfGroupBy = dfConcat.groupby(list(dfConcat.columns))  
  idx = [x[0] for x in dfGroupBy.groups.values() if len(x) == 1]  
  dfConcatDiff = dfConcat.reindex(idx)
    

    
  if (len(dfConcatDiff) == 0) :
    print("User input and Bitbucket equal.")
  else :  
    df = pd.merge(dfUserInput2, dfBitbucket2, how='outer', suffixes=('','_y'), indicator=True)
    dfInUserInput_NotInBitbucket = df[df['_merge']=='left_only'][dfUserInput2.columns]
        
    df = pd.merge(dfBitbucket2, dfUserInput2, how='outer', suffixes=('','_y'), indicator=True)
    dfInBitbucket_NotUserInput = df[df['_merge']=='left_only'][dfBitbucket2.columns]
    
    if (len(dfInUserInput_NotInBitbucket.index) > 0):
      print("IN User Input NOT in Bitbucket:")
      print(dfInUserInput_NotInBitbucket)
      print("")
    
    if (len(dfInBitbucket_NotUserInput.index) > 0):
      print("In Bitbucket NOT in User Input:")
      print(dfInBitbucket_NotUserInput)
      print("")

except Exception as e:
    print(e)
    logging.error(e)
    






