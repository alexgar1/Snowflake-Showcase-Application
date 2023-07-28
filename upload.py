'''
Copies images and HTML to server
'''
import paramiko, os

def copyHTMLwithImage(path, image):
    # Snowflake data and HTML content generation...

    # Write HTML content to a file

    # Connect to the remote server via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('kingspeak34.chpc.utah.edu', username='u6045297', password='X1q9l4571%')

    new = os.path.join(path, image)
    # Transfer the file to the remote server using SCP
    scp = ssh.open_sftp()

    # copy image showcase html
    scp.put(f'{path}images.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/images.html')

    # copy data html
    scp.put(f'{path}data.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data.html')

    # copy data2 html
    scp.put(f'{path}data.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data2.html')

    # copy image
    scp.put(new, '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/'+image)
    scp.put(new[:-4]+'_s.jpg', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/'+image[:-4]+'_s.jpg')
    scp.close()

    # Close the SSH connection
    ssh.close()

def copyHTML(path):
    # Connect to the remote server via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('kingspeak34.chpc.utah.edu', username='u6045297', password='X1q9l4571%')

    scp = ssh.open_sftp()

    # copy image showcase html
    scp.put(f'{path}images.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/images.html')

    # copy data html
    scp.put(f'{path}data.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data.html')

    # copy data html
    scp.put(f'{path}data.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data2.html')
    
    scp.close()

    # Close the SSH connection
    ssh.close()