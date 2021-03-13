# DNS-Server-Proxy-Cloudflare
DNS (Domain Name System) is responsible for translating domain names to IP addresses. It’s designed in 1987 with no security or privacy in mind. By default DNS queries are not encrypted. They are sent in plain text on the wire and can be exploited by middle entities. For example, the Great Firewall of China (GFW) uses a technique called DNS cache poison to censor the Chinese Internet. (They also use other methods, which are beyond the scope of this article.)

GFW checks every DNS query that is sent to a DNS server outside of China. Since plain text DNS protocol is based on UDP, which is a connection-less protocol, GFW can spoof both the client IP and server IP. When GFW finds a domain name on its block list, it changes the DNS response. For instance, if a Chinese Internet user wants to visit google.com, GFW returns an IP address located in China instead of Google’s real IP address, to the user’s DNS resolver. Then the DNS resolver returns the fake IP address to the user’s computer, so the user cannot visit google.com.

DNS over TLS means that DNS queries are sent over a secure connection encrypted with TLS, the same technology that encrypts HTTP traffic.

This project is a DNS proxy or DNS forwarder that works as a DNS resolver for client application but requires an upstream DNS server, CloudFlare DNS server is used in this project as an upstream DNS server, to perform the DNS lookup. It receives queries from the clients and forward it to the CloudFlare DNS server for the results.

## Diagram
![enter image description here](https://raw.githubusercontent.com/mrvarmazyar/DNS-Server-Proxy-Cloudflare/main/screenshot/dns-server-diagram.png)


## Notes

In this simple app, I've used CloudFlare DNS Over TLS (1.1.1.1) for querying the client requests.
* It will create a socket connection and bind it on host 0.0.0.0 on port 53
* After deploy the K8S folder manifests, we're going to have a Loadbalancer IP (It depends on Cloud Provider)
* Receive UDP DNS requests on the Loadbalancer IP and create a thread for the request and run RequestHandler
* RequestHandler will call the function to create TLS connection cloudflare dns server on port 853 using self-signed certificate and after that convert UDP request into TCP DNS query and send it to Cloudflare DNS server over the tcp connection, when the server got TCP answer from Cloudflare DNS server, it will convert the result into UDP and respond to the client over the same Docker network socket connection
* Currently, It is handling nslookup and dig requests

### How to setup?

* Run the following commands to deploy it on kubernetes:
```bash
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare$ cd ./K8S
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare/K8S$ kubectl create -f ./
deployment.apps/dns-server created
service/dns-server created
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare/K8S$ kubectl get svc -n default
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP          PORT(S)        AGE
dns-server   LoadBalancer   10.0.179.136   <MASKED_IPADDRESS>   53:31980/UDP   88s
kubernetes   ClusterIP      10.0.0.1       <none>               443/TCP        278d
```

*Note1: I used Azure kubernetes service to deploy this application so the external IP has acquired from Azure infrastructure as well*


*Note2: The DNS IP address is `MASKED_IPADDRESS`*


Now we should set the dns address on our client as follows


```bash
echo "nameserver MASKED_IPADDRESS" > /etc/resolv.conf
```

To test and check the server's log we can run these commands:

```bash
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare/K8S$ kubectl logs dns-server-bc657779c-fb458 -n default -f #Pod name should be different in your system
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare/K8S$ dig @MASKED_IPADDRESS -p 53 msn.com

; <<>> DiG 9.11.3-1ubuntu1.7-Ubuntu <<>> @MASKED_IPADDRESS -p 53 msn.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 50898
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; PAD: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ("............................................................................................................................................................................................................................................................................................................................................................................................................................")
;; QUESTION SECTION:
;msn.com.                       IN      A

;; ANSWER SECTION:
msn.com.                4090    IN      A       13.82.28.61

;; Query time: 120 msec
;; SERVER: MASKED_IPADDRESS#53(MASKED_IPADDRESS)
;; WHEN: Fri Mar 12 19:19:30 +0330 2021
;; MSG SIZE  rcvd: 468
mohammad@DESKTOP-G98ERLC:~/DNS-Server-Proxy-Cloudflare/K8S$ nslookup microsoft.net
Server:         MASKED_IPADDRESS
Address:        MASKED_IPADDRESS#53

Non-authoritative answer:
Name:   microsoft.net
Address: 40.112.72.205
Name:   microsoft.net
Address: 40.76.4.15
Name:   microsoft.net
Address: 40.113.200.201
Name:   microsoft.net
Address: 13.77.161.179
Name:   microsoft.net
Address: 104.215.148.63
```

The dns-server's log should be something like this:

```
{'crlDistributionPoints': (u'http://crl3.digicert.com/DigiCertTLSHybridECCSHA3842020CA1.crl', u'http://crl4.digicert.com/DigiCertTLSHybridECCSHA3842020CA1.crl'), 'subjectAltName': (('DNS', 'cloudflare-dns.com'), ('DNS', '*.cloudflare-dns.com'), ('DNS', 'one.one.one.one'), ('IP Address', '1.1.1.1'), ('IP Address', '1.0.0.1'), ('IP Address', '162.159.36.1'), ('IP Address', '162.159.46.1'), ('IP Address', '2606:4700:4700:0:0:0:0:1111\n'), ('IP Address', '2606:4700:4700:0:0:0:0:1001\n'), ('IP Address', '2606:4700:4700:0:0:0:0:64\n'), ('IP Address', '2606:4700:4700:0:0:0:0:6400\n')), 'notBefore': u'Jan 11 00:00:00 2021 GMT', 'caIssuers': (u'http://cacerts.digicert.com/DigiCertTLSHybridECCSHA3842020CA1.crt',), 'OCSP': (u'http://ocsp.digicert.com',), 'serialNumber': u'05076F66D11B692256CCACD546FFEC53', 'notAfter': 'Jan 18 23:59:59 2022 GMT', 'version': 3L, 'subject': ((('countryName', u'US'),), (('stateOrProvinceName', u'California'),), (('localityName', u'San Francisco'),), (('organizationName', u'Cloudflare, Inc.'),), (('commonName', u'cloudflare-dns.com'),)), 'issuer': ((('countryName', u'US'),), (('organizationName', u'DigiCert Inc'),), (('commonName', u'DigiCert TLS Hybrid ECC SHA384 2020 CA1'),))}
```
![enter image description here](https://raw.githubusercontent.com/mrvarmazyar/DNS-Server-Proxy-Cloudflare/main/screenshot/dns-server-log.png)


We can also scale up the service to achieve more high availability:


![enter image description here](https://raw.githubusercontent.com/mrvarmazyar/DNS-Server-Proxy-Cloudflare/main/screenshot/dns-server-scale.png)


## Security considerations

Hence we're using DNS over TLS with TCP protocol, we should have some considerations with TLS and OpenSSL.
When the client sends request to our DNS server and then proxy server will create TCP connection with the Upstream (In this case CloudFlare), the request maybe attacked by MTIM and in the case of OpenSSL we should use a more secure certificates.

### Microservices Architecture

If we deploy this service on a docker orchestrator like docker swarm or kubernetes we have high availability and scalability and naturally we have security options that applied on the whole microservices environment. we should configure dnsConfig in our service's deployments. Here is an example:

```yaml
apiVersion: v1
kind: Pod
metadata:
  namespace: default
  name: my-pod
spec:
  containers:
    - name: nginx
      image: nginx
  dnsPolicy: "None"
  dnsConfig:
    nameservers:
      - <Our DNS Server's Cluster IP>
```

## Improvements

>  * Store and cache results into the buffer or something like Redis or so for the better performance
>  * We can also add more upstream DNS-over-TLS servers like Google, Quad9, Cleanbrowsing and AdGuard. ([LINK](https://en.wikipedia.org/wiki/Public_recursive_name_server))
>  * Rate limit implementation to throttle requests in a time bucket from specific IP address/s  ([LINK](https://en.wikipedia.org/wiki/Rate_limiting#:~:text=A%20rate%20limiting%20algorithm%20is,code%20429:%20Too%20Many%20Requests.))
