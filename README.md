![nginx 1.7.8](https://img.shields.io/badge/nginx-1.7.8-brightgreen.svg)
![Kibana Dashboard](https://raw.githubusercontent.com/Troyhy/harbour/master/fluentd-data/kibana_nginx_dash.jpg)
Docker container runner with centralised logging and automated nginx proxy.

This is collection of docker containers and configuration files to simplify running single host multidomain webserver.

This package gives you:

 * [fabric][3]-script handling installation of Harbour to new machine.
 * [nginx-proxy][4] with [docker-gen][1] that will detect your containers and their domains.
 * Centralized logging with [fluentd][5]
 * Elasticsearch backend for storing logs
 * Kibana 4 for searching and visualisation 
 * Logrotate for rotating Docker logs

  [1]: https://github.com/jwilder/docker-gen
  [2]: http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/
  [3]: https://github.com/fabric/fabric
  [4]: https://github.com/Troyhy/nginx-proxy
  [5]: https://github.com/fluent/fluentd
  
  
### Installation

  1. User with sudo rights and server hostname/ip
  2. fab create_new_harbour:<user>@<hostname>
  3. harbour installs Docker and other dependencies
  4. test new Harbour http://<hostname> 
  5. make fake domain in your local machine
  
     `
     echo '<host_ip>  example.com' >> /etc/hosts
     `
  5. run container with domain associated to it:
  
     `
     sudo docker run -e VIRTUAL_HOST=example.com -e LOG=true tutum/hello-world
     `
