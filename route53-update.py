from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
import boto
import json
from urllib2 import urlopen
import configparser

# Uncomment the following line for debugging
boto.set_stream_logger('boto')

def monitor(route53, host_id, host_name, check_interval):
    while True:
        # Request record set from amazon
        records = route53.get_all_rrsets(host_id, 'A', host_name, 1)
        records = [record for record in records if record.name.startswith(host_name)]
    
        # Get DNS IP from record set
        dns_ip = records[0].resource_records[0]
    
        # Get external IP
        host_ip = json.load(urlopen('http://httpbin.org/ip'))['origin']

        # Compare IPs and update if nessisary
        if dns_ip != host_ip:
            update(host_ip)
        else:
            print "DNS is OK."

    time.sleep(check_interval)

def update(host_ip):
    change = boto.route53.record.ResourceRecordSets(route53, host_id, 'IP updated')
    if record:
        change.add_change_record("DELETE", records[0])
        change.add_change_record("CREATE", boto.route53.record.Record(name = host_name,
                                                                      type = "A",
                                                                      resource_records = [host_ip],
                                                                      alias_hosted_zone_id = host_id))
        change.commit()
    print "IP was updated on DNS"

if __name__ == "__main__":

    # Load configuration file
    config = configparser.ConfigParser()
    config.read('.config')

    # Set configuration variables
    secret_key     = config['authentication']['secret_key']
    access_key     = config['authentication']['access_key']
    host_id        = config['zone']['host_id']
    host_name      = config['zone']['host_name']
    check_interval = config['monitor']['check_interval']

    # Connect to Route 53
    route53 = boto.route53.connection.Route53Connection(aws_access_key_id = access_key,
                                                        aws_secret_access_key = secret_key)
    # Start monitoring IPs
    monitor(route53, host_id, host_name, check_interval)




