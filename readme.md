# python env how-to short version

* org article:
    * Windows [https://medium.com/@asheshnathmishra/how-to-create-a-virtual-environment-in-python-on-a-windows-11-system-2023-80cd37c14db3](https://medium.com/@asheshnathmishra/how-to-create-a-virtual-environment-in-python-on-a-windows-11-system-2023-80cd37c14db3)
    * MacOS: [How to activate Python venv on a Mac? \| by Manzeel Uprety \| Medium](https://mnzel.medium.com/how-to-activate-python-venv-on-a-mac-a8fa1c3cb511)

1. Now coming to the steps, first navigate to a folder where you want to create the venv.
2. create a folder “venv” inside Downloads
3. navigate to "venv" folder and type at cmd: "python -m venv venv\_name"
    1. Simply give your venv any name. Once you do this, you will see a folder is created in that path.
4. navigate to Scripts folder inside your venv created and type the command “activate” to go inside your venv.
5. You will observe that the name of your venv now shows in the beginning of the path inside command prompt.

* Now you have successfully created a virtual environment in python.
* You can go ahead and install any library in here using pip command.

## pyenv

- ```pyenv global 3.11```

# Certificate challenges

1. Step #1 on intial setup
   - use:
     - export SSL_CERT_FILE=223943_zscaler.pem
     - pip install {package_name}

   - cd /usr/local/share/ca-certificates/
   - curl -o "CarMax_Cloud_PKI_Root_CA.crt" "http://aia.carmax.cloud.axiadids.net/CarMax_Cloud_PKI_Root_CA.crt"
   - curl -o "CarMax_Cloud_SSL_Issuing_CA.crt" "http://aia.carmax.cloud.axiadids.net/CarMax_Cloud_SSL_Issuing_CA.crt"
   - sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain CarMax_Cloud_PKI_Root_CA.crt
   - sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain CarMax_Cloud_SSL_Issuing_CA.crt
   - export SSL_CERT_FILE=$(python -m certifi)
  2. Install the Required CA Certificates: 
      - Obtain the root and intermediate certificates from your IT or network team. Import these certificates into your system’s and browser's certificate stores.
  3. Set the Environment Variable: 
      - Set the NODE_EXTRA_CA_CERTS environment variable to point to the CA certificate file. This can be done in the terminal using:
      - ```export NODE_EXTRA_CA_CERTS="/path/to/your/ca-certificate.pem"```
  4.  Disable Certificate Verification (Not recommended for production):
       - If this is a development workaround, you might disable strict SSL certificate verification by setting:
       - ```export NODE_TLS_REJECT_UNAUTHORIZED='0'```
       - Note: Disabling SSL verification is not a secure practice and should only be used temporarily for troubleshooting.
  5. Use a Custom HTTPS Agent:
      - For more control within the application, consider using a custom HTTPS agent that points to your CA certificates.
      - Make sure to follow your organization's security policies while making these changes, and consult with your IT or network team as needed.

