from subprocess import call, check_output 
import ast
import json

EXPORT_PROFILE = "dev_source"
IMPORT_PROFILE = "dev_target"

#Get all group information as a string (json format)
groups_str = check_output("databricks groups --profile " + EXPORT_PROFILE + " list").decode("utf-8")

#Convert group information to a dictionary
groups_dict = ast.literal_eval(groups_str)

#Convert groups to a list
groups_list = groups_dict.get("group_names")

for group in groups_list:
	#Create group in target if it is not "admin"
	if 'admin' not in group:
		print('+++++++ Creating group "' + group + '" in target ++++++')
		call("databricks groups create --group-name " + group + " --profile " + IMPORT_PROFILE, shell=True)
	print()
	
	#Get all user information as a string (json format)
	members_str = check_output("databricks groups list-members --profile " + EXPORT_PROFILE + " --group-name " + group).decode("utf-8")
	
	#Convert user information to a dictionary
	members_dict = ast.literal_eval(members_str)
	
	#Convert users to a list
	members_list = members_dict.get("members")
	
	print('+++++++ Creating users for group "{}" +++++++'.format(group))
	for user in members_list:
		#Get the user name and add the user to the group
		user_name = user.get("user_name")
		print(user_name)
		
		call("databricks groups --profile " + IMPORT_PROFILE + " add-member --parent-name " + group + " --user-name " + user_name)
	print()