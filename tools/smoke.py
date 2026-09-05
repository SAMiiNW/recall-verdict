import json,re,time
from pathlib import Path
from genlayer_py import create_client,create_account
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionStatus
ROOT=Path(__file__).parents[1];ENV=(ROOT.parents[3]/'accounts.env').read_text()
def secret(n):return re.search(rf'^ACCOUNT_{n}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)',ENV,re.M).group(1).strip()
deploy=json.loads((ROOT/"casebook/deployment.json").read_text());contract=deploy['contract']
account=create_account(account_private_key=secret(1));client=create_client(chain=studionet,account=account)
def send(c,fn,args):
 tx=c.write_contract(address=contract,function_name=fn,args=args);print(fn,tx,flush=True)
 c.wait_for_transaction_receipt(transaction_hash=tx,status=TransactionStatus.ACCEPTED,retries=120,interval=10000);info=c.get_transaction(transaction_hash=tx)
 if info.get('status_name')!='ACCEPTED' or not any(r.get('execution_result')=='SUCCESS' for r in info.get('consensus_data',{}).get('leader_receipt',[])):raise RuntimeError({'function':fn,'tx':tx,'status':info.get('status_name'),'execution':info.get('tx_execution_result_name')})
 return tx
def negative(c,fn,args,label):
 try:c.simulate_write_contract(address=contract,function_name=fn,args=args);raise RuntimeError(label+' unexpectedly passed')
 except RuntimeError:raise
 except Exception:print('negative',label,'rejected',flush=True)
case_id='RV-'+str(int(time.time()))
base=f'https://raw.githubusercontent.com/SAMiiNW/recall-verdict/{deploy["evidenceCommit"]}/casebook/notices/'
sources=[base+'regulator-notice.txt',base+'manufacturer-notice.txt']
opened=send(client,'open_case',[case_id,'Northwind Kettle','NK-442','Morocco',sources])
negative(client,'open_case',[case_id,'Northwind Kettle','NK-442','Morocco',sources],'duplicate id')
finalized=send(client,'adjudicate',[case_id])
state=client.read_contract(address=contract,function_name='get_case',args=[case_id])
verdict=client.read_contract(address=contract,function_name='get_verdict',args=[case_id])
assert state['status']=='FINAL' and len(state['digests'])==2 and verdict['action']=='RECALL'
proof={'caseId':case_id,'transactions':{'open':opened,'adjudicate':finalized},'state':state,'verdict':verdict}
(ROOT/"casebook/network-run.json").parent.mkdir(parents=True,exist_ok=True)
(ROOT/"casebook/network-run.json").write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
