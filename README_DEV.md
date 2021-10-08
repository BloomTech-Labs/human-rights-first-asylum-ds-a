# Installing AWS CLI v2

## macOS – Command Line
#### For all users (sudo)
For the latest version of the AWS CLI, use the following command block:
```
$ curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
$ sudo installer -pkg AWSCLIV2.pkg -target /
```
For a specific version of the AWS CLI, append a hyphen and the version number to the filename. For this example the filename for version 2.0.30 would be AWSCLIV2-2.0.30.pkg resulting in the following command:
```
$ curl "https://awscli.amazonaws.com/AWSCLIV2-2.0.30.pkg" -o "AWSCLIV2.pkg"
$ sudo installer -pkg AWSCLIV2.pkg -target /
```
#### Verify Installation
To verify that the shell can find and run the aws command in your $PATH, use the following commands. If the aws command cannot be found, you may need to restart your terminal.
```
$ which aws
/usr/local/bin/aws 
$ aws --version
aws-cli/2.1.29 Python/3.7.4 Darwin/18.7.0 botocore/2.0.0
```

## Windows - MSI Installer

Run the msiexec command to run the MSI installer.
```
C:\> msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```
#### Verify Installation
To confirm the installation, open the Start menu, search for cmd to open a command prompt window, and at the command prompt use the following command block:
```
C:\> aws --version
aws-cli/2.1.29 Python/3.7.4 Windows/10 botocore/2.0.0
```

## Linux
#### Linux x86 (64-bit)
For the latest version of the AWS CLI, use the following command block:
```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
For a specific version of the AWS CLI, append a hyphen and the version number to the filename. For this example the filename for version 2.0.30 would be awscli-exe-linux-x86_64-2.0.30.zip resulting in the following command:
```
$ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.0.30.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
You can install without sudo if you specify directories that you already have write permissions to. Use the following instructions for the install command to specify the installation location:

Ensure that the paths you provide to the -i and -b parameters contain no volume name or directory names that contain any space characters or other white space characters. If there is a space, the installation fails.

--install-dir or -i – This option specifies the directory to copy all of the files to.

The default value is /usr/local/aws-cli.

--bin-dir or -b – This option specifies that the main aws program in the install directory is symbolically linked to the file aws in the specified path. You must have write permissions to the specified directory. Creating a symlink to a directory that is already in your path eliminates the need to add the install directory to the user's $PATH variable.

The default value is /usr/local/bin.
```
$ ./aws/install -i /usr/local/aws-cli -b /usr/local/bin
```

#### Verify Installation
Confirm the installation with the following command. If the aws command cannot be found, you may need to restart your terminal.
```
$ aws --version
aws-cli/2.1.29 Python/3.7.4 Linux/4.14.133-113.105.amzn2.x86_64 botocore/2.0.0
```
