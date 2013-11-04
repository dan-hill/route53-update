from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
import boto
import json
from urllib2 import urlopen
import configparser
import time

# Uncomment the following line for debugging
# boto.set_stream_logger('boto')


def monitor(route53, host_id, host_name, check_interval):
    print 'Monitoring...'
    # Initial check and update
    if external_ip() != zone_ip():
        update(external_ip())
    
    host_ip = external_ip()

    while True:
  
        # Check if external ip has changed
        if host_ip != external_ip():

            # Compare IPs and update if nessisary
            if external_ip() != zone_ip() :
                update(external_ip())
          
        # Sleep until next check
        time.sleep(check_interval)



def update(host_ip):

    # Get the current record set
    records = request_record_set()

    # Set up the record set with new data
    change = boto.route53.record.ResourceRecordSets(route53, host_id, 'IP updated')
    
    # Delete the old record set from Route 53
    change.add_change_record("DELETE", records[0])
    
    # Save the updated record set to Route 53
    change.add_change_record("CREATE", boto.route53.record.Record(name = host_name,
                                                                      type = "A",
                                                                      resource_records = [host_ip],
                                                                      alias_hosted_zone_id = host_id))
    # Commit all record changes
    change.commit()



def external_ip():
    return json.load(urlopen('http://httpbin.org/ip'))['origin']



def zone_ip():
    records = request_record_set()
    
    # Return DNS IP from record set
    return records[0].resource_records[0]



def request_record_set():
    # Request record set from amazon
    records = route53.get_all_rrsets(host_id, 'A', host_name, 1)
    return [record for record in records if record.name.startswith(host_name)]


     
if __name__ == "__main__":

    # Load configuration file
    config = configparser.ConfigParser()
    config.read('.config')

    # Set configuration variables
    secret_key     = config['authentication']['secret_key']
    access_key     = config['authentication']['access_key']
    host_id        = config['zone']['host_id']
    host_name      = config['zone']['host_name']
    check_interval = float( config['monitor']['check_interval'])

    # Connect to Route 53
    route53 = boto.route53.connection.Route53Connection(aws_access_key_id = access_key,
                                                        aws_secret_access_key = secret_key)
    # Start monitoring IPs
    monitor(route53, host_id, host_name, check_interval)




