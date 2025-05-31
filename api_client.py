import logging
from datetime import datetime
from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TradeTrackerAPI')
#As i understood the SOAP process it became super easy to check what props i need to put in authenticate, all the functions related to campaigns and transaction; everything is in this xml file https://ws.tradetracker.com/soap/merchant?wsdl

class TradeTrackerAPI:
    def __init__(self, customer_id, passphrase, sandbox=False, locale='fr_FR'):
        self.wsdl_url = "https://ws.tradetracker.com/soap/merchant?wsdl"
        self.customer_id = customer_id
        self.passphrase = passphrase
        self.sandbox = sandbox
        self.locale = locale
        #go see in my  notes the graph used to understand how to use zeep, it's new to me too 
        settings = Settings(strict=False, xml_huge_tree=True)
        transport = Transport(cache=SqliteCache())
        self.client = Client(self.wsdl_url, settings=settings, transport=transport)
        self.session = None
        
    def authenticate(self):
        #go see my notes to check how to find what proprities we need in authentification (it's in the tradetracker xml file)
        try:
            self.session = self.client.service.authenticate(
                customerID=self.customer_id,
                passphrase=self.passphrase,
                sandbox=self.sandbox,
                locale=self.locale,
                demo=False
            )
            return True
        except Exception as e:
            logger.error(f"Auth failed: {str(e)}")
            return False

    def get_campaigns(self):
        if not self.session:
            if not self.authenticate():
                return []
        
        try:
            raw_campaigns = self.client.service.getCampaigns(_soapheaders={'session': self.session})
            return self._process_campaigns(raw_campaigns)
        except Exception as e:
            logger.error(f"Failed to get campaigns: {str(e)}")
            return []
            
    def _process_campaigns(self, raw_campaigns):
        campaigns = []
        for campaign in raw_campaigns.item:
            campaign_data = {
                'id': campaign.ID,
                'name': campaign.name,
                'url': campaign.URL,
                'start_date': campaign.info.startDate,
                'end_date': campaign.info.stopDate,
                'status': self._get_status(campaign.info)
            }
            campaigns.append(campaign_data)
        return campaigns

    def _get_status(self, campaign_info):
        now = datetime.now().date()
        if campaign_info.stopDate and campaign_info.stopDate < now:
            return 'expired'
        elif campaign_info.startDate > now:
            return 'scheduled'
        else:
            return 'active'

    def get_transactions(self, transaction_type, start_date, end_date, limit=100):
        if not self.session:
            if not self.authenticate():
                return []
        
        try:
            if transaction_type == 'click':
                response = self.client.service.getClickTransactions(
                    _soapheaders={'session': self.session},
                    options={
                        'registrationDateFrom': start_date,
                        'registrationDateTo': end_date,
                        'limit': limit
                    }
                )
            elif transaction_type == 'conversion':
                response = self.client.service.getConversionTransactions(
                    _soapheaders={'session': self.session},
                    options={
                        'registrationDateFrom': start_date,
                        'registrationDateTo': end_date,
                        'limit': limit
                    }
                )
            else:
                return []
                
            return self._process_transactions(response, transaction_type)
        except Exception as e:
            logger.error(f"Failed to get transactions: {str(e)}")
            return []
            
    def _process_transactions(self, raw_transactions, tx_type):
        transactions = []
        for tx in raw_transactions.item:
            tx_data = {
                'id': tx.ID,
                'type': tx_type,
                'date': tx.registrationDate,
                'status': tx.transactionStatus,
                'commission': float(tx.commission),
                'currency': tx.currency
            }
            transactions.append(tx_data)
        return transactions
    #I could also add the clicks number and all sort of other data but my account didn't get activates by trader tracker so i cannot test this shit
    #Fuck You Trader Tracker 