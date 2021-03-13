import socket
import ssl
import sys
import thread
import binascii

# Add Length to query
def DnsQuery(DNS_QUERY):
  pre_length = "\x00"+chr(len(DNS_QUERY))
  _query = pre_length + DNS_QUERY
  return _query

# Send Query to cloudfare (one.one.one.one) server
def SendQuery(tls_connection_socket,DNS_QUERY):
  tcp_query=DnsQuery(DNS_QUERY)
  tls_connection_socket.send(tcp_query)
  result=tls_connection_socket.recv(1024)
  return result


# TLS connection with cloudflare server
def TcpConnection(DNS_ADDR):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(10)
  context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
  context.verify_mode = ssl.CERT_REQUIRED
  context.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
  wrappedSocket = context.wrap_socket(sock, server_hostname=DNS_ADDR)
  wrappedSocket.connect((DNS_ADDR , DNS_TLS_PORT))
  print(wrappedSocket.getpeercert())
  return wrappedSocket

# Handle requests
def RequestHandle(data,address,DNS_ADDR):
  tls_connection_socket=TcpConnection(DNS_ADDR)
  tcp_result = SendQuery(tls_connection_socket, data)
  if tcp_result:
     rcode = tcp_result[:6].encode("hex")
     rcode = str(rcode)[11:]
     if (int(rcode, 16) ==1):
        print ("This is not a DNS query!!!")
     else:
        udp_result = tcp_result[2:]
        s.sendto(udp_result,address)
        print ("200")
  else:
     print ("This is not a DNS query!!!")

if __name__ == '__main__':
   DNS_ADDR = '1.1.1.1'
   DNS_TLS_PORT = 853
   DNS_PORT = 53
   DNS_HOST='0.0.0.0'
   try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.bind((DNS_HOST, DNS_PORT))
      while True:
        data,addr = s.recvfrom(1024)
        thread.start_new_thread(RequestHandle,(data, addr, DNS_ADDR))
   except Exception, e:
      print (e)
      s.close()
