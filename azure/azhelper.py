from azure.cli.core import get_default_cli
import tempfile

def az_cli (args_str):
    temp = tempfile.TemporaryFile()
    args = args_str.split()
    code = get_default_cli().invoke(args, None, temp)
    temp.seek(0)
    data = temp.read().strip()
    temp.close()
    return [code, data]

## az ad user list --upn "tdube-cl@carmax.com"