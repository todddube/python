from azhelper import *
# code, response = az_cli("ad user show --id tdube-cl@carmax.com")
response = az_cli("ad user show --id tdube-cl@carmax.com")
print ("Info: $s" % (response))
print (response)

## az ad user list --upn "tdube-cl@carmax.com"