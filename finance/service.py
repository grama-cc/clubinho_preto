import requests
from clubinho_preto.settings import ASAAS_KEY, ASAAS_URL
from account.service import AccountService


class FinanceService:
    @staticmethod
    def asaas_resquest(api_endpoint):
        url = f'{ASAAS_URL}{api_endpoint}'
        r = requests.get(url, headers={'access_token': ASAAS_KEY})
        return r.json()

    @staticmethod
    def get_asaas_customer():
        offset = 0
        limit = 100
        customers = FinanceService.asaas_resquest(f'customers?offset={offset}&limit={limit}')
        total_count = customers["totalCount"]
        while offset < total_count:
            for item in customers["data"]:
                print(AccountService.update_asaas_customer_id(item["email"], item["id"]))
            offset += limit
            customers = FinanceService.asaas_resquest(f'customers?offset={offset}&limit={limit}')
        return customers

    @staticmethod
    def get_asaas_subscriptions(customer_id=None):
        offset = 0
        limit = 100
        
        url = f'subscriptions?offset={offset}&limit={limit}'
        if customer_id:
            url += f'&customer={customer_id}'
                
        content = FinanceService.asaas_resquest(url)
        subscriptions = content.get('data')
        has_more = content.get('hasMore')

        while has_more:
            offset += limit
            url = f'subscriptions?offset={offset}&limit={limit}'
            content = FinanceService.asaas_resquest(url)
            subscriptions += content.get('data')
            has_more = content.get('hasMore')

        return subscriptions

