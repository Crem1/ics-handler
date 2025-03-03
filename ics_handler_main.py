import requests
import json
import getpass
import argparse
from prettytable import PrettyTable
from pprint import pprint

#boilerplate based on https://docs.rapid7.com/insightcloudsec/api-documentation/

base_url = "TEMP"
api_key = "TEMP" #Preferably use environment variables or getpass to avoid hardcoded key

headers = {
'Content-Type': 'application/json;charset=UTF-8',
'Accept': 'application/json',
'Api-Key':api_key
}

def get_account_id():
    data = {}
    response = requests.get(
        url = base_url + '/v2/public/clouds/get',
        data = json.dumps(data),
        verify = False,
        headers = headers
    )
    return response.json()

## currently only handles one account at a time
def get_account_findings(account_id, severity):
    #raw account findings
    #data = {}
    #account_findings = requests.get(
    #    url = base_url + '/v4/insights/findings-per-cloud/' + account_id,
    #    data = json.dumps(data),
    #    verify = False,
    #    headers = headers
    #)

    #insights = get_insights()

    insights = get_insights()
    insight_names = [insight['name'] for insight in insights]

    table_out = PrettyTable()
    table_out.field_names = ["Severity", "Insight Name", "Resource", "Description", "Tags"]
    table_out.align = "l"
    table_out.sortby = "Severity"

    with open('findings_response.json', 'r') as account_findings:
        account_findings = json.load(account_findings) #replace with API request later
        account_findings = account_findings['results']

        for account_finding in account_findings:
            for insight in insights:
                if account_finding['insight_name'] in insight['name']:
                    account_finding.update({'Severity': insight['severity']})
                    account_finding.update({'Description': insight['description']})
                    account_finding.update({'Tags': insight['tags']})
  
            if severity is None:
                severity = ["Critical", "High", "Medium", "Low"]

            for sev in severity:
                if sev in account_finding['Severity']:
                    table_out.add_row([
                    account_finding['Severity'], account_finding['insight_name'], 
                    account_finding['resource_name'], 
                    account_finding['Description'],
                    ", ".join(account_finding['Tags'])
                    ])

    print(table_out)
    return account_findings

def get_insights():
    #data = {}
    #response = requests.get(
    #    url = base_url + '/v2/public/insights/get',
    #    data = json.dumps(data),
    #    verify = False,
    #    headers = headers
    #)

    with open('insights.json', 'r') as insights:
        insights = json.load(insights) #replace with API request later

        for insight in insights:
            insight_severity = insight['severity']

            if insight_severity == 1:
                insight['severity'] = '1. 💀Critical💀'
            elif insight_severity == 2:
                insight['severity'] = '2. 🔥High🔥'
            elif insight_severity == 3:
                insight['severity'] = '3. 🎃Medium🎃'
            elif insight_severity == 4:
                insight['severity'] = '4. 👻Low👻'

    return insights


if __name__ == "__main__":
    # Param validation
    if not api_key:
        api_key = getpass.getpass('API Key:')
    else:
        api_key = api_key

    if not base_url:
        base_url = input('Base URL:')
    else:
        base_url = base_url

    banner = r"""
    Welcome to the InsightCloudSec Python API Wrapper
    """
    #Argparse
    parser = argparse.ArgumentParser(description=banner)
    subparsers = parser.add_subparsers(dest='Commands', help='Available commands', required=True)

    # main use case
    parser_get_account_findings = subparsers.add_parser('get-account-findings', help='Get findings for a specific account')
    parser_get_account_findings.add_argument('--account_id', help='Specify account id')
    parser_get_account_findings.add_argument('--severity', nargs='*', help='Specify severity to include')

    # useful for seeing what insights are available; can enable edits via the API later
    parser_get_insights = subparsers.add_parser('get-insights', help='get all Insights')

    args = parser.parse_args()
 
    if args.Commands == 'get-account-findings':
        account_id = args.account_id
        severity = args.severity
        get_account_findings(account_id, severity)
    
    elif args.Commands == 'get-insights':
        print("Getting insights for account ")
        #(get_insights()
    
    else:
        print("No valid arguments provided")
        parser.print_usage()
        exit(1)



