
# This is a script to retrieve Meraki events and write to a local csv file. It is based on the Meraki SDK and export formating uses pandas
# requirements meraki pandas
# pip install meraki pandas
# Defining your API key as a variable in source code is not recommended
# Instead, use an environment variable as shown under the Usage section
# @ https://github.com/meraki/dashboard-api-python/

import meraki,sys,datetime
import pandas as pd
from dateutil import parser


def main():
    # Set API key 
    API_KEY = 'XXXXXXXX'

    # init the meraki dashboard
    dashboard = meraki.DashboardAPI(API_KEY,suppress_logging=True)
    #retrieve the organizations
    organizations = dashboard.organizations.getOrganizations()
    #list the oranizations and have the user select one
    while True:
        for i in range( 0, len(organizations)):
            print( str(i) + ") " + organizations[i]['name'])
        org_response = int(input('Choose your organization: '))
        if org_response not in range( 0, len(organizations)):
                print("invalid choice, please try again")
        if org_response in range( 0, len(organizations)):
            break
    #retrieve the organization id
    organization_id = organizations[org_response]['id']

    #retrieve the networks under the selected organization
    networks = dashboard.organizations.getOrganizationNetworks(organization_id, total_pages='all')
    #enter and find the desired network from the retrieved list
    network_response = input('Enter your network name: ')
    for k in range( 0, len(networks)):
        if network_response == networks[k]['name']:
           network_id = networks[k]['id']
    try:       
        network_info = dashboard.networks.getNetwork(network_id)
    except:
        print('Could not find network, exiting')
        sys.exit(2)
    #list the product types and have the user select one
    while True:
        for l in range( 0, len(network_info["productTypes"])):
            print( str(l) + ") " + network_info["productTypes"][l])
        type_response = int(input('Choose your product type: '))
        if type_response not in range( 0, len(network_info["productTypes"])):
            print("invalid choice, please try again")
        if type_response in range( 0, len(network_info["productTypes"])):
                product_type = network_info["productTypes"][type_response]
                break
    
    #select start/end date/time for the event logs and convert to iso 8601 format
    start_time = parser.parse(input('Choose your start UTC date/time in format YYYY-MM-DD HH:MM:SS: '))
    end_time = parser.parse(input('Choose your end UTC date/time in format YYYY-MM-DD HH:MM:SS: '))
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()
    #retrieve the events
    print('Getting events...')
    response = dashboard.networks.getNetworkEvents(network_id,productType=product_type,total_pages=-1,direction="next",startingAfter=start_time,event_log_end_time=end_time )
    events = response['events']
    
    #check to see if any events were found
    if len(events) == 0:
        print('No events found, exiting')
        sys.exit(2)
    print(str(len(events)) + ' events found')
    #set file name
    reportFileName = 'meraki_events_' + product_type + '_' + str(datetime.datetime.now()).replace(':','.') + '.csv'
    #format the output and write to csv using pandas
    try:
        print(f"Writing file {reportFileName}")
        df = pd.DataFrame.from_dict(events) 
        df.to_csv (reportFileName, index = None)
    except:
        print(f'Unable to write file {reportFileName}' )
    

if __name__ == '__main__':
    main()