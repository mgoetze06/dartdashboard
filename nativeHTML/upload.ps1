#session = New-PSSession albs-ubuntuserv -Name boris

scp ./static/style.css boris@albs-ubuntuserv:/home/boris/projects/dartdashboard/nativeHTML/static
scp ./templates/index.html boris@albs-ubuntuserv:/home/boris/projects/dartdashboard/nativeHTML/templates
scp server.py boris@albs-ubuntuserv:/home/boris/projects/dartdashboard/nativeHTML